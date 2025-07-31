import redis
import json
import pickle
from typing import Any, Optional, Union
from functools import wraps
import hashlib
from datetime import timedelta

from app.core.config import settings

# Redis client for caching
cache_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=2,  # Use different DB for caching
    decode_responses=False  # Keep binary for pickle
)

class CacheManager:
    """Redis-based cache manager."""
    
    def __init__(self, redis_client=cache_client):
        self.redis = redis_client
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage."""
        if isinstance(value, (str, int, float, bool)):
            return json.dumps(value).encode()
        return pickle.dumps(value)
    
    def _deserialize(self, value: bytes) -> Any:
        """Deserialize value from storage."""
        try:
            return json.loads(value.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return pickle.loads(value)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.redis.get(key)
            if value is None:
                return None
            return self._deserialize(value)
        except Exception:
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set value in cache with optional expiration."""
        try:
            serialized = self._serialize(value)
            if expire:
                if isinstance(expire, timedelta):
                    expire = int(expire.total_seconds())
                return self.redis.setex(key, expire, serialized)
            return self.redis.set(key, serialized)
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return bool(self.redis.delete(key))
        except Exception:
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return bool(self.redis.exists(key))
        except Exception:
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception:
            return 0

# Global cache instance
cache = CacheManager()

def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()

def cached(expire: Union[int, timedelta] = 300, key_prefix: str = ""):
    """
    Caching decorator for functions.
    
    Args:
        expire: Cache expiration time in seconds or timedelta
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            func_name = f"{func.__module__}.{func.__name__}"
            key_suffix = cache_key(*args, **kwargs)
            cache_key_full = f"{key_prefix}:{func_name}:{key_suffix}" if key_prefix else f"{func_name}:{key_suffix}"
            
            # Try to get from cache
            cached_result = await cache.get(cache_key_full)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key_full, result, expire)
            
            return result
        
        return wrapper
    return decorator

# Specific cache functions for common use cases
class LabServiceCache:
    """Cache manager for lab services."""
    
    @staticmethod
    async def get_lab_services(lab_id: str) -> Optional[list]:
        """Get cached lab services for a lab."""
        return await cache.get(f"lab_services:{lab_id}")
    
    @staticmethod
    async def set_lab_services(lab_id: str, services: list, expire: int = 300):
        """Cache lab services for a lab."""
        await cache.set(f"lab_services:{lab_id}", services, expire)
    
    @staticmethod
    async def invalidate_lab_services(lab_id: str):
        """Invalidate lab services cache for a lab."""
        await cache.delete(f"lab_services:{lab_id}")
        await cache.clear_pattern(f"lab_services:{lab_id}:*")

class AppointmentCache:
    """Cache manager for appointments."""
    
    @staticmethod
    async def get_available_slots(lab_id: str, service_id: str, date: str) -> Optional[list]:
        """Get cached available slots."""
        return await cache.get(f"slots:{lab_id}:{service_id}:{date}")
    
    @staticmethod
    async def set_available_slots(
        lab_id: str, 
        service_id: str, 
        date: str, 
        slots: list, 
        expire: int = 60
    ):
        """Cache available slots (short expiration due to dynamic nature)."""
        await cache.set(f"slots:{lab_id}:{service_id}:{date}", slots, expire)
    
    @staticmethod
    async def invalidate_slots(lab_id: str, date: str = None):
        """Invalidate slot cache for a lab and optionally specific date."""
        if date:
            await cache.clear_pattern(f"slots:{lab_id}:*:{date}")
        else:
            await cache.clear_pattern(f"slots:{lab_id}:*")

class ConfigurationCache:
    """Cache manager for lab configurations."""
    
    @staticmethod
    async def get_lab_config(lab_id: str) -> Optional[dict]:
        """Get cached lab configuration."""
        return await cache.get(f"lab_config:{lab_id}")
    
    @staticmethod
    async def set_lab_config(lab_id: str, config: dict, expire: int = 3600):
        """Cache lab configuration (longer expiration as it changes less frequently)."""
        await cache.set(f"lab_config:{lab_id}", config, expire)
    
    @staticmethod
    async def invalidate_lab_config(lab_id: str):
        """Invalidate lab configuration cache."""
        await cache.delete(f"lab_config:{lab_id}")

# Cache warming functions
async def warm_cache():
    """Warm up frequently accessed cache entries."""
    # This would be called on application startup
    # Implementation depends on specific use cases
    pass

# Cache statistics
async def get_cache_stats() -> dict:
    """Get cache statistics."""
    try:
        info = cache_client.info()
        return {
            "used_memory": info.get("used_memory_human", "N/A"),
            "connected_clients": info.get("connected_clients", 0),
            "total_commands_processed": info.get("total_commands_processed", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "hit_rate": (
                info.get("keyspace_hits", 0) / 
                max(1, info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0))
            ) * 100
        }
    except Exception:
        return {"error": "Unable to fetch cache statistics"}