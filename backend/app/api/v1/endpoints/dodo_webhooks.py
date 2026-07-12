"""
DODO Payment Webhooks
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.services.dodo_payments import dodo_client, DODO_WEBHOOK_SECRET
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/dodo")


@router.post("")
async def dodo_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle DODO payment webhook events"""

    body = await request.body()

    # Log incoming webhook for debugging
    logger.info(f"Received Dodo webhook: {len(body)} bytes")

    # Get signature from various possible header names
    signature = (
        request.headers.get("X-DODO-Signature") or
        request.headers.get("X-Dodo-Signature") or
        request.headers.get("x-dodo-signature") or
        request.headers.get("Webhook-Signature") or
        request.headers.get("X-Webhook-Signature") or
        ""
    )

    # Verify webhook signature if secret is configured
    if DODO_WEBHOOK_SECRET:
        if not signature:
            logger.warning("No webhook signature provided")
            raise HTTPException(status_code=401, detail="Missing webhook signature")
        if not dodo_client.verify_webhook_signature(body, signature):
            logger.warning("Invalid webhook signature received")
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
    else:
        logger.warning("DODO_WEBHOOK_SECRET not configured - skipping signature verification")

    try:
        # Parse event
        event = json.loads(body)
        event_type = event.get("type") or event.get("event_type") or event.get("event")
        data = event.get("data", event)  # Some webhooks have data at root level

        logger.info(f"Processing Dodo event: {event_type}")
        logger.info(f"Event data: {json.dumps(data)[:500]}")  # Log first 500 chars

        # Extract user identification from various possible locations
        user_id = (
            data.get("metadata", {}).get("user_id") or
            data.get("customer_metadata", {}).get("user_id") or
            data.get("custom_data", {}).get("user_id") or
            event.get("metadata", {}).get("user_id")
        )

        user_email = (
            data.get("metadata", {}).get("email") or
            data.get("customer_email") or
            data.get("email") or
            event.get("metadata", {}).get("email")
        )

        # Get plan from product ID or plan_id
        product_id = data.get("product_id") or data.get("plan_id") or data.get("price_id")
        plan_id = _get_plan_from_product(product_id) if product_id else "starter_monthly"

        # Handle different event types
        if event_type in ["subscription.created", "subscription.active", "checkout.completed", "payment.succeeded"]:
            # Find user
            user = None
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
            if not user and user_email:
                user = db.query(User).filter(User.email == user_email).first()

            if user:
                # Use user_metadata (the correct column name)
                if not user.user_metadata:
                    user.user_metadata = {}
                user.user_metadata["dodo_subscription_id"] = data.get("id") or data.get("subscription_id")
                user.user_metadata["plan_id"] = plan_id
                user.user_metadata["subscription_status"] = "active"
                user.user_metadata["payment_date"] = data.get("created_at") or data.get("timestamp")
                db.commit()
                logger.info(f"Updated user {user.email} to plan {plan_id}")
            else:
                logger.warning(f"User not found for webhook: user_id={user_id}, email={user_email}")

        elif event_type in ["subscription.updated", "subscription.renewed"]:
            user = None
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
            if not user and user_email:
                user = db.query(User).filter(User.email == user_email).first()

            if user:
                # Use user_metadata (the correct column name)
                if not user.user_metadata:
                    user.user_metadata = {}
                user.user_metadata["plan_id"] = plan_id
                user.user_metadata["subscription_status"] = "active"
                db.commit()
                logger.info(f"Renewed subscription for user {user.email}")

        elif event_type in ["subscription.deleted", "subscription.cancelled", "subscription.expired"]:
            user = None
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
            if not user and user_email:
                user = db.query(User).filter(User.email == user_email).first()

            if user:
                # Use user_metadata (the correct column name)
                if not user.user_metadata:
                    user.user_metadata = {}
                user.user_metadata["plan_id"] = "free_monthly"
                user.user_metadata["dodo_subscription_id"] = None
                user.user_metadata["subscription_status"] = "cancelled"
                db.commit()
                logger.info(f"Cancelled subscription for user {user.email}")

        elif event_type == "payment.failed":
            logger.warning(f"Payment failed for user: {user_id or user_email}")
            # TODO: Send notification email

        return {"status": "success", "event_type": event_type}

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse webhook JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        # Don't fail the webhook - return success to prevent retries
        return {"status": "error", "message": str(e)}


def _get_plan_from_product(product_id: str) -> str:
    """Map Dodo product ID to plan ID"""
    from app.services.dodo_payments import SUBSCRIPTION_PLANS

    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        if plan.get("dodo_product_id") == product_id:
            return plan_id

    # Default to free if product not found (safer than defaulting to paid)
    return "free_monthly"
