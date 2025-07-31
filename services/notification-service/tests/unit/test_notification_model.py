import pytest
from datetime import datetime, timedelta
from app.models.notification import Notification, NotificationType, NotificationService

def test_notification_model_creation():
    """Test that a notification can be created with all fields."""
    notification = Notification(
        id="test-id",
        service=NotificationService.USER,
        type=NotificationType.INFO,
        title="Test Title",
        message="Test Message",
        user_id="user-123",
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(days=1),
        data={"key": "value"},
        read=False
    )
    
    assert notification.id == "test-id"
    assert notification.service == NotificationService.USER
    assert notification.type == NotificationType.INFO
    assert notification.title == "Test Title"
    assert notification.message == "Test Message"
    assert notification.user_id == "user-123"
    assert notification.data == {"key": "value"}
    assert notification.read is False

def test_notification_model_defaults():
    """Test that a notification uses default values correctly."""
    notification = Notification(
        id="test-id",
        service=NotificationService.USER,
        type=NotificationType.INFO,
        title="Test Title",
        message="Test Message"
    )
    
    assert notification.user_id is None
    assert notification.read is False
    assert notification.data is None
    assert notification.expires_at is None
    assert notification.created_at is not None

def test_notification_model_serialization():
    """Test that a notification can be serialized to JSON."""
    now = datetime.now()
    expires = now + timedelta(days=1)
    
    notification = Notification(
        id="test-id",
        service=NotificationService.USER,
        type=NotificationType.INFO,
        title="Test Title",
        message="Test Message",
        user_id="user-123",
        created_at=now,
        expires_at=expires,
        data={"key": "value"},
        read=False
    )
    
    json_data = notification.json()
    assert isinstance(json_data, str)
    
    # Convert back to dict for easier assertions
    import json
    data_dict = json.loads(json_data)
    
    assert data_dict["id"] == "test-id"
    assert data_dict["service"] == "user_management"
    assert data_dict["type"] == "info"
    assert data_dict["title"] == "Test Title"
    assert data_dict["message"] == "Test Message"
    assert data_dict["user_id"] == "user-123"
    assert data_dict["data"] == {"key": "value"}
    assert data_dict["read"] is False