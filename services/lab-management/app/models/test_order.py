# app/models/test_order.py

import enum
from sqlalchemy import Column, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import BaseModel

class TestOrderStatusEnum(enum.Enum):
    PENDING_CONSENT = "Pending Consent"
    AWAITING_APPOINTMENT = "Awaiting Appointment"
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class TestOrder(BaseModel):
    """
    SQLAlchemy model for a test order.
    This is initiated by a doctor for a patient.
    """
    __tablename__ = "test_orders"

    # Foreign key to the patient for whom the test is ordered.
    patient_user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Foreign key to the doctor or entity who created the order.
    requesting_entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Foreign key to the lab/organization this order is associated with.
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Foreign key to the specific service being ordered from the lab's catalog.
    lab_service_id = Column(UUID(as_uuid=True), ForeignKey("lab_services.id"), nullable=False, index=True)

    # The current status of the order in its lifecycle.
    status = Column(Enum(TestOrderStatusEnum), nullable=False, default=TestOrderStatusEnum.PENDING_CONSENT)

    # Optional notes or clinical information from the requesting doctor.
    clinical_notes = Column(Text, nullable=True)

    # --- Relationships ---

    # This links back to the specific service being ordered.
    lab_service = relationship("LabService")
    
    # File attachments for this test order (lazy loading)
    attachments = relationship("FileAttachment", back_populates="test_order", lazy="select")