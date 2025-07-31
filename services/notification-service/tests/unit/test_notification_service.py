import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from app.models.notification import Notification, NotificationType, NotificationService as ServiceEnum
from app.services.notification_service import NotificationService

@pytest.fixture
def notification_service():
    """Create a notification service with mocked Redis."""
    with patch('app.services.notification_service.redis.Redis') as mock_redis:
        with patch('app.services.notification_service.aioredis') as mock_aioredis:
            service = NotificationService()
            service.redis = MagicMock()
            service.async_redis = AsyncMock()
            yield service

@pytest.fixture
def sample_notification():
    """Create a sample notification."""
    return Notification(
        id="test-id",
        service=ServiceEnum.USER,
        type=NotificationType.INFO,
        title="Test Title",
        message="Test Message",
        user_id="user-123",
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(days=1),
        data={"key": "value"},
        read=False
    )

@pytest.mark.asyncio
async def test_publish_notification(notification_service, sample_notification):
    """Test publishing a notification."""
    # Setup
    notification_service.redis.publish = MagicMock()
    notification_service.redis.hset = MagicMock()
    notification_service.redis.expireat = MagicMock()
    
    # Execute
    result = await notification_service.publish_notification(sample_notification)
    
    # Assert
    assert result is True
    notification_service.redis.publish.assert_called()
    notification_service.redis.hset.assert_called()
    notification_service.redis.expireat.assert_called()

@pytest.mark.asyncio
async def test_get_user_notifications(notification_service):
    """Test getting user notifications."""
    # Setup
    user_id = "user-123"
    mock_notifications = {
        b"service:notif1": b'{"id":"notif1","service":"user_management","type":"info","title":"Test1","message":"Message1","user_id":"user-123"}',
        b"service:notif2": b'{"id":"notif2","service":"user_management","type":"warning","title":"Test2","message":"Message2","user_id":"user-123"}'
    }
    notification_service.async_redis.hgetall = AsyncMock(return_value=mock_notifications)
    
    # Execute
    result = await notification_service.get_user_notifications(user_id)
    
    # Assert
    assert len(result) == 2
    notification_service.async_redis.hgetall.assert_called_once_with(f"user:{user_id}:notifications")
    assert result[0]["id"] == "notif1"
    assert result[1]["id"] == "notif2"

@pytest.mark.asyncio
async def test_mark_as_read(notification_service):
    """Test marking a notification as read."""
    # Setup
    user_id = "user-123"
    notification_id = "service:notif1"
    mock_notification = b'{"id":"notif1","service":"user_management","type":"info","title":"Test1","message":"Message1","user_id":"user-123","read":false}'
    notification_service.async_redis.hget = AsyncMock(return_value=mock_notification)
    notification_service.async_redis.hset = AsyncMock()
    
    # Execute
    result = await notification_service.mark_as_read(user_id, notification_id)
    
    # Assert
    assert result is True
    notification_service.async_redis.hget.assert_called_once_with(f"user:{user_id}:notifications", notification_id)
    notification_service.async_redis.hset.assert_called_once()
    
    # Verify the notification was marked as read
    call_args = notification_service.async_redis.hset.call_args[0]
    assert call_args[0] == f"user:{user_id}:notifications"
    assert call_args[1] == notification_id
    saved_notification = json.loads(call_args[2])
    assert saved_notification["read"] is True

@pytest.mark.asyncio
async def test_mark_as_read_not_found(notification_service):
    """Test marking a non-existent notification as read."""
    # Setup
    user_id = "user-123"
    notification_id = "service:notif1"
    notification_service.async_redis.hget = AsyncMock(return_value=None)
    
    # Execute
    result = await notification_service.mark_as_read(user_id, notification_id)
    
    # Assert
    assert result is False
    notification_service.async_redis.hget.assert_called_once_with(f"user:{user_id}:notifications", notification_id)
    notification_service.async_redis.hset.assert_not_called()