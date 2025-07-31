from sqlalchemy import Column, String, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class TestDuration(BaseModel):
    """Test duration configuration for different lab services."""
    __tablename__ = "test_durations"

    lab_service_id = Column(UUID(as_uuid=True), ForeignKey("lab_services.id"), nullable=False, index=True)
    
    # Duration settings
    duration_minutes = Column(Integer, nullable=False)
    setup_time_minutes = Column(Integer, nullable=False, default=5)  # Time before test
    cleanup_time_minutes = Column(Integer, nullable=False, default=5)  # Time after test
    
    # Total time = setup + duration + cleanup
    total_time_minutes = Column(Integer, nullable=False)
    
    # Scheduling preferences
    preferred_time_slots = Column(String(500), nullable=True)  # e.g., "morning,afternoon"
    requires_fasting = Column(Boolean, default=False)
    requires_special_prep = Column(Boolean, default=False)
    
    # Equipment/room requirements
    equipment_required = Column(String(255), nullable=True)
    room_type_required = Column(String(100), nullable=True)
    
    # Notes for scheduling
    scheduling_notes = Column(Text, nullable=True)
    
    # Relationships
    lab_service = relationship("LabService", back_populates="duration_config")