from pydantic import BaseModel, ConfigDict, EmailStr
import uuid
from typing import Dict, Any

class Address(BaseModel):
    street: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str = "India"
    address_type: str | None = "home"

class ContactInfo(BaseModel):
    primary_email: EmailStr | None = None
    secondary_email: EmailStr | None = None
    phone_number: str | None = None
    website: str | None = None

class OrganizationBase(BaseModel):
    name: str
    type: str | None = None
    registration_number: str | None = None
    abha_facility_id: str | None = None
    license_details: Dict[str, Any] | None = None
    address: Address | None = None
    contact_info: ContactInfo | None = None
    subscription_tier: str | None = "FREE"

class OrganizationCreate(OrganizationBase):
    id: uuid.UUID | None = None

class OrganizationRead(OrganizationBase):
    id: uuid.UUID
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class OrganizationUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    license_details: Dict[str, Any] | None = None
    address: Address | None = None
    contact_info: ContactInfo | None = None