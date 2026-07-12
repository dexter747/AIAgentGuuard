"""
Rate limiting middleware using slowapi for API protection.
Prevents abuse and ensures fair usage across all users.
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from typing import Callable
import redis

from app.core.config import settings


def get_user_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting.
    Uses API key if available, otherwise IP address.
    """
    # Try to get API key from header
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"apikey:{api_key[:16]}"  # Use first 16 chars
    
    # Try to get user from auth token
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.id}"
    
    # Fall back to IP address
    return get_remote_address(request)


# Initialize limiter
limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=["1000/hour"],  # Global default
    storage_uri=settings.REDIS_URL if settings.REDIS_URL else "memory://",
    strategy="fixed-window",
    headers_enabled=True
)


# Rate limit configurations by plan
RATE_LIMITS = {
    "free": {
        "traces": "100/minute",      # Trace ingestion
        "queries": "1000/hour",      # API queries
        "ai_analysis": "50/hour",    # AI-powered endpoints
        "tests": "20/hour",          # Test generation
    },
    "pro": {
        "traces": "1000/minute",
        "queries": "10000/hour",
        "ai_analysis": "500/hour",
        "tests": "200/hour",
    },
    "enterprise": {
        "traces": "10000/minute",
        "queries": "100000/hour",
        "ai_analysis": "5000/hour",
        "tests": "2000/hour",
    }
}


def get_user_plan(request: Request) -> str:
    """Get user's subscription plan from request state."""
    if hasattr(request.state, "user") and request.state.user:
        user = request.state.user
        if hasattr(user, "subscription_tier"):
            return user.subscription_tier
    return "free"


def get_rate_limit_for_endpoint(request: Request, endpoint_type: str) -> str:
    """
    Get rate limit string for specific endpoint based on user plan.
    
    Args:
        request: FastAPI request object
        endpoint_type: Type of endpoint (traces, queries, ai_analysis, tests)
    
    Returns:
        Rate limit string like "100/minute"
    """
    plan = get_user_plan(request)
    return RATE_LIMITS.get(plan, RATE_LIMITS["free"]).get(endpoint_type, "100/hour")


# Decorator for custom rate limiting per plan
def rate_limit_by_plan(endpoint_type: str):
    """
    Apply rate limit based on user's subscription plan.
    
    Usage:
        @router.post("/traces")
        @rate_limit_by_plan("traces")
        async def create_trace(...):
            ...
    """
    def decorator(func: Callable):
        async def wrapper(request: Request, *args, **kwargs):
            rate_limit = get_rate_limit_for_endpoint(request, endpoint_type)
            
            # Apply the rate limit using slowapi
            try:
                limiter.limit(rate_limit)(func)
            except RateLimitExceeded as e:
                # Custom error message with upgrade prompt
                plan = get_user_plan(request)
                if plan == "free":
                    raise HTTPException(
                        status_code=429,
                        detail={
                            "error": "Rate limit exceeded",
                            "message": f"You've exceeded the {rate_limit} limit for {endpoint_type}",
                            "upgrade_message": "Upgrade to Pro for higher limits",
                            "current_plan": plan,
                            "retry_after": e.retry_after if hasattr(e, 'retry_after') else 60
                        }
                    )
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "message": f"You've exceeded the {rate_limit} limit",
                        "retry_after": e.retry_after if hasattr(e, 'retry_after') else 60
                    }
                )
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


# Common rate limit decorators (shortcuts)
def rate_limit_traces(func: Callable):
    """Rate limit for trace ingestion endpoints."""
    return rate_limit_by_plan("traces")(func)


def rate_limit_queries(func: Callable):
    """Rate limit for query/list endpoints."""
    return rate_limit_by_plan("queries")(func)


def rate_limit_ai(func: Callable):
    """Rate limit for AI-powered analysis endpoints."""
    return rate_limit_by_plan("ai_analysis")(func)


def rate_limit_tests(func: Callable):
    """Rate limit for test generation endpoints."""
    return rate_limit_by_plan("tests")(func)
