from fastapi import APIRouter, HTTPException, Depends
from app.models.notification import Notification
from app.services.notification_service import NotificationService
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
notification_service = NotificationService()

@router.post("/notifications/")
async def create_notification(notification: Notification):
    """Create and publish a notification"""
    try:
        logger.info(f"Creating notification: {notification.id} for user {notification.user_id}")
        await notification_service.publish_notification(notification)
        logger.info(f"Notification {notification.id} published successfully")
        return {"status": "notification sent", "notification_id": notification.id}
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create notification: {str(e)}")

@router.get("/notifications/user/{user_id}")
async def get_user_notifications(user_id: str):
    """Get notifications for a specific user"""
    try:
        logger.info(f"Getting notifications for user {user_id}")
        notifications = await notification_service.get_user_notifications(user_id)
        logger.info(f"Retrieved {len(notifications)} notifications for user {user_id}")
        return notifications
    except Exception as e:
        logger.error(f"Error getting notifications for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get notifications: {str(e)}")

@router.put("/notifications/user/{user_id}/{notification_id}/read")
async def mark_notification_read(user_id: str, notification_id: str):
    """Mark a notification as read"""
    try:
        logger.info(f"Marking notification {notification_id} as read for user {user_id}")
        success = await notification_service.mark_as_read(user_id, notification_id)
        if not success:
            logger.warning(f"Notification {notification_id} not found for user {user_id}")
            raise HTTPException(status_code=404, detail="Notification not found")
        logger.info(f"Notification {notification_id} marked as read successfully")
        return {"status": "notification marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification {notification_id} as read: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to mark notification as read: {str(e)}")