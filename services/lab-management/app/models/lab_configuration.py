from sqlalchemy import Column, String, Integer, Time, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import time

from app.db.base import BaseModel


class LabConfiguration(BaseModel):
    """Lab configuration including operating hours and capacity."""
    __tablename__ = "lab_configurations"

    lab_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    lab_name = Column(String(255), nullable=False)
    
    # Operating hours
    opening_time = Column(Time, nullable=False, default=time(8, 0))
    closing_time = Column(Time, nullable=False, default=time(18, 0))
    lunch_start = Column(Time, nullable=True, default=time(12, 0))
    lunch_end = Column(Time, nullable=True, default=time(13, 0))
    
    # Capacity and scheduling
    max_concurrent_appointments = Column(Integer, nullable=False, default=5)
    slot_interval_minutes = Column(Integer, nullable=False, default=15)  # Minimum slot interval
    
    # Operating days (JSON array of weekday numbers: 0=Monday, 6=Sunday)
    operating_days = Column(JSON, nullable=False, default=[0, 1, 2, 3, 4])  # Mon-Fri
    
    # Holiday dates (JSON array of date strings)
    holiday_dates = Column(JSON, nullable=False, default=[])
    
    # Special configurations
    allow_same_day_booking = Column(Boolean, default=True)
    advance_booking_days = Column(Integer, default=30)  # How far in advance can book
    
    is_active = Column(Boolean, default=True)