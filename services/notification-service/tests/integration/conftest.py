import pytest
import os
import asyncio
import time
from datetime import datetime, timedelta

# Import Redis async client based on availability
try:
    import aioredis
except ImportError:
    from redis import asyncio as aioredis

@pytest.fixture(scope="session")
async def redis_client():
    """Create a Redis client for testing."""
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # Try to connect with retries
    for i in range(5):
        try:
            redis = await aioredis.from_url(redis_url)
            await redis.ping()
            break
        except Exception as e:
            if i == 4:  # Last attempt
                pytest.skip(f"Redis not available after 5 attempts: {str(e)}")
            time.sleep(2)  # Wait before retrying
    
    yield redis
    await redis.close()

@pytest.fixture
async def clean_redis(redis_client):
    """Clean up Redis before and after tests."""
    # Clean up before test
    await redis_client.flushdb()
    yield
    # Clean up after test
    await redis_client.flushdb()