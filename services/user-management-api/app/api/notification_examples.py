import httpx
import uuid
from datetime import datetime, timedelta

async def send_notification(notification_data):
    """Send a notification to the notification service"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://notification-api:8004/api/v1/notifications/",
            json=notification_data
        )
        return response.json()

# Example: User registration notification
async def send_registration_notification(admin_id, user_name, user_id):
    notification = {
        "id": str(uuid.uuid4()),
        "service": "user_management",
        "type": "info",
        "title": "New User Registration",
        "message": f"User {user_name} has registered",
        "user_id": admin_id,
        "created_at": datetime.now().isoformat(),
        "data": {"user_id": user_id}
    }
    return await send_notification(notification)

# Example: Password reset notification
async def send_password_reset_notification(user_id, user_email):
    notification = {
        "id": str(uuid.uuid4()),
        "service": "user_management",
        "type": "warning",
        "title": "Password Reset Requested",
        "message": f"A password reset was requested for your account ({user_email})",
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(days=1)).isoformat()
    }
    return await send_notification(notification)