# app/models/appointment.py (Updated)
import enum
from sqlalchemy import Column, DateTime, ForeignKey, Enum, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import BaseModel

class AppointmentStatusEnum(enum.Enum):
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    NO_SHOW = "No Show"

class Appointment(BaseModel):
    __tablename__ = "appointments"

    patient_user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    lab_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    lab_service_id = Column(UUID(as_uuid=True), ForeignKey("lab_services.id"), nullable=False, index=True)

    # --- NEW FIELD ---
    test_order_id = Column(UUID(as_uuid=True), ForeignKey("test_orders.id"), nullable=True, index=True)
    # --- END NEW FIELD ---

    appointment_time = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(Enum(AppointmentStatusEnum), nullable=False, default=AppointmentStatusEnum.SCHEDULED)

    service = relationship("LabService")
    test_order = relationship("TestOrder")
    
    # File attachments for this appointment
    attachments = relationship("FileAttachment", back_populates="appointment")