import asyncio
import os
import sys
from datetime import datetime

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the notification client
from app.integrations.notification_client import notification_client, NotificationType, ServiceType

async def test_notification_integration():
    """Test the integration between user-management and notification services."""
    print("Testing notification integration...")
    
    # Set the notification service URL
    notification_client.notification_service_url = os.getenv("NOTIFICATION_SERVICE_URL", "localhost:50051")
    print(f"Using notification service URL: {notification_client.notification_service_url}")
    
    # Test sending a notification
    user_id = f"test-user-{datetime.now().timestamp()}"
    title = "Test Notification"
    message = "This is a test notification from user-management service"
    
    print(f"Sending notification to user {user_id}...")
    notification_id = notification_client.send_notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=NotificationType.INFO,
        data={"test": "true", "source": "integration_test"}
    )
    
    if notification_id:
        print(f"Notification sent successfully! ID: {notification_id}")
    else:
        print("Failed to send notification")
        return
    
    # Test getting notifications
    print(f"Getting notifications for user {user_id}...")
    notifications = notification_client.get_user_notifications(
        user_id=user_id,
        include_read=True,
        limit=10,
        offset=0
    )
    
    print(f"Found {notifications['total_count']} notifications, {notifications['unread_count']} unread")
    
    for i, notification in enumerate(notifications['notifications']):
        print(f"\nNotification {i+1}:")
        print(f"  ID: {notification['id']}")
        print(f"  Title: {notification['title']}")
        print(f"  Message: {notification['message']}")
        print(f"  Type: {notification['type']}")
        print(f"  Service: {notification['service']}")
        print(f"  Read: {notification['read']}")
    
    # Test marking a notification as read
    if notifications['notifications']:
        notification_to_mark = notifications['notifications'][0]
        full_notification_id = f"{notification_to_mark['service'].lower()}:{notification_to_mark['id']}"
        
        print(f"\nMarking notification {full_notification_id} as read...")
        success = notification_client.mark_notification_as_read(
            user_id=user_id,
            notification_id=full_notification_id
        )
        
        if success:
            print("Notification marked as read successfully!")
        else:
            print("Failed to mark notification as read")
    
    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(test_notification_integration())