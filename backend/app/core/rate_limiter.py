"""
Rate limiting middleware using Redis
"""
from fastapi import Request, HTTPException
from redis import Redis
from datetime import datetime, timedelta
from typing import Optional

from app.core.config import settings


class RateLimiter:
    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    def check_rate_limit(
        self,
        api_key: str,
        limit: int = 100,
        window_seconds: int = 86400  # 24 hours
    ) -> tuple[bool, dict]:
        """
        Check if request is within rate limit
        
        Returns:
            (is_allowed, info_dict)
        """
        key = f"rate_limit:{api_key}"
        
        # Get current count
        current = self.redis.get(key)
        
        if current is None:
            # First request in window
            self.redis.setex(key, window_seconds, 1)
            return True, {
                "limit": limit,
                "remaining": limit - 1,
                "reset_at": (datetime.utcnow() + timedelta(seconds=window_seconds)).isoformat()
            }
        
        current_count = int(current)
        
        if current_count >= limit:
            # Rate limit exceeded
            ttl = self.redis.ttl(key)
            return False, {
                "limit": limit,
                "remaining": 0,
                "reset_at": (datetime.utcnow() + timedelta(seconds=ttl)).isoformat()
            }
        
        # Increment counter
        self.redis.incr(key)
        ttl = self.redis.ttl(key)
        
        return True, {
            "limit": limit,
            "remaining": limit - current_count - 1,
            "reset_at": (datetime.utcnow() + timedelta(seconds=ttl)).isoformat()
        }


rate_limiter = RateLimiter()


def get_rate_limit_for_plan(plan: str) -> int:
    """Get daily rate limit based on subscription plan"""
    limits = {
        "free": 100,
        "pro": 10000,
        "team": 100000,
        "enterprise": 1000000
    }
    return limits.get(plan, 100)
