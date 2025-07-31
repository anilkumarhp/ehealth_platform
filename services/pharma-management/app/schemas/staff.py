"""
Staff management schemas
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date


class StaffCreate(BaseModel):
    """Schema for creating staff members."""
    user_id: UUID
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    role: str = Field(..., pattern=r'^(pharmacist|pharmacy_technician|store_manager|cashier|delivery_person|admin)$')
    license_number: Optional[str] = Field(None, max_length=100)
    license_expiry: Optional[date] = None
    certifications: Optional[List[str]] = None
    hire_date: date
    can_validate_prescriptions: bool = False
    can_dispense_controlled_substances: bool = False
    can_manage_inventory: bool = False
    can_process_payments: bool = False
    
    @validator('role')
    def validate_role_permissions(cls, v, values):
        # Pharmacists should have prescription validation rights
        if v == 'pharmacist':
            values['can_validate_prescriptions'] = True
            values['can_dispense_controlled_substances'] = True
        return v


class StaffResponse(BaseModel):
    """Staff member response schema."""
    id: UUID
    pharmacy_id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str
    role: str
    license_number: Optional[str] = None
    license_expiry: Optional[date] = None
    certifications: Optional[List[str]] = None
    hire_date: date
    employment_status: str
    can_validate_prescriptions: bool
    can_dispense_controlled_substances: bool
    can_manage_inventory: bool
    can_process_payments: bool
    is_active: bool
    
    class Config:
        from_attributes = True


class StaffList(BaseModel):
    """Simplified staff list schema."""
    id: UUID
    first_name: str
    last_name: str
    email: str
    role: str
    employment_status: str
    hire_date: date
    is_active: bool
    
    class Config:
        from_attributes = True