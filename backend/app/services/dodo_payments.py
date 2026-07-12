"""
DODO Payment Provider Integration
Handles subscription management, payment processing, and webhooks
"""
import os
import hmac
import hashlib
import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

# DODO API Configuration
DODO_API_URL = os.getenv("DODO_API_URL", "https://api.dodopayments.com/v1")
DODO_API_KEY = os.getenv("DODO_API_KEY", "")
DODO_SECRET_KEY = os.getenv("DODO_SECRET_KEY", "")
DODO_WEBHOOK_SECRET = os.getenv("DODO_WEBHOOK_SECRET", "")

# Request timeout in seconds
REQUEST_TIMEOUT = 30


# Subscription Plans Configuration - MUST MATCH FRONTEND PRICING
# Product IDs from DODO dashboard
SUBSCRIPTION_PLANS = {
    "free_monthly": {
        "name": "Free / OSS",
        "billing_cycle": "monthly",
        "amount": 0.0,
        "currency": "usd",
        "dodo_product_id": "",  # No DODO product for free tier
        "checkout_url": "",
        "features": {
            "traces_per_month": 50,
            "max_agents": 3,
            "max_tests": 10,
            "api_calls_per_minute": 10,
            "health_checks_per_agent": 1,
            "trace_retention_days": 7,
            "support": "Community",
            "advanced_analytics": False,
            "multi_agent_analysis": False,
            "custom_integrations": False,
            "coordination_view": False,
            "framework_integrations": False,
            "corrective_suggestions": False
        }
    },
    "starter_monthly": {
        "name": "Starter",
        "billing_cycle": "monthly",
        "amount": 24.0,  # Frontend: $24/mo
        "currency": "usd",
        "dodo_product_id": "pdt_0NXF1MSBiauLdufGGFfbb",
        "checkout_url": "https://checkout.dodopayments.com/buy/pdt_0NXF1MSBiauLdufGGFfbb?quantity=1",
        "features": {
            "traces_per_month": 200,  # Frontend: 200 analyzed traces/month
            "max_agents": 10,
            "max_tests": 100,
            "api_calls_per_minute": 50,
            "health_checks_per_agent": 3,
            "trace_retention_days": 14,  # Frontend: 14-day retention
            "support": "Email",
            "advanced_analytics": True,
            "multi_agent_analysis": False,
            "custom_integrations": False,
            "pii_redaction": False,
            "coordination_view": True,  # Basic coordination view
            "framework_integrations": False,
            "corrective_suggestions": False
        }
    },
    "pro_monthly": {
        "name": "Pro",
        "billing_cycle": "monthly",
        "amount": 99.0,  # Frontend: $99/mo
        "currency": "usd",
        "dodo_product_id": "pdt_0NXF1pQdVaDwF1sbDzJpY",
        "checkout_url": "https://checkout.dodopayments.com/buy/pdt_0NXF1pQdVaDwF1sbDzJpY?quantity=1",
        "features": {
            "traces_per_month": 1000,  # Frontend: 1,000 analyzed traces/month
            "max_agents": 25,
            "max_tests": -1,  # Unlimited test generation
            "api_calls_per_minute": 100,
            "health_checks_per_agent": 5,
            "trace_retention_days": 30,  # Frontend: 30-day retention
            "support": "Email",
            "advanced_analytics": True,
            "multi_agent_analysis": True,
            "custom_integrations": True,
            "pii_redaction": False,
            "coordination_view": True,
            "coordination_analysis": True,  # Full coordination analysis
            "framework_integrations": True,  # Framework integrations
            "corrective_suggestions": True,  # Corrective suggestions
            "health_monitoring": True,
            "webhooks": True
        }
    },
    "team_monthly": {
        "name": "Team",
        "billing_cycle": "monthly",
        "amount": 449.0,  # Frontend: $449/mo
        "currency": "usd",
        "dodo_product_id": "pdt_0NXF241ZJDNhEuCKCWsxi",
        "checkout_url": "https://checkout.dodopayments.com/buy/pdt_0NXF241ZJDNhEuCKCWsxi?quantity=1",
        "features": {
            "traces_per_month": 10000,  # Frontend: 10,000 traces/month
            "max_agents": -1,  # Unlimited
            "max_tests": -1,
            "api_calls_per_minute": 500,
            "health_checks_per_agent": 20,
            "trace_retention_days": 60,  # Frontend: 60-day retention
            "support": "Priority",
            "advanced_analytics": True,
            "multi_agent_analysis": True,
            "custom_integrations": True,
            "pii_redaction": False,
            "coordination_view": True,
            "coordination_analysis": True,
            "advanced_coordination": True,  # Advanced coordination
            "corrective_intelligence": True,  # Full corrective intelligence
            "framework_integrations": True,
            "corrective_suggestions": True,
            "health_monitoring": True,
            "webhooks": True,
            "team_members": 10,  # Up to 10 team members
            "slack_integration": True,
            "pagerduty_integration": True
        }
    },
    "enterprise_monthly": {
        "name": "Enterprise",
        "billing_cycle": "monthly",
        "amount": 999.0,  # Starting at $999/mo (custom pricing on contact)
        "currency": "usd",
        "dodo_product_id": "",  # Contact sales
        "checkout_url": "",
        "features": {
            "traces_per_month": -1,  # Unlimited
            "max_agents": -1,
            "max_tests": -1,
            "api_calls_per_minute": -1,  # Unlimited
            "health_checks_per_agent": -1,
            "trace_retention_days": 365,  # 1-year retention
            "support": "Dedicated",
            "advanced_analytics": True,
            "multi_agent_analysis": True,
            "custom_integrations": True,
            "pii_redaction": True,  # PII auto-redaction
            "coordination_view": True,
            "coordination_analysis": True,
            "advanced_coordination": True,
            "corrective_intelligence": True,
            "full_corrective_ai": True,  # Full corrective AI
            "custom_ai_training": True,  # Custom AI model training
            "framework_integrations": True,
            "corrective_suggestions": True,
            "health_monitoring": True,
            "webhooks": True,
            "team_members": -1,  # Unlimited
            "slack_integration": True,
            "pagerduty_integration": True,
            "sso": True,  # SSO/SAML
            "on_premise": True,  # On-premise option
            "dedicated_support": True,
            "custom_sla": True
        }
    },
    "starter_annual": {
        "name": "Starter",
        "billing_cycle": "annual",
        "amount": 228.0,  # Frontend: $19/mo * 12 = $228/yr (20% savings)
        "currency": "usd",
        "dodo_product_id": "pdt_0NXF2TMX9ykvwQYkFze4N",
        "checkout_url": "https://checkout.dodopayments.com/buy/pdt_0NXF2TMX9ykvwQYkFze4N?quantity=1",
        "savings": 60.0,  # Save $60/year vs monthly
        "features": {
            "traces_per_month": 200,
            "max_agents": 10,
            "max_tests": 100,
            "api_calls_per_minute": 50,
            "health_checks_per_agent": 3,
            "trace_retention_days": 14,
            "support": "Email",
            "advanced_analytics": True,
            "multi_agent_analysis": False,
            "custom_integrations": False,
            "pii_redaction": False,
            "coordination_view": True,
            "framework_integrations": False,
            "corrective_suggestions": False
        }
    },
    "pro_annual": {
        "name": "Pro",
        "billing_cycle": "annual",
        "amount": 948.0,  # Frontend: $79/mo * 12 = $948/yr (20% savings)
        "currency": "usd",
        "dodo_product_id": "pdt_0NXF2hAnZy6kF6g8ZVNv1",
        "checkout_url": "https://checkout.dodopayments.com/buy/pdt_0NXF2hAnZy6kF6g8ZVNv1?quantity=1",
        "savings": 240.0,  # Save $240/year vs monthly
        "features": {
            "traces_per_month": 1000,
            "max_agents": 25,
            "max_tests": -1,
            "api_calls_per_minute": 100,
            "health_checks_per_agent": 5,
            "trace_retention_days": 30,
            "support": "Email",
            "advanced_analytics": True,
            "multi_agent_analysis": True,
            "custom_integrations": True,
            "pii_redaction": False,
            "coordination_view": True,
            "coordination_analysis": True,
            "framework_integrations": True,
            "corrective_suggestions": True,
            "health_monitoring": True,
            "webhooks": True
        }
    },
    "team_annual": {
        "name": "Team",
        "billing_cycle": "annual",
        "amount": 4188.0,  # Frontend: $349/mo * 12 = $4188/yr (22% savings)
        "currency": "usd",
        "dodo_product_id": "pdt_0NXF34FqMkk67P8YYm1nD",
        "checkout_url": "https://checkout.dodopayments.com/buy/pdt_0NXF34FqMkk67P8YYm1nD?quantity=1",
        "savings": 1200.0,  # Save $1200/year vs monthly
        "features": {
            "traces_per_month": 10000,
            "max_agents": -1,
            "max_tests": -1,
            "api_calls_per_minute": 500,
            "health_checks_per_agent": 20,
            "trace_retention_days": 60,
            "support": "Priority",
            "advanced_analytics": True,
            "multi_agent_analysis": True,
            "custom_integrations": True,
            "pii_redaction": False,
            "coordination_view": True,
            "coordination_analysis": True,
            "advanced_coordination": True,
            "corrective_intelligence": True,
            "framework_integrations": True,
            "corrective_suggestions": True,
            "health_monitoring": True,
            "webhooks": True,
            "team_members": 10,
            "slack_integration": True,
            "pagerduty_integration": True
        }
    }
}


def get_plan_features(plan_id: str) -> Dict[str, Any]:
    """Get features for a specific plan"""
    plan = SUBSCRIPTION_PLANS.get(plan_id)
    if not plan:
        return SUBSCRIPTION_PLANS["free_monthly"]["features"].copy()

    features = plan["features"].copy()
    # Add computed fields for backward compatibility
    features["traces_limit"] = features["traces_per_month"]
    features["agents_limit"] = features["max_agents"]
    features["retention_days"] = features["trace_retention_days"]

    return features


def get_checkout_url(plan_id: str, user_email: str, user_id: str, return_url: str = "") -> str:
    """Generate checkout URL with metadata"""
    plan = SUBSCRIPTION_PLANS.get(plan_id)
    if not plan or not plan.get("checkout_url"):
        return ""

    checkout_url = plan["checkout_url"]

    # Add return URL if provided
    if return_url:
        checkout_url += f"&return_url={return_url}"

    # Add customer email for pre-fill
    checkout_url += f"&customer_email={user_email}"

    # Add metadata to track user
    checkout_url += f"&metadata[user_id]={user_id}&metadata[plan_id]={plan_id}"

    return checkout_url


def check_usage_limit(user, resource_type: str, db):
    """Check if user has exceeded usage limits for their plan"""
    # Use user_metadata instead of metadata (which is SQLAlchemy's MetaData)
    user_meta = getattr(user, 'user_metadata', None) or {}
    plan_id = user_meta.get("plan_id", "free_monthly") if isinstance(user_meta, dict) else "free_monthly"
    features = get_plan_features(plan_id)

    if resource_type == "traces":
        limit = features["traces_per_month"]
        if limit == -1:  # Unlimited
            return (True, 0, -1)

        # Count traces this month for user's org
        from app.models.trace import Trace
        from app.models.agent import Agent
        from datetime import datetime
        from sqlalchemy import func

        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        count = db.query(func.count(Trace.id)).join(Trace.agent).filter(
            Agent.org_id == user.org_id,
            Trace.created_at >= current_month_start
        ).scalar() or 0

        return (count < limit, count, limit)

    elif resource_type == "agents":
        limit = features["max_agents"]
        if limit == -1:
            return (True, 0, -1)

        from app.models.agent import Agent
        from sqlalchemy import func
        count = db.query(func.count(Agent.id)).filter(
            Agent.org_id == user.org_id
        ).scalar() or 0

        return (count < limit, count, limit)

    elif resource_type == "tests":
        limit = features.get("max_tests", 10)
        if limit == -1:
            return (True, 0, -1)

        from app.models.test import Test
        from app.models.agent import Agent
        from sqlalchemy import func
        count = db.query(func.count(Test.id)).join(Test.agent).filter(
            Agent.org_id == user.org_id
        ).scalar() or 0

        return (count < limit, count, limit)

    return (True, 0, 0)


def calculate_next_billing_date(current_date: datetime, plan_id: str) -> datetime:
    """Calculate next billing date based on plan cycle"""
    plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS["free_monthly"])
    billing_cycle = plan["billing_cycle"]

    if billing_cycle == "annual":
        # Add 1 year
        return current_date.replace(year=current_date.year + 1)
    else:
        # Add 1 month
        if current_date.month == 12:
            return current_date.replace(year=current_date.year + 1, month=1)
        else:
            return current_date.replace(month=current_date.month + 1)


def is_within_usage_limit(current_usage: int, limit: int) -> bool:
    """Check if usage is within limit (-1 means unlimited)"""
    if limit == -1:
        return True
    return current_usage < limit


class DODOPaymentProvider:
    """DODO Payments integration client"""

    def __init__(self):
        self.api_url = DODO_API_URL
        self.api_key = DODO_API_KEY
        self.secret_key = DODO_SECRET_KEY

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to DODO API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        url = f"{self.api_url}/{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=data, timeout=REQUEST_TIMEOUT)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=REQUEST_TIMEOUT)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=REQUEST_TIMEOUT)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=REQUEST_TIMEOUT)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            raise Exception(f"DODO API timeout after {REQUEST_TIMEOUT}s")
        except requests.RequestException as e:
            raise Exception(f"DODO API error: {str(e)}")

    def create_customer(self, email: str, name: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a customer in DODO"""
        data = {
            "email": email,
            "name": name,
            "metadata": metadata or {}
        }
        return self._make_request("POST", "customers", data)

    def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
        payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a subscription"""
        data = {
            "customer_id": customer_id,
            "plan_id": plan_id,
            "payment_method_id": payment_method_id
        }
        return self._make_request("POST", "subscriptions", data)

    def update_subscription(
        self,
        subscription_id: str,
        plan_id: Optional[str] = None,
        cancel_at_period_end: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update a subscription"""
        data = {}
        if plan_id:
            data["plan_id"] = plan_id
        if cancel_at_period_end is not None:
            data["cancel_at_period_end"] = cancel_at_period_end

        return self._make_request("PUT", f"subscriptions/{subscription_id}", data)

    def cancel_subscription(self, subscription_id: str, immediately: bool = False) -> Dict[str, Any]:
        """Cancel a subscription"""
        data = {"immediately": immediately}
        return self._make_request("DELETE", f"subscriptions/{subscription_id}", data)

    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription details"""
        return self._make_request("GET", f"subscriptions/{subscription_id}")

    def add_payment_method(
        self,
        customer_id: str,
        payment_method_token: str,
        set_default: bool = False
    ) -> Dict[str, Any]:
        """Add a payment method to customer"""
        data = {
            "customer_id": customer_id,
            "payment_method_token": payment_method_token,
            "set_default": set_default
        }
        return self._make_request("POST", "payment-methods", data)

    def remove_payment_method(self, payment_method_id: str) -> Dict[str, Any]:
        """Remove a payment method"""
        return self._make_request("DELETE", f"payment-methods/{payment_method_id}")

    def get_invoices(self, customer_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get customer invoices"""
        return self._make_request("GET", "invoices", {"customer_id": customer_id, "limit": limit})

    def get_payment_methods(self, customer_id: str) -> Dict[str, Any]:
        """Get customer payment methods"""
        return self._make_request("GET", "payment-methods", {"customer_id": customer_id})

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify DODO webhook signature"""
        if not DODO_WEBHOOK_SECRET:
            return False
        expected_signature = hmac.new(
            DODO_WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_signature, signature)


# Singleton instance
dodo_client = DODOPaymentProvider()
