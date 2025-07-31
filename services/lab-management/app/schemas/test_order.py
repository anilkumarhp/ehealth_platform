# app/schemas/test_order.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import uuid

from app.models.test_order import TestOrderStatusEnum

class TestOrderBase(BaseModel):
    """Base schema for a test order."""
    lab_service_id: uuid.UUID = Field(..., description="The ID of the lab service being ordered.")
    clinical_notes: Optional[str] = Field(None, description="Optional clinical notes from the requesting doctor.")

class TestOrderCreate(TestOrderBase):
    """
    Schema for creating a new test order.
    The patient_user_id will be provided separately.
    """
    pass

class TestOrderUpdate(BaseModel):
    """Schema for updating a test order (e.g., changing its status)."""
    status: Optional[TestOrderStatusEnum] = None
    clinical_notes: Optional[str] = None

class TestOrder(TestOrderBase):
    """
    Schema for reading a test order.
    This is the main response model, including all relevant IDs.
    """
    id: uuid.UUID
    patient_user_id: uuid.UUID
    requesting_entity_id: uuid.UUID
    organization_id: uuid.UUID
    status: TestOrderStatusEnum

    model_config = ConfigDict(from_attributes=True)