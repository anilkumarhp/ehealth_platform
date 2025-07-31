from pydantic import BaseModel, EmailStr, ConfigDict
import uuid
from typing import Dict, Any, List
from datetime import datetime

# Import the RoleRead schema so we can nest it
from .rbac import RoleRead

class Address(BaseModel):
    street: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str | None = None
    address_type: str = "home"

class PersonalInfo(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: str | None = None  # Changed from datetime to str to handle date strings from frontend
    gender: str | None = None
    display_name: str | None = None
    emergency_contact: str | None = None
    blood_group: str | None = None
    aadhar_id: str | None = None
    address: Address | None = None

class UserBase(BaseModel):
    email: EmailStr
    abha_id: str | None = None
    personal_info: PersonalInfo | None = None
    profile_data: Dict[str, Any] | None = None

class UserCreate(UserBase):
    password: str
    # The role is now handled by assigning a Role object, not a string
    primary_phone: str

class UserUpdateByAdmin(BaseModel):
    is_active: bool | None = None

class UserRead(UserBase):
    id: uuid.UUID
    is_active: bool
    mfa_enabled: bool
    organization_id: uuid.UUID
    last_login: datetime | None = None
    profile_photo_url: str | None = None
    
    # REMOVED: role: str
    # REMOVED: permissions: List[str] | None = []
    
    # ADDED: A list of Role objects, using our RoleRead schema
    roles: List[RoleRead] = []
    
    model_config = ConfigDict(from_attributes=True)

class UserInviteResponse(UserRead):
    """
    Special response for the invite endpoint that includes the invitation token.
    """
    invitation_token: str | None = None