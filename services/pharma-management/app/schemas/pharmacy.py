"""
Pydantic schemas for pharmacy operations
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class PharmacyBase(BaseModel):
    """Base pharmacy schema with common fields."""
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    website: Optional[str] = Field(None, max_length=255)
    
    # Address
    address_line1: str = Field(..., max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    postal_code: str = Field(..., max_length=20)
    country: str = Field(default="USA", max_length=100)
    
    # Geolocation
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    
    # Operational
    delivery_radius_km: float = Field(default=10.0, ge=0, le=100)
    home_delivery_available: bool = Field(default=True)
    
    # Business Information
    owner_name: str = Field(..., max_length=255)
    pharmacist_in_charge: str = Field(..., max_length=255)
    tax_id: Optional[str] = Field(None, max_length=50)
    
    @validator('phone')
    def validate_phone(cls, v):
        # Remove non-digits
        digits = ''.join(filter(str.isdigit, v))
        if len(digits) < 10:
            raise ValueError('Phone number must have at least 10 digits')
        return v


class PharmacyCreate(PharmacyBase):
    """Schema for creating a new pharmacy."""
    license_number: str = Field(..., max_length=100)
    registration_number: str = Field(..., max_length=100)
    dea_number: Optional[str] = Field(None, max_length=50)
    state_license_expiry: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    
    # Settings
    operating_hours: Optional[Dict[str, Any]] = None
    certifications: Optional[List[str]] = None
    insurance_accepted: Optional[List[str]] = None
    auto_refill_enabled: bool = Field(default=True)
    generic_substitution_allowed: bool = Field(default=True)


class PharmacyUpdate(BaseModel):
    """Schema for updating pharmacy information."""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    website: Optional[str] = Field(None, max_length=255)
    
    # Address
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    
    # Operational
    delivery_radius_km: Optional[float] = Field(None, ge=0, le=100)
    home_delivery_available: Optional[bool] = None
    
    # Settings
    operating_hours: Optional[Dict[str, Any]] = None
    auto_refill_enabled: Optional[bool] = None
    generic_substitution_allowed: Optional[bool] = None
    
    # Status
    operational_status: Optional[str] = Field(None, pattern=r'^(active|inactive|maintenance)$')


class PharmacyResponse(PharmacyBase):
    """Schema for pharmacy response."""
    id: UUID
    license_number: str
    registration_number: str
    dea_number: Optional[str] = None
    
    # Status
    verification_status: str
    operational_status: str
    is_active: bool
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Settings
    operating_hours: Optional[Dict[str, Any]] = None
    certifications: Optional[List[str]] = None
    insurance_accepted: Optional[List[str]] = None
    auto_refill_enabled: bool
    generic_substitution_allowed: bool
    
    class Config:
        from_attributes = True


class PharmacyList(BaseModel):
    """Simplified schema for pharmacy listings."""
    id: UUID
    name: str
    city: str
    state: str
    phone: str
    delivery_radius_km: float
    home_delivery_available: bool
    verification_status: str
    operational_status: str
    is_active: bool
    
    class Config:
        from_attributes = True


class PharmacyVerification(BaseModel):
    """Schema for pharmacy verification results."""
    pharmacy_id: UUID
    verification_status: str
    license_valid: bool
    dea_valid: bool
    certifications_valid: bool
    verification_date: datetime
    issues: Optional[List[str]] = None
    next_verification_date: Optional[datetime] = None


class NearbyPharmacy(BaseModel):
    """Schema for nearby pharmacy results."""
    id: UUID
    name: str
    address_line1: str
    city: str
    state: str
    phone: str
    distance_km: float
    home_delivery_available: bool
    operational_status: str
    
    class Config:
        from_attributes = True