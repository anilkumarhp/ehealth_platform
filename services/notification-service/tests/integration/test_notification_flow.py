import pytest
import asyncio
import json
from datetime import datetime, timedelta
from app.models.notification import Notification, NotificationType, NotificationService
from app.services.notification_service import NotificationService as NotificationServiceClass

# Import Redis async client based on availability
try:
    import aioredis
except ImportError:
    from redis import asyncio as aioredis

# This test requires a running Redis instance
# It can be skipped if Redis is not available
pytestmark = pytest.mark.asyncio

@pytest.fixture
async def redis_client():
    """Create a Redis client for testing."""
    try:
        redis = await aioredis.from_url("redis://localhost:6379/0")
        yield redis
        await redis.close()
    except Exception as e:
        pytest.skip(f"Redis not available: {str(e)}")

@pytest.fixture
async def notification_service(redis_client):
    """Create a notification service with a real Redis connection."""
    service = NotificationServiceClass()
    service.redis_url = "redis://localhost:6379/0"
    service.redis = redis_client
    service.async_redis = redis_client
    yield service

@pytest.fixture
async def clean_redis(redis_client):
    """Clean up Redis before and after tests."""
    # Clean up before test
    await redis_client.flushdb()
    yield
    # Clean up after test
    await redis_client.flushdb()

async def test_notification_flow(notification_service, redis_client, clean_redis):
    """Test the full notification flow: publish, retrieve, mark as read."""
    # Create a notification
    user_id = f"test-user-{datetime.now().timestamp()}"
    notification = Notification(
        id=f"test-id-{datetime.now().timestamp()}",
        service=NotificationService.USER,
        type=NotificationType.INFO,
        title="Integration Test",
        message="This is an integration test",
        user_id=user_id,
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(days=1),
        data={"test_key": "test_value"},
        read=False
    )
    
    # Publish the notification
    await notification_service.publish_notification(notification)
    
    # Get the user's notifications
    notifications = await notification_service.get_user_notifications(user_id)
    
    # Verify the notification was stored
    assert len(notifications) == 1
    assert notifications[0]["id"] == notification.id
    assert notifications[0]["title"] == "Integration Test"
    assert notifications[0]["read"] is False
    
    # Mark the notification as read
    notification_id = f"{notification.service}:{notification.id}"
    success = await notification_service.mark_as_read(user_id, notification_id)
    assert success is True
    
    # Get the notifications again
    notifications = await notification_service.get_user_notifications(user_id)
    
    # Verify the notification was marked as read
    assert len(notifications) == 1
    assert notifications[0]["read"] is True