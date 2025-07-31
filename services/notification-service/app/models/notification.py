from enum import Enum
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class NotificationType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"

class NotificationService(str, Enum):
    USER = "user_management"
    LAB = "lab_management"
    PHARMA = "pharma_management"
    HOSPITAL = "hospital_management"
    CHAT = "in_app_messages"

class Notification(BaseModel):
    id: str
    service: NotificationService
    type: NotificationType
    title: str
    message: str
    user_id: Optional[str] = None
    created_at: datetime = datetime.now()
    expires_at: Optional[datetime] = None
    data: Optional[Dict[Any, Any]] = None
    read: bool = False