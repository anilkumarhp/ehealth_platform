import json
from typing import Any, Optional, TypeVar, Callable, Awaitable
import redis.asyncio as redis
from functools import wraps
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Initialize Redis connection
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

T = TypeVar("T")

async def get_cache(key: str) -> Optional[str]:
    """Get value from cache"""
    try:
        return await redis_client.get(key)
    except Exception as e:
        logger.error("cache_get_error", key=key, error=str(e))
        return None

async def set_cache(key: str, value: str, ttl: int = settings.CACHE_TTL) -> bool:
    """Set value in cache with TTL"""
    try:
        await redis_client.set(key, value, ex=ttl)
        return True
    except Exception as e:
        logger.error("cache_set_error", key=key, error=str(e))
        return False

async def delete_cache(key: str) -> bool:
    """Delete value from cache"""
    try:
        await redis_client.delete(key)
        return True
    except Exception as e:
        logger.error("cache_delete_error", key=key, error=str(e))
        return False

def cached(ttl: int = settings.CACHE_TTL, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = await get_cache(cache_key)
            if cached_result:
                try:
                    return json.loads(cached_result)
                except json.JSONDecodeError:
                    # If not JSON, return as is
                    return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            try:
                await set_cache(cache_key, json.dumps(result), ttl)
            except (TypeError, json.JSONDecodeError):
                # If not JSON serializable, store as string
                await set_cache(cache_key, str(result), ttl)
            
            return result
        return wrapper
    return decorator