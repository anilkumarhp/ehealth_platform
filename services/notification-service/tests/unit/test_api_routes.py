import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.models.notification import Notification, NotificationType, NotificationService

client = TestClient(app)

@pytest.fixture
def mock_notification_service():
    with patch('app.api.routes.notification_service') as mock_service:
        yield mock_service

def test_create_notification(mock_notification_service):
    """Test creating a notification."""
    # Setup
    mock_notification_service.publish_notification = AsyncMock(return_value=True)
    
    # Execute
    response = client.post(
        "/api/v1/notifications/",
        json={
            "id": "test-id",
            "service": "user_management",
            "type": "info",
            "title": "Test Title",
            "message": "Test Message",
            "user_id": "user-123"
        }
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "notification sent", "notification_id": "test-id"}
    mock_notification_service.publish_notification.assert_called_once()

def test_get_user_notifications(mock_notification_service):
    """Test getting user notifications."""
    # Setup
    mock_notifications = [
        {"id": "notif1", "service": "user_management", "type": "info", "title": "Test1", "message": "Message1"},
        {"id": "notif2", "service": "user_management", "type": "warning", "title": "Test2", "message": "Message2"}
    ]
    mock_notification_service.get_user_notifications = AsyncMock(return_value=mock_notifications)
    
    # Execute
    response = client.get("/api/v1/notifications/user/user-123")
    
    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 2
    mock_notification_service.get_user_notifications.assert_called_once_with("user-123")

def test_mark_notification_read_success(mock_notification_service):
    """Test marking a notification as read (success case)."""
    # Setup
    mock_notification_service.mark_as_read = AsyncMock(return_value=True)
    
    # Execute
    response = client.put("/api/v1/notifications/user/user-123/notif1/read")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "notification marked as read"}
    mock_notification_service.mark_as_read.assert_called_once_with("user-123", "notif1")

def test_mark_notification_read_not_found(mock_notification_service):
    """Test marking a notification as read (not found case)."""
    # Setup
    mock_notification_service.mark_as_read = AsyncMock(return_value=False)
    
    # Execute
    response = client.put("/api/v1/notifications/user/user-123/notif1/read")
    
    # Assert
    assert response.status_code == 404
    assert "Notification not found" in response.json()["detail"]
    mock_notification_service.mark_as_read.assert_called_once_with("user-123", "notif1")