import redis
import time
import json
from typing import Optional
from fastapi import HTTPException, status, Request
from functools import wraps

from app.core.config import settings

# Redis client for rate limiting
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=1,  # Use different DB for rate limiting
    decode_responses=True
)

class RateLimiter:
    """Rate limiter using Redis sliding window algorithm."""
    
    def __init__(self, redis_client=redis_client):
        self.redis = redis_client
    
    async def is_allowed(
        self, 
        key: str, 
        limit: int, 
        window: int,
        identifier: str = None
    ) -> tuple[bool, dict]:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            key: Rate limit key (e.g., 'api:user:123')
            limit: Number of requests allowed
            window: Time window in seconds
            identifier: Additional identifier for logging
        
        Returns:
            (is_allowed, info_dict)
        """
        now = time.time()
        pipeline = self.redis.pipeline()
        
        # Remove expired entries
        pipeline.zremrangebyscore(key, 0, now - window)
        
        # Count current requests
        pipeline.zcard(key)
        
        # Add current request
        pipeline.zadd(key, {str(now): now})
        
        # Set expiration
        pipeline.expire(key, window)
        
        results = pipeline.execute()
        current_requests = results[1]
        
        is_allowed = current_requests < limit
        
        info = {
            "limit": limit,
            "remaining": max(0, limit - current_requests - 1),
            "reset_time": int(now + window),
            "current_requests": current_requests
        }
        
        if not is_allowed:
            # Remove the request we just added since it's not allowed
            self.redis.zrem(key, str(now))
        
        return is_allowed, info

# Rate limiting decorator
def rate_limit(requests: int, window: int, per: str = "ip"):
    """
    Rate limiting decorator.
    
    Args:
        requests: Number of requests allowed
        window: Time window in seconds
        per: Rate limit per what ('ip', 'user', 'endpoint')
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request object
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # If no request object found, skip rate limiting
                return await func(*args, **kwargs)
            
            # Generate rate limit key
            if per == "ip":
                client_ip = request.client.host
                key = f"rate_limit:ip:{client_ip}:{func.__name__}"
            elif per == "user":
                # Extract user from token (simplified)
                auth_header = request.headers.get("authorization", "")
                user_id = "anonymous"
                if auth_header.startswith("Bearer "):
                    # In real implementation, decode JWT to get user ID
                    user_id = "authenticated_user"
                key = f"rate_limit:user:{user_id}:{func.__name__}"
            else:
                key = f"rate_limit:endpoint:{func.__name__}"
            
            # Check rate limit
            limiter = RateLimiter()
            is_allowed, info = await limiter.is_allowed(key, requests, window)
            
            if not is_allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "limit": info["limit"],
                        "reset_time": info["reset_time"]
                    }
                )
            
            # Add rate limit headers to response
            response = await func(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers["X-RateLimit-Limit"] = str(info["limit"])
                response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
                response.headers["X-RateLimit-Reset"] = str(info["reset_time"])
            
            return response
        
        return wrapper
    return decorator

# Middleware for global rate limiting
class RateLimitMiddleware:
    """Middleware for applying rate limits globally."""
    
    def __init__(self, app, default_limit: int = 100, window: int = 3600):
        self.app = app
        self.default_limit = default_limit
        self.window = window
        self.limiter = RateLimiter()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Get client IP
        client_ip = None
        for header_name, header_value in scope.get("headers", []):
            if header_name == b"x-forwarded-for":
                client_ip = header_value.decode().split(",")[0].strip()
                break
        
        if not client_ip:
            client_ip = scope.get("client", ["unknown"])[0]
        
        # Check rate limit
        key = f"global_rate_limit:ip:{client_ip}"
        is_allowed, info = await self.limiter.is_allowed(
            key, self.default_limit, self.window
        )
        
        if not is_allowed:
            response = {
                "detail": {
                    "error": "Global rate limit exceeded",
                    "limit": info["limit"],
                    "reset_time": info["reset_time"]
                }
            }
            
            await send({
                "type": "http.response.start",
                "status": 429,
                "headers": [
                    [b"content-type", b"application/json"],
                    [b"x-ratelimit-limit", str(info["limit"]).encode()],
                    [b"x-ratelimit-remaining", str(info["remaining"]).encode()],
                    [b"x-ratelimit-reset", str(info["reset_time"]).encode()],
                ]
            })
            
            await send({
                "type": "http.response.body",
                "body": json.dumps(response).encode()
            })
            return
        
        await self.app(scope, receive, send)