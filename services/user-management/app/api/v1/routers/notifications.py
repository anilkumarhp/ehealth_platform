from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.services.notification_service import user_notification_service
from app.api.v1.deps import get_current_user
from app.db.models.user import User

router = APIRouter()

@router.get("/")
async def get_notifications(
    current_user: User = Depends(get_current_user),
    include_read: bool = False,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get notifications for the current user.
    """
    result = await user_notification_service.get_user_notifications(
        user_id=str(current_user.id),
        include_read=include_read,
        limit=limit,
        offset=offset
    )
    
    return result

@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Mark a notification as read.
    """
    success = await user_notification_service.mark_notification_as_read(
        user_id=str(current_user.id),
        notification_id=notification_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"status": "success", "message": "Notification marked as read"}