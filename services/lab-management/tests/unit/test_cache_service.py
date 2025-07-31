import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import timedelta
import json

from app.core.cache import CacheManager, cached, LabServiceCache


@pytest.mark.asyncio
class TestCacheManager:
    """Unit tests for CacheManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_redis = MagicMock()
        self.cache_manager = CacheManager(self.mock_redis)

    async def test_set_string_value(self):
        """Test setting string value in cache."""
        self.mock_redis.set.return_value = True
        
        result = await self.cache_manager.set("test_key", "test_value")
        
        assert result is True
        self.mock_redis.set.assert_called_once()

    async def test_set_with_expiration(self):
        """Test setting value with expiration."""
        self.mock_redis.setex.return_value = True
        
        result = await self.cache_manager.set("test_key", "test_value", expire=300)
        
        assert result is True
        self.mock_redis.setex.assert_called_once_with("test_key", 300, b'"test_value"')

    async def test_set_with_timedelta_expiration(self):
        """Test setting value with timedelta expiration."""
        self.mock_redis.setex.return_value = True
        
        result = await self.cache_manager.set("test_key", "test_value", expire=timedelta(minutes=5))
        
        assert result is True
        self.mock_redis.setex.assert_called_once_with("test_key", 300, b'"test_value"')

    async def test_get_string_value(self):
        """Test getting string value from cache."""
        self.mock_redis.get.return_value = b'"test_value"'
        
        result = await self.cache_manager.get("test_key")
        
        assert result == "test_value"
        self.mock_redis.get.assert_called_once_with("test_key")

    async def test_get_nonexistent_key(self):
        """Test getting non-existent key."""
        self.mock_redis.get.return_value = None
        
        result = await self.cache_manager.get("nonexistent_key")
        
        assert result is None

    async def test_delete_key(self):
        """Test deleting key from cache."""
        self.mock_redis.delete.return_value = 1
        
        result = await self.cache_manager.delete("test_key")
        
        assert result is True
        self.mock_redis.delete.assert_called_once_with("test_key")

    async def test_exists_key(self):
        """Test checking if key exists."""
        self.mock_redis.exists.return_value = 1
        
        result = await self.cache_manager.exists("test_key")
        
        assert result is True
        self.mock_redis.exists.assert_called_once_with("test_key")

    async def test_clear_pattern(self):
        """Test clearing keys by pattern."""
        self.mock_redis.keys.return_value = ["key1", "key2", "key3"]
        self.mock_redis.delete.return_value = 3
        
        result = await self.cache_manager.clear_pattern("test_*")
        
        assert result == 3
        self.mock_redis.keys.assert_called_once_with("test_*")
        self.mock_redis.delete.assert_called_once_with("key1", "key2", "key3")

    async def test_serialize_complex_object(self):
        """Test serializing complex object."""
        test_obj = {"key": "value", "number": 42, "list": [1, 2, 3]}
        
        serialized = self.cache_manager._serialize(test_obj)
        
        import pickle
        assert pickle.loads(serialized) == test_obj

    async def test_deserialize_json(self):
        """Test deserializing JSON."""
        json_data = b'{"key": "value"}'
        
        result = self.cache_manager._deserialize(json_data)
        
        assert result == {"key": "value"}

    async def test_exception_handling(self):
        """Test exception handling in cache operations."""
        self.mock_redis.get.side_effect = Exception("Redis error")
        
        result = await self.cache_manager.get("test_key")
        
        assert result is None


@pytest.mark.asyncio
class TestLabServiceCache:
    """Unit tests for LabServiceCache."""

    @patch('app.core.cache.cache')
    async def test_get_lab_services(self, mock_cache):
        """Test getting lab services from cache."""
        mock_cache.get = AsyncMock(return_value=[{"id": "123", "name": "Test Service"}])
        
        result = await LabServiceCache.get_lab_services("lab_123")
        
        assert result == [{"id": "123", "name": "Test Service"}]
        mock_cache.get.assert_called_once_with("lab_services:lab_123")

    @patch('app.core.cache.cache')
    async def test_set_lab_services(self, mock_cache):
        """Test setting lab services in cache."""
        services = [{"id": "123", "name": "Test Service"}]
        mock_cache.set = AsyncMock(return_value=True)
        
        await LabServiceCache.set_lab_services("lab_123", services, expire=600)
        
        mock_cache.set.assert_called_once_with("lab_services:lab_123", services, 600)

    @patch('app.core.cache.cache')
    async def test_invalidate_lab_services(self, mock_cache):
        """Test invalidating lab services cache."""
        mock_cache.delete = AsyncMock(return_value=True)
        mock_cache.clear_pattern = AsyncMock(return_value=2)
        
        await LabServiceCache.invalidate_lab_services("lab_123")
        
        mock_cache.delete.assert_called_once_with("lab_services:lab_123")
        mock_cache.clear_pattern.assert_called_once_with("lab_services:lab_123:*")


@pytest.mark.asyncio
class TestCachedDecorator:
    """Unit tests for cached decorator."""

    @patch('app.core.cache.cache')
    async def test_cached_decorator_cache_miss(self, mock_cache):
        """Test cached decorator on cache miss."""
        mock_cache.get = AsyncMock(return_value=None)
        mock_cache.set = AsyncMock(return_value=True)

        @cached(expire=300)
        async def test_function(arg1, arg2):
            return f"result_{arg1}_{arg2}"

        result = await test_function("test", "args")

        assert result == "result_test_args"
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()

    @patch('app.core.cache.cache')
    async def test_cached_decorator_cache_hit(self, mock_cache):
        """Test cached decorator on cache hit."""
        mock_cache.get = AsyncMock(return_value="cached_result")

        @cached(expire=300)
        async def test_function(arg1, arg2):
            return f"result_{arg1}_{arg2}"

        result = await test_function("test", "args")

        assert result == "cached_result"
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_not_called()