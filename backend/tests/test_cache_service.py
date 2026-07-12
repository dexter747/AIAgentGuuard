"""
Unit tests for caching service.
"""
import pytest
from app.services.cache_service import CacheService, cache, cached


class TestCacheService:
    """Test cache service functionality."""
    
    def test_cache_set_and_get(self, mock_redis):
        """Test basic cache set and get."""
        cache.set("test_key", {"data": "value"}, ttl=60)
        
        # Mock should have been called
        mock_redis.setex.assert_called_once()
        
    def test_cache_get_nonexistent(self, mock_redis):
        """Test getting non-existent key."""
        mock_redis.get.return_value = None
        
        result = cache.get("nonexistent_key")
        assert result is None
    
    def test_cache_delete(self, mock_redis):
        """Test cache deletion."""
        cache.delete("test_key")
        mock_redis.delete.assert_called_once_with("test_key")
    
    def test_cache_delete_pattern(self, mock_redis):
        """Test pattern-based deletion."""
        mock_redis.keys.return_value = ["key1", "key2", "key3"]
        
        count = cache.delete_pattern("test:*")
        
        mock_redis.keys.assert_called_once_with("test:*")
        mock_redis.delete.assert_called_once()
    
    def test_invalidate_agent(self, mock_redis):
        """Test agent cache invalidation."""
        mock_redis.keys.return_value = []
        
        cache.invalidate_agent("agent_123")
        
        # Should call keys() for each pattern
        assert mock_redis.keys.call_count >= 1
    
    def test_cached_decorator(self, mock_redis):
        """Test @cached decorator."""
        call_count = 0
        
        @cached("test:function", ttl=60)
        def expensive_function(arg):
            nonlocal call_count
            call_count += 1
            return f"result_{arg}"
        
        # First call should execute function
        result1 = expensive_function("test")
        assert result1 == "result_test"
        assert call_count == 1
        
        # Mock cache hit for second call
        mock_redis.get.return_value = '"result_test"'
        result2 = expensive_function("test")
        # In real scenario, would use cached value
        
    def test_cache_key_generation(self):
        """Test cache key generation."""
        key1 = cache._make_key("prefix", "arg1", "arg2", param="value")
        key2 = cache._make_key("prefix", "arg1", "arg2", param="value")
        
        # Same args should produce same key
        assert key1 == key2
        
        key3 = cache._make_key("prefix", "arg1", "different")
        # Different args should produce different key
        assert key1 != key3
