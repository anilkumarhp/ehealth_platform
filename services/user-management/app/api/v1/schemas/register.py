from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any, Optional, List
from .user import PersonalInfo, Address
from .mfa import MFAEnableResponse

class Insurance(BaseModel):
    category: str | None = None
    type: str | None = None
    provider_name: str | None = None
    policy_number: str | None = None
    group_number: str | None = None
    plan_type: str | None = None
    effective_date: str | None = None
    expiration_date: str | None = None
    copay_amount: str | None = None
    deductible_amount: str | None = None
    policy_holder_name: str | None = None
    relationship_to_policy_holder: str | None = None

class RegisterWithMFARequest(BaseModel):
    # Required fields
    email: EmailStr
    password: str
    phone: str | None = None
    primary_phone: str | None = None  # At least one of phone or primary_phone must be provided
    
    # Personal information
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    date_of_birth: str | None = None
    gender: str | None = None
    blood_group: str | None = None
    emergency_contact: str | None = None
    aadhar_id: str | None = None
    
    # Photo as base64 string
    photo: str | None = None
    
    # Address information
    address: Address | Dict[str, Any] | None = None
    
    # Insurance information
    has_insurance: bool = False
    insurance: List[Insurance | Dict[str, Any]] = []
    
    # MFA settings
    enable_mfa: bool = False
    
    # Organization information
    organization_name: str | None = None
    organization_id: str | None = None
    
    # Legacy fields for backward compatibility
    personal_info: PersonalInfo | Dict[str, Any] | None = None
    profile_data: Dict[str, Any] | None = None
    
    # Model config to allow extra fields
    class Config:
        extra = "allow"
        
    @property
    def get_phone(self) -> str:
        """Return the phone number from either phone or primary_phone field"""
        return self.phone or self.primary_phone or ""

class RegisterResponse(BaseModel):
    user_id: str
    email: EmailStr
    mfa_setup: Optional[MFAEnableResponse] = None
    mfa_enabled: bool = False
    token: Dict[str, str] | None = None  # Will contain access_token and token_type if MFA not enabled