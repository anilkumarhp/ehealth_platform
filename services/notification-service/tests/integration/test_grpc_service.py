import pytest
import grpc
import asyncio
import os
import sys
import time
from datetime import datetime, timedelta
from concurrent import futures
from google.protobuf.timestamp_pb2 import Timestamp

# Add the parent directory to the path so we can import the proto modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the generated gRPC code
from app.protos.notification_pb2 import (
    NotificationRequest, UserNotificationsRequest, MarkAsReadRequest,
    NotificationType, ServiceType
)
from app.protos.notification_pb2_grpc import NotificationServiceStub

# This test requires a running gRPC server
# It can be skipped if the server is not available
pytestmark = pytest.mark.asyncio

@pytest.fixture
def grpc_channel():
    """Create a gRPC channel for testing."""
    try:
        channel = grpc.aio.insecure_channel("localhost:50051")
        yield channel
        channel.close()
    except Exception as e:
        pytest.skip(f"gRPC server not available: {str(e)}")

@pytest.fixture
def grpc_client(grpc_channel):
    """Create a gRPC client for testing."""
    return NotificationServiceStub(grpc_channel)

async def test_send_notification(grpc_client):
    """Test sending a notification via gRPC."""
    # Create a timestamp for now
    now = Timestamp()
    now.GetCurrentTime()
    
    # Create a timestamp for expiration
    expires = Timestamp()
    expires.FromDatetime(datetime.now() + timedelta(days=1))
    
    # Create a notification request
    request = NotificationRequest(
        id=f"grpc-test-{time.time()}",
        service=ServiceType.USER_MANAGEMENT,
        type=NotificationType.INFO,
        title="gRPC Test",
        message="This is a test from gRPC",
        user_id="grpc-test-user",
        created_at=now,
        expires_at=expires,
        data={"source": "grpc_test"}
    )
    
    # Send the notification
    response = await grpc_client.SendNotification(request)
    
    # Verify the response
    assert response.success is True
    assert response.notification_id == request.id

async def test_get_user_notifications(grpc_client):
    """Test getting user notifications via gRPC."""
    # First send a notification to ensure there's something to retrieve
    await test_send_notification(grpc_client)
    
    # Create a request to get notifications
    request = UserNotificationsRequest(
        user_id="grpc-test-user",
        include_read=True,
        limit=10,
        offset=0
    )
    
    # Get the notifications
    response = await grpc_client.GetUserNotifications(request)
    
    # Verify the response
    assert response.total_count > 0
    assert len(response.notifications) > 0
    assert response.notifications[0].user_id == "grpc-test-user"

async def test_mark_notification_as_read(grpc_client):
    """Test marking a notification as read via gRPC."""
    # First get notifications to find one to mark as read
    request = UserNotificationsRequest(
        user_id="grpc-test-user",
        include_read=False,  # Only get unread notifications
        limit=1,
        offset=0
    )
    
    get_response = await grpc_client.GetUserNotifications(request)
    
    # Skip if no unread notifications
    if get_response.total_count == 0:
        pytest.skip("No unread notifications to mark as read")
    
    notification_id = get_response.notifications[0].id
    
    # Create a request to mark as read
    mark_request = MarkAsReadRequest(
        user_id="grpc-test-user",
        notification_id=f"user_management:{notification_id}"
    )
    
    # Mark as read
    mark_response = await grpc_client.MarkNotificationAsRead(mark_request)
    
    # Verify the response
    assert mark_response.success is True