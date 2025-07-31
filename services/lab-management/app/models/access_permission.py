# app/models/access_permission.py

import enum
from sqlalchemy import Column, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import BaseModel

class PermissionLevelEnum(enum.Enum):
    VIEW = "View"
    VIEW_AND_DOWNLOAD = "View and Download"

class AccessPermission(BaseModel):
    __tablename__ = "access_permissions"
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False, index=True)
    grantee_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    granted_by_user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    permission_level = Column(Enum(PermissionLevelEnum), nullable=False, default=PermissionLevelEnum.VIEW)
    expiry_at = Column(DateTime(timezone=True), nullable=True)
    report = relationship("Report")