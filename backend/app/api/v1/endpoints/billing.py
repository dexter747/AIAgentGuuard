"""
Billing and subscription endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User
from app.core.auth import get_current_user
from app.services.dodo_payments import (
    dodo_client, 
    SUBSCRIPTION_PLANS,
    get_plan_features,
    calculate_next_billing_date
)

router = APIRouter()


# Request Models
class UpgradeRequest(BaseModel):
    plan_id: str
    payment_method_id: Optional[str] = None


class PaymentMethodRequest(BaseModel):
    payment_method_token: str
    set_default: bool = False


# Response Models
class PlanFeatures(BaseModel):
    traces_per_month: int
    max_agents: int
    max_tests: int
    api_calls_per_minute: int
    health_checks_per_agent: int
    trace_retention_days: int
    support: str
    advanced_analytics: bool
    multi_agent_analysis: bool
    custom_integrations: bool
    pii_redaction: bool = False
    sso: bool = False
    dedicated_support: bool = False
    custom_sla: bool = False


class PlanResponse(BaseModel):
    id: str
    name: str
    billing_cycle: str
    amount: float
    currency: str
    features: PlanFeatures
    savings: Optional[float] = None
    checkout_url: Optional[str] = None
    dodo_product_id: Optional[str] = None


class SubscriptionResponse(BaseModel):
    plan: str
    plan_id: str
    status: str
    billing_cycle: str
    amount: float
    currency: str
    next_billing_date: Optional[str] = None
    cancel_at_period_end: bool = False
    customer_id: Optional[str] = None
    subscription_id: Optional[str] = None


class InvoiceResponse(BaseModel):
    id: str
    date: str
    amount: float
    status: str
    pdf_url: Optional[str] = None


class PaymentMethodResponse(BaseModel):
    id: str
    type: str
    last4: str
    brand: str
    exp_month: int
    exp_year: int
    is_default: bool


@router.get("/plans", response_model=List[PlanResponse])
async def get_available_plans(
    current_user: User = Depends(get_current_user)
):
    """Get all available subscription plans with personalized checkout URLs"""
    from app.services.dodo_payments import get_checkout_url
    import os
    
    # Get app URL for return redirect
    app_url = os.getenv("APP_URL", "http://localhost:3000")
    return_url = f"{app_url}/payment/success"
    
    plans = []
    for plan_id, plan_data in SUBSCRIPTION_PLANS.items():
        # Skip free plan from listing (it's the default)
        if plan_id == "free_monthly":
            continue
        
        # Convert features dict to PlanFeatures model
        features_dict = plan_data["features"]
        features_dict.setdefault("pii_redaction", False)
        features_dict.setdefault("sso", False)
        features_dict.setdefault("dedicated_support", False)
        features_dict.setdefault("custom_sla", False)
        
        # Generate personalized checkout URL
        checkout_url = get_checkout_url(
            plan_id=plan_id,
            user_email=current_user.email,
            user_id=str(current_user.id),
            return_url=return_url
        )
        
        plans.append(PlanResponse(
            id=plan_id,
            name=plan_data["name"],
            billing_cycle=plan_data["billing_cycle"],
            amount=plan_data["amount"],
            currency=plan_data["currency"],
            features=PlanFeatures(**features_dict),
            savings=plan_data.get("savings"),
            checkout_url=checkout_url or plan_data.get("checkout_url", ""),
            dodo_product_id=plan_data.get("dodo_product_id", "")
        ))
    
    return plans


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current subscription details"""
    
    # Check if user has subscription info in metadata
    user_meta = current_user.user_metadata or {}
    subscription_id = user_meta.get("dodo_subscription_id")
    customer_id = user_meta.get("dodo_customer_id")
    current_plan = user_meta.get("plan_id", "free_monthly")
    
    if subscription_id and customer_id:
        try:
            # Get subscription from DODO
            subscription = dodo_client.get_subscription(subscription_id)
            
            plan_data = SUBSCRIPTION_PLANS.get(current_plan, SUBSCRIPTION_PLANS["free_monthly"])
            
            return SubscriptionResponse(
                plan=subscription.get("plan_name", plan_data["name"]),
                plan_id=current_plan,
                status=subscription.get("status", "active"),
                billing_cycle=plan_data["billing_cycle"],
                amount=plan_data["amount"],
                currency=plan_data["currency"],
                next_billing_date=subscription.get("current_period_end"),
                cancel_at_period_end=subscription.get("cancel_at_period_end", False),
                customer_id=customer_id,
                subscription_id=subscription_id
            )
        except Exception as e:
            print(f"Error fetching DODO subscription: {e}")
            # Fall back to default
    
    # Return Free plan as default
    plan_data = SUBSCRIPTION_PLANS[current_plan]
    next_billing = None
    if current_plan != "free_monthly":
        next_billing = calculate_next_billing_date(datetime.utcnow(), current_plan).isoformat()

    return SubscriptionResponse(
        plan=plan_data["name"],
        plan_id=current_plan,
        status="active",
        billing_cycle=plan_data["billing_cycle"],
        amount=plan_data["amount"],
        currency=plan_data["currency"],
        next_billing_date=next_billing,
        cancel_at_period_end=False,
        customer_id=customer_id,
        subscription_id=subscription_id
    )


@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_invoices(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get billing invoices"""
    
    user_meta = current_user.user_metadata or {}
    customer_id = user_meta.get("dodo_customer_id")
    
    if not customer_id:
        return []
    
    try:
        invoices_data = dodo_client.get_invoices(customer_id, limit)
        invoices = []
        
        for invoice in invoices_data.get("invoices", []):
            invoices.append(InvoiceResponse(
                id=invoice["id"],
                date=invoice["created_at"],
                amount=invoice["amount"],
                status=invoice["status"],
                pdf_url=invoice.get("pdf_url")
            ))
        
        return invoices
    except Exception as e:
        print(f"Error fetching invoices: {e}")
        return []


@router.get("/payment-methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get saved payment methods"""
    
    user_meta = current_user.user_metadata or {}
    customer_id = user_meta.get("dodo_customer_id")
    
    if not customer_id:
        return []
    
    try:
        methods_data = dodo_client.get_payment_methods(customer_id)
        methods = []
        
        for method in methods_data.get("payment_methods", []):
            methods.append(PaymentMethodResponse(
                id=method["id"],
                type=method["type"],
                last4=method["last4"],
                brand=method.get("brand", "card"),
                exp_month=method["exp_month"],
                exp_year=method["exp_year"],
                is_default=method.get("is_default", False)
            ))
        
        return methods
    except Exception as e:
        print(f"Error fetching payment methods: {e}")
        return []


@router.post("/payment-methods")
async def add_payment_method(
    request: PaymentMethodRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new payment method"""
    
    user_meta = current_user.user_metadata or {}
    customer_id = user_meta.get("dodo_customer_id")
    
    # Create customer if doesn't exist
    if not customer_id:
        try:
            customer = dodo_client.create_customer(
                email=current_user.email,
                name=current_user.full_name or current_user.email,
                metadata={"user_id": str(current_user.id)}
            )
            customer_id = customer["id"]
            
            # Update user metadata
            if not current_user.user_metadata:
                current_user.user_metadata = {}
            current_user.user_metadata["dodo_customer_id"] = customer_id
            db.commit()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create customer: {str(e)}"
            )
    
    try:
        payment_method = dodo_client.add_payment_method(
            customer_id=customer_id,
            payment_method_token=request.payment_method_token,
            set_default=request.set_default
        )
        return {"success": True, "payment_method_id": payment_method["id"]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add payment method: {str(e)}"
        )


@router.delete("/payment-methods/{payment_method_id}")
async def remove_payment_method(
    payment_method_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a payment method"""
    
    try:
        dodo_client.remove_payment_method(payment_method_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove payment method: {str(e)}"
        )


@router.post("/upgrade")
async def upgrade_subscription(
    request: UpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upgrade or change subscription plan - returns checkout URL for paid plans"""
    from app.services.dodo_payments import get_checkout_url
    import os
    
    # Validate plan exists
    if request.plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan_id: {request.plan_id}"
        )
    
    plan_data = SUBSCRIPTION_PLANS[request.plan_id]
    
    # Free plan doesn't need payment - just update metadata
    if request.plan_id == "free_monthly":
        user_meta = current_user.user_metadata or {}
        user_meta["plan_id"] = request.plan_id
        current_user.user_metadata = user_meta
        db.commit()
        return {"success": True, "plan": plan_data["name"]}
    
    # For paid plans, generate checkout URL and return it
    # The actual subscription will be created via webhook after payment
    app_url = os.getenv("APP_URL", "http://localhost:3000")
    return_url = f"{app_url}/payment/success"
    
    checkout_url = get_checkout_url(
        plan_id=request.plan_id,
        user_email=current_user.email,
        user_id=str(current_user.id),
        return_url=return_url
    )
    
    if not checkout_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate checkout URL"
        )
    
    return {
        "success": True,
        "checkout_url": checkout_url,
        "plan": plan_data["name"],
        "amount": plan_data["amount"]
    }


@router.post("/cancel")
async def cancel_subscription(
    immediately: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel subscription"""
    
    user_meta = current_user.user_metadata or {}
    subscription_id = user_meta.get("dodo_subscription_id")
    
    if not subscription_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    try:
        dodo_client.cancel_subscription(subscription_id, immediately)
        
        if immediately:
            # Downgrade to free immediately
            current_user.user_metadata["plan_id"] = "free_monthly"
            current_user.user_metadata["dodo_subscription_id"] = None
        
        db.commit()
        return {"success": True, "cancelled_immediately": immediately}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.get("/usage")
async def get_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current usage statistics"""
    
    # Get current plan
    user_meta = current_user.user_metadata or {}
    plan_id = user_meta.get("plan_id", "free_monthly")
    plan_features = get_plan_features(plan_id)
    
    # Count traces for current billing period
    from datetime import datetime
    from app.models.trace import Trace
    from app.models.agent import Agent
    
    # Calculate billing period start
    billing_start = calculate_next_billing_date(datetime.utcnow(), plan_id)
    
    # Count traces
    traces_used = db.query(Trace).join(Trace.agent).filter(
        Agent.org_id == current_user.org_id,
        Trace.created_at >= billing_start
    ).count()
    
    # Count agents
    agents_count = db.query(Agent).filter(
        Agent.org_id == current_user.org_id
    ).count()
    
    return {
        "traces": traces_used,
        "agents": agents_count,
        "tests_run": 0,  # TODO: Implement test counting
        "api_calls": traces_used,  # Same as traces for now
        "plan_limits": {
            "traces": plan_features["traces_limit"],
            "agents": plan_features["agents_limit"],
            "tests": plan_features.get("tests_limit", 0),
            "api_calls": plan_features["traces_limit"]
        }
    }

@router.post("/create-checkout")
async def create_checkout_session(
    upgrade_request: UpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a checkout session for a plan upgrade"""
    from app.services.dodo_payments import get_checkout_url
    import os
    
    plan_id = upgrade_request.plan_id
    
    # Validate plan exists
    if plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan_id: {plan_id}"
        )
    
    # Get plan details
    plan_data = SUBSCRIPTION_PLANS[plan_id]
    
    # Get app URL for return redirect
    app_url = os.getenv("APP_URL", "https://overseex.com")
    return_url = f"{app_url}/dashboard/billing?checkout=success"
    cancel_url = f"{app_url}/upgrade?checkout=cancelled"
    
    # Generate personalized checkout URL
    checkout_url = get_checkout_url(
        plan_id=plan_id,
        user_email=current_user.email,
        user_id=str(current_user.id),
        return_url=return_url
    )
    
    if not checkout_url:
        # Fallback to plan's default checkout URL
        checkout_url = plan_data.get("checkout_url", "")
    
    if not checkout_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No checkout URL available for plan: {plan_id}"
        )
    
    return {
        "checkout_url": checkout_url,
        "plan_id": plan_id,
        "plan_name": plan_data["name"],
        "amount": plan_data["amount"],
        "currency": plan_data["currency"]
    }