# app/models/access_request.py

import enum
from sqlalchemy import Column, String, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import BaseModel

class AccessRequestStatusEnum(enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    DENIED = "Denied"
    EXPIRED = "Expired"

class AccessRequest(BaseModel):
    __tablename__ = "access_requests"
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False, index=True)
    requesting_entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    patient_user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(Enum(AccessRequestStatusEnum), nullable=False, default=AccessRequestStatusEnum.PENDING)
    request_reason = Column(Text, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    report = relationship("Report")