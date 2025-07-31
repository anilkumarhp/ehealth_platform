# app/schemas/consent.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
import uuid
from datetime import datetime

from app.models.access_request import AccessRequestStatusEnum
from app.models.access_permission import PermissionLevelEnum

# ==================================
# Schemas for AccessRequest
# ==================================

class AccessRequestCreate(BaseModel):
    """Schema for creating a new access request for a report."""
    report_id: uuid.UUID = Field(..., description="The ID of the report being requested.")
    patient_user_id: uuid.UUID = Field(..., description="The ID of the patient whose consent is needed.")
    request_reason: str = Field(..., description="The reason for requesting access.")

class AccessRequest(BaseModel):
    """Schema for reading an access request."""
    id: uuid.UUID
    report_id: uuid.UUID
    requesting_entity_id: uuid.UUID
    patient_user_id: uuid.UUID
    status: AccessRequestStatusEnum
    request_reason: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================================
# Schemas for AccessPermission
# ==================================

class AccessPermission(BaseModel):
    """Schema for reading a granted access permission."""
    id: uuid.UUID
    report_id: uuid.UUID
    grantee_id: uuid.UUID
    granted_by_user_id: uuid.UUID
    permission_level: PermissionLevelEnum
    expiry_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)