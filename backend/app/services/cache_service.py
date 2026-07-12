"""
Redis caching service for performance optimization.
Caches frequently accessed data with TTL-based expiration.
"""
import json
import redis
from typing import Optional, Any, Callable
from functools import wraps
from datetime import timedelta
import hashlib
import os

from app.core.config import settings


class CacheService:
    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client = None
        if settings.REDIS_URL:
            try:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
                print("✅ Redis cache connected successfully")
            except Exception as e:
                print(f"⚠️  Redis connection failed: {e}. Caching disabled.")
                self.redis_client = None
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and arguments."""
        key_parts = [prefix]
        
        # Add positional args
        for arg in args:
            key_parts.append(str(arg))
        
        # Add sorted kwargs
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        
        # Join and hash if too long
        key = ":".join(key_parts)
        if len(key) > 200:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            key = f"{prefix}:{key_hash}"
        
        return key
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 300  # 5 minutes default
    ) -> bool:
        """Set value in cache with TTL in seconds."""
        if not self.redis_client:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete pattern error: {e}")
            return 0
    
    def invalidate_agent(self, agent_id: str):
        """Invalidate all cache entries for an agent."""
        patterns = [
            f"agent:{agent_id}:*",
            f"traces:agent:{agent_id}:*",
            f"analytics:agent:{agent_id}:*",
            f"health:agent:{agent_id}:*"
        ]
        for pattern in patterns:
            self.delete_pattern(pattern)
    
    def invalidate_organization(self, org_id: str):
        """Invalidate all cache entries for an organization."""
        patterns = [
            f"org:{org_id}:*",
            f"dashboard:org:{org_id}:*",
            f"agents:org:{org_id}:*"
        ]
        for pattern in patterns:
            self.delete_pattern(pattern)


# Global cache instance
cache = CacheService()


def cached(prefix: str, ttl: int = 300):
    """
    Decorator for caching function results.
    
    Usage:
        @cached("user:profile", ttl=600)
        def get_user_profile(user_id: str):
            return db.query(User).filter(User.id == user_id).first()
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache._make_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Convenience functions for common cache patterns

def cache_dashboard_stats(org_id: str, data: dict, ttl: int = 300):
    """Cache dashboard statistics."""
    key = f"dashboard:org:{org_id}:stats"
    cache.set(key, data, ttl)


def get_cached_dashboard_stats(org_id: str) -> Optional[dict]:
    """Get cached dashboard statistics."""
    key = f"dashboard:org:{org_id}:stats"
    return cache.get(key)


def cache_agent_list(org_id: str, agents: list, ttl: int = 600):
    """Cache agent list for organization."""
    key = f"agents:org:{org_id}:list"
    cache.set(key, agents, ttl)


def get_cached_agent_list(org_id: str) -> Optional[list]:
    """Get cached agent list."""
    key = f"agents:org:{org_id}:list"
    return cache.get(key)


def cache_prebuilt_mocks(mocks: list, ttl: int = 3600):
    """Cache pre-built mocks library."""
    key = "mocks:prebuilt:library"
    cache.set(key, mocks, ttl)


def get_cached_prebuilt_mocks() -> Optional[list]:
    """Get cached pre-built mocks."""
    key = "mocks:prebuilt:library"
    return cache.get(key)
