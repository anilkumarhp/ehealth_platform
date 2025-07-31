from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

from app.models.appointment import AppointmentStatusEnum


class AppointmentBase(BaseModel):
    """Base appointment schema."""
    appointment_time: datetime = Field(..., description="Appointment date and time")


class AppointmentCreate(AppointmentBase):
    """Schema for creating appointments."""
    test_order_id: UUID
    patient_user_id: UUID
    lab_service_id: UUID
    lab_id: UUID
    status: AppointmentStatusEnum = AppointmentStatusEnum.SCHEDULED
    
    @field_validator('appointment_time')
    @classmethod
    def validate_appointment_time(cls, v):
        if v <= datetime.utcnow():
            raise ValueError("Appointment must be scheduled for future time")
        return v


class AppointmentUpdate(BaseModel):
    """Schema for updating appointments."""
    appointment_time: Optional[datetime] = None
    status: Optional[AppointmentStatusEnum] = None
    
    @field_validator('appointment_time')
    @classmethod
    def validate_appointment_time(cls, v):
        if v and v <= datetime.utcnow():
            raise ValueError("Appointment must be scheduled for future time")
        return v


class Appointment(AppointmentBase):
    """Full appointment schema for responses."""
    id: UUID
    test_order_id: UUID
    patient_user_id: UUID
    lab_service_id: UUID
    lab_id: UUID
    status: AppointmentStatusEnum
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class AppointmentSummary(BaseModel):
    """Summary appointment info for lists."""
    id: UUID
    appointment_time: datetime
    status: AppointmentStatusEnum
    lab_service_name: Optional[str] = None
    patient_name: Optional[str] = None
    
    model_config = {"from_attributes": True}