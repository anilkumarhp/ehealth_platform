import logging
from datetime import datetime, timedelta
from app.integrations.notification_client import notification_client, NotificationType

logger = logging.getLogger(__name__)

class UserNotificationService:
    def __init__(self):
        self.client = notification_client
    
    async def send_welcome_notification(self, user_id, username):
        """Send a welcome notification to a new user."""
        title = "Welcome to eHealth Platform!"
        message = f"Hello {username}, welcome to the eHealth Platform. We're glad to have you on board!"
        
        notification_id = self.client.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.INFO,
            data={"event": "user_registration"}
        )
        
        return notification_id
    
    async def send_password_reset_notification(self, user_id, username):
        """Send a password reset notification."""
        title = "Password Reset Requested"
        message = f"Hello {username}, we received a request to reset your password. If you didn't make this request, please contact support."
        
        notification_id = self.client.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.WARNING,
            data={"event": "password_reset"}
        )
        
        return notification_id
    
    async def send_account_update_notification(self, user_id, username, update_type):
        """Send a notification about account updates."""
        title = "Account Updated"
        message = f"Hello {username}, your account has been updated. Update type: {update_type}"
        
        notification_id = self.client.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.INFO,
            data={"event": "account_update", "update_type": update_type}
        )
        
        return notification_id
    
    async def send_security_alert(self, user_id, username, alert_type):
        """Send a security alert notification."""
        title = "Security Alert"
        message = f"Hello {username}, we detected a security event on your account: {alert_type}"
        
        notification_id = self.client.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.WARNING,
            data={"event": "security_alert", "alert_type": alert_type}
        )
        
        return notification_id
    
    async def send_role_assignment_notification(self, user_id, username, role_name, organization_name):
        """Send a notification about role assignment."""
        title = "Role Assignment"
        message = f"Hello {username}, you have been assigned the role '{role_name}' in organization '{organization_name}'."
        
        notification_id = self.client.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.INFO,
            data={"event": "role_assignment", "role": role_name, "organization": organization_name}
        )
        
        return notification_id
    
    async def get_user_notifications(self, user_id, include_read=False, limit=10, offset=0):
        """Get notifications for a user."""
        return self.client.get_user_notifications(
            user_id=user_id,
            include_read=include_read,
            limit=limit,
            offset=offset
        )
    
    async def mark_notification_as_read(self, user_id, notification_id):
        """Mark a notification as read."""
        return self.client.mark_notification_as_read(
            user_id=user_id,
            notification_id=notification_id
        )

# Create a singleton instance
user_notification_service = UserNotificationService()