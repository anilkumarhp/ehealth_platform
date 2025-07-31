import grpc
import os
import logging
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

# Import the generated gRPC code
try:
    from app.protos.notification_pb2 import (
        NotificationRequest, UserNotificationsRequest, MarkAsReadRequest,
        NotificationType, ServiceType
    )
    from app.protos.notification_pb2_grpc import NotificationServiceStub
except ImportError:
    logging.error("Failed to import notification proto files. Make sure to generate them first.")
    # Define placeholder classes to avoid errors
    class NotificationType:
        INFO = 0
        SUCCESS = 1
        WARNING = 2
        ERROR = 3
    
    class ServiceType:
        USER_MANAGEMENT = 0

logger = logging.getLogger(__name__)

class NotificationClient:
    def __init__(self):
        self.notification_service_url = os.getenv("NOTIFICATION_SERVICE_URL", "notification:50051")
        self.channel = None
        self.stub = None
        
    def _get_stub(self):
        """Get or create a gRPC stub."""
        if self.stub is None:
            try:
                self.channel = grpc.insecure_channel(self.notification_service_url)
                self.stub = NotificationServiceStub(self.channel)
                logger.info(f"Connected to notification service at {self.notification_service_url}")
            except Exception as e:
                logger.error(f"Failed to connect to notification service: {str(e)}")
                raise
        return self.stub
    
    def close(self):
        """Close the gRPC channel."""
        if self.channel:
            self.channel.close()
            self.channel = None
            self.stub = None
    
    def send_notification(self, user_id, title, message, notification_type=NotificationType.INFO, 
                         data=None, expires_at=None):
        """Send a notification to a user."""
        try:
            stub = self._get_stub()
            
            # Create timestamps
            now = Timestamp()
            now.GetCurrentTime()
            
            expires = None
            if expires_at:
                expires = Timestamp()
                expires.FromDatetime(expires_at)
            
            # Create request
            request = NotificationRequest(
                id=f"user-mgmt-{datetime.now().timestamp()}",
                service=ServiceType.USER_MANAGEMENT,
                type=notification_type,
                title=title,
                message=message,
                user_id=user_id,
                created_at=now,
                data=data or {}
            )
            
            if expires:
                request.expires_at.CopyFrom(expires)
            
            # Send notification
            response = stub.SendNotification(request)
            
            if response.success:
                logger.info(f"Notification sent to user {user_id}: {response.notification_id}")
                return response.notification_id
            else:
                logger.error(f"Failed to send notification: {response.error_message}")
                return None
                
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return None
    
    def get_user_notifications(self, user_id, include_read=False, limit=10, offset=0):
        """Get notifications for a user."""
        try:
            stub = self._get_stub()
            
            request = UserNotificationsRequest(
                user_id=user_id,
                include_read=include_read,
                limit=limit,
                offset=offset
            )
            
            response = stub.GetUserNotifications(request)
            
            logger.info(f"Retrieved {response.total_count} notifications for user {user_id}")
            
            # Convert to Python objects
            notifications = []
            for notif in response.notifications:
                notifications.append({
                    "id": notif.id,
                    "service": ServiceType.Name(notif.service),
                    "type": NotificationType.Name(notif.type),
                    "title": notif.title,
                    "message": notif.message,
                    "created_at": notif.created_at.ToDatetime().isoformat(),
                    "read": notif.read,
                    "data": {k: v for k, v in notif.data.items()}
                })
            
            return {
                "notifications": notifications,
                "total_count": response.total_count,
                "unread_count": response.unread_count
            }
                
        except Exception as e:
            logger.error(f"Error getting notifications: {str(e)}")
            return {"notifications": [], "total_count": 0, "unread_count": 0}
    
    def mark_notification_as_read(self, user_id, notification_id):
        """Mark a notification as read."""
        try:
            stub = self._get_stub()
            
            request = MarkAsReadRequest(
                user_id=user_id,
                notification_id=notification_id
            )
            
            response = stub.MarkNotificationAsRead(request)
            
            if response.success:
                logger.info(f"Notification {notification_id} marked as read for user {user_id}")
                return True
            else:
                logger.error(f"Failed to mark notification as read: {response.error_message}")
                return False
                
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            return False

# Create a singleton instance
notification_client = NotificationClient()