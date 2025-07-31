import grpc
import sys
import os
import time
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

# Add the current directory to the path so we can import the proto modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the generated gRPC code
from app.protos.notification_pb2 import (
    NotificationRequest, UserNotificationsRequest, MarkAsReadRequest,
    NotificationType, ServiceType
)
from app.protos.notification_pb2_grpc import NotificationServiceStub

def run():
    print("Testing gRPC Notification Service")
    
    # Connect to the gRPC server
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = NotificationServiceStub(channel)
        
        # Create a user ID
        user_id = f"grpc-test-user-{int(time.time())}"
        print(f"Using user ID: {user_id}")
        
        # Create a timestamp for now
        now = Timestamp()
        now.GetCurrentTime()
        
        # Create a notification request
        notification_id = f"grpc-test-{int(time.time())}"
        request = NotificationRequest(
            id=notification_id,
            service=ServiceType.USER_MANAGEMENT,
            type=NotificationType.INFO,
            title="gRPC Test Notification",
            message="This is a test notification sent via gRPC",
            user_id=user_id,
            created_at=now
        )
        
        print("\n1. Sending notification...")
        response = stub.SendNotification(request)
        print(f"Response: success={response.success}, notification_id={response.notification_id}")
        
        # Get the user's notifications
        print("\n2. Getting user notifications...")
        get_request = UserNotificationsRequest(
            user_id=user_id,
            include_read=True,
            limit=10,
            offset=0
        )
        
        get_response = stub.GetUserNotifications(get_request)
        print(f"Found {get_response.total_count} notifications, {get_response.unread_count} unread")
        
        for i, notification in enumerate(get_response.notifications):
            print(f"\nNotification {i+1}:")
            print(f"  ID: {notification.id}")
            print(f"  Title: {notification.title}")
            print(f"  Message: {notification.message}")
            print(f"  Type: {NotificationType.Name(notification.type)}")
            print(f"  Service: {ServiceType.Name(notification.service)}")
            print(f"  Read: {notification.read}")
        
        # Mark the notification as read
        print("\n3. Marking notification as read...")
        mark_request = MarkAsReadRequest(
            user_id=user_id,
            notification_id=f"user_management:{notification_id}"
        )
        
        mark_response = stub.MarkNotificationAsRead(mark_request)
        print(f"Response: success={mark_response.success}")
        
        # Get the notifications again
        print("\n4. Getting user notifications again...")
        get_response = stub.GetUserNotifications(get_request)
        print(f"Found {get_response.total_count} notifications, {get_response.unread_count} unread")
        
        for i, notification in enumerate(get_response.notifications):
            print(f"\nNotification {i+1}:")
            print(f"  ID: {notification.id}")
            print(f"  Title: {notification.title}")
            print(f"  Message: {notification.message}")
            print(f"  Type: {NotificationType.Name(notification.type)}")
            print(f"  Service: {ServiceType.Name(notification.service)}")
            print(f"  Read: {notification.read}")

if __name__ == '__main__':
    run()