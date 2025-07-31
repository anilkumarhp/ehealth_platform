import enum
from sqlalchemy import Column, String, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import BaseModel


class ReportStatusEnum(enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    REVIEWED = "Reviewed"
    DELIVERED = "Delivered"


class Report(BaseModel):
    __tablename__ = "reports"

    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=False, index=True)
    status = Column(Enum(ReportStatusEnum), nullable=False, default=ReportStatusEnum.PENDING)
    findings = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    reviewed_by_user_id = Column(UUID(as_uuid=True), nullable=True)
    report_file_url = Column(String(500), nullable=True)

    # Relationships
    # appointment = relationship("Appointment", back_populates="report")