# Webhook delivery background tasks
from app.core.celery_app import celery_app
from datetime import datetime
import httpx
import hmac
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


@celery_app.task
def process_webhook_queue():
    """Process pending webhooks from the queue"""
    from app.core.database import SessionLocal
    
    logger.info("Processing webhook queue")
    # In a full implementation, this would pull from a webhook_events table
    # For now, it's a placeholder for the beat schedule


@celery_app.task(bind=True, max_retries=5, default_retry_delay=60)
def deliver_webhook(self, webhook_id: int, event_type: str, payload: dict):
    """Deliver a webhook to the configured URL"""
    from app.core.database import SessionLocal
    from app.models.webhook import Webhook
    
    db = SessionLocal()
    try:
        webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
        if not webhook:
            logger.error(f"Webhook {webhook_id} not found")
            return {"status": "error", "message": "Webhook not found"}
        
        if not webhook.is_active:
            logger.info(f"Webhook {webhook_id} is inactive, skipping")
            return {"status": "skipped", "message": "Webhook inactive"}
        
        # Check if this event type is subscribed
        if webhook.events and event_type not in webhook.events:
            logger.info(f"Webhook {webhook_id} not subscribed to {event_type}")
            return {"status": "skipped", "message": "Event not subscribed"}
        
        # Prepare payload
        webhook_payload = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": payload
        }
        payload_json = json.dumps(webhook_payload)
        
        # Generate signature
        signature = generate_webhook_signature(payload_json, webhook.secret)
        
        # Deliver webhook
        headers = {
            "Content-Type": "application/json",
            "X-AgentGuard-Signature": signature,
            "X-AgentGuard-Event": event_type,
            "X-AgentGuard-Timestamp": str(int(datetime.utcnow().timestamp())),
            "User-Agent": "AgentGuard-Webhook/1.0"
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    webhook.url,
                    content=payload_json,
                    headers=headers
                )
                
                if response.status_code >= 200 and response.status_code < 300:
                    logger.info(f"Webhook {webhook_id} delivered successfully to {webhook.url}")
                    return {
                        "status": "delivered",
                        "status_code": response.status_code,
                        "webhook_id": webhook_id
                    }
                else:
                    logger.warning(f"Webhook {webhook_id} returned {response.status_code}")
                    raise Exception(f"Webhook returned {response.status_code}")
                    
        except httpx.TimeoutException:
            logger.error(f"Webhook {webhook_id} timed out")
            raise
        except httpx.ConnectError:
            logger.error(f"Webhook {webhook_id} connection failed")
            raise
            
    except Exception as e:
        logger.error(f"Webhook delivery failed: {str(e)}")
        # Retry with exponential backoff
        retry_delay = 60 * (2 ** self.request.retries)  # 60, 120, 240, 480, 960 seconds
        self.retry(exc=e, countdown=retry_delay)
    finally:
        db.close()


def generate_webhook_signature(payload: str, secret: str) -> str:
    """Generate HMAC SHA-256 signature for webhook payload"""
    return hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


@celery_app.task
def trigger_webhook_event(org_id: int, event_type: str, payload: dict):
    """Trigger webhooks for a specific event"""
    from app.core.database import SessionLocal
    from app.models.webhook import Webhook
    
    db = SessionLocal()
    try:
        # Get all active webhooks for this organization
        webhooks = db.query(Webhook).filter(
            Webhook.org_id == org_id,
            Webhook.is_active == True
        ).all()
        
        for webhook in webhooks:
            # Check if webhook is subscribed to this event
            if webhook.events and event_type not in webhook.events:
                continue
            
            # Queue webhook delivery
            deliver_webhook.delay(
                webhook_id=webhook.id,
                event_type=event_type,
                payload=payload
            )
        
        logger.info(f"Triggered {len(webhooks)} webhooks for event {event_type}")
    finally:
        db.close()


# Event type constants
class WebhookEvents:
    AGENT_CREATED = "agent.created"
    AGENT_UPDATED = "agent.updated"
    AGENT_DELETED = "agent.deleted"
    AGENT_HEALTH_CHANGED = "agent.health_changed"
    
    TRACE_CREATED = "trace.created"
    TRACE_FAILED = "trace.failed"
    
    TEST_COMPLETED = "test.completed"
    TEST_FAILED = "test.failed"
    
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_UPDATED = "subscription.updated"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    
    PAYMENT_SUCCEEDED = "payment.succeeded"
    PAYMENT_FAILED = "payment.failed"
