"""
Rate limiting service using Redis
"""
from datetime import datetime, timedelta
from typing import Optional
import redis
from app.core.config import settings

# Redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)


class RateLimiter:
    """Rate limiter using Redis for distributed rate limiting"""
    
    @staticmethod
    def check_rate_limit(
        api_key_id: str,
        limit_per_minute: int = 60,
        limit_per_hour: int = 1000,
        limit_per_day: int = 10000
    ) -> tuple[bool, dict]:
        """
        Check if request is within rate limits
        Returns: (is_allowed, details)
        """
        now = datetime.utcnow()
        
        # Define time windows
        minute_key = f"rate:{api_key_id}:minute:{now.strftime('%Y%m%d%H%M')}"
        hour_key = f"rate:{api_key_id}:hour:{now.strftime('%Y%m%d%H')}"
        day_key = f"rate:{api_key_id}:day:{now.strftime('%Y%m%d')}"
        
        # Get current counts
        minute_count = int(redis_client.get(minute_key) or 0)
        hour_count = int(redis_client.get(hour_key) or 0)
        day_count = int(redis_client.get(day_key) or 0)
        
        # Check limits
        if minute_count >= limit_per_minute:
            return False, {
                "error": "Rate limit exceeded",
                "limit_type": "per_minute",
                "limit": limit_per_minute,
                "current": minute_count,
                "reset_at": (now + timedelta(minutes=1)).isoformat()
            }
        
        if hour_count >= limit_per_hour:
            return False, {
                "error": "Rate limit exceeded",
                "limit_type": "per_hour",
                "limit": limit_per_hour,
                "current": hour_count,
                "reset_at": (now + timedelta(hours=1)).isoformat()
            }
        
        if day_count >= limit_per_day:
            return False, {
                "error": "Rate limit exceeded",
                "limit_type": "per_day",
                "limit": limit_per_day,
                "current": day_count,
                "reset_at": (now + timedelta(days=1)).isoformat()
            }
        
        # Increment counts
        pipe = redis_client.pipeline()
        
        # Minute window
        pipe.incr(minute_key)
        pipe.expire(minute_key, 60)
        
        # Hour window
        pipe.incr(hour_key)
        pipe.expire(hour_key, 3600)
        
        # Day window
        pipe.incr(day_key)
        pipe.expire(day_key, 86400)
        
        pipe.execute()
        
        return True, {
            "allowed": True,
            "limits": {
                "per_minute": {"limit": limit_per_minute, "remaining": limit_per_minute - minute_count - 1},
                "per_hour": {"limit": limit_per_hour, "remaining": limit_per_hour - hour_count - 1},
                "per_day": {"limit": limit_per_day, "remaining": limit_per_day - day_count - 1}
            }
        }
    
    @staticmethod
    def reset_rate_limit(api_key_id: str):
        """Reset rate limits for an API key"""
        now = datetime.utcnow()
        patterns = [
            f"rate:{api_key_id}:minute:*",
            f"rate:{api_key_id}:hour:*",
            f"rate:{api_key_id}:day:*"
        ]
        for pattern in patterns:
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
