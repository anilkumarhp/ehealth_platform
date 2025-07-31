from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime
from .organization import Address

class PatientInsuranceBase(BaseModel):
    provider_name: str | None = None  # Making provider_name optional for government schemes
    policy_number: str
    scheme_name: str | None = None
    insurance_category: str | None = None
    group_number: str | None = None
    plan_type: str | None = None
    effective_date: str | None = None  # Changed from datetime to str to handle date strings from frontend
    expiration_date: str | None = None  # Changed from datetime to str to handle date strings from frontend
    copay_amount: float | None = None
    deductible_amount: float | None = None
    policy_holder_name: str | None = None
    relationship_to_policy_holder: str | None = None

class PatientInsuranceCreate(PatientInsuranceBase):
    pass

class PatientInsuranceRead(PatientInsuranceBase):
    id: uuid.UUID
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class PatientBase(BaseModel):
    primary_phone: str
    alternate_phone: str | None = None
    address: Address | None = None
    aadhaar_id: str | None = None
    aadhaar_last_4_digits: str | None = None
    blood_group: str | None = None

class PatientCreate(PatientBase):
    insurance_info: list[dict] | None = None

class PatientUpdate(BaseModel):
    alternate_phone: str | None = None
    address: Address | None = None
    blood_group: str | None = None
    s3_data_prefix: str | None = None 

class PatientRead(PatientBase):
    user_id: uuid.UUID
    aadhaar_verified: bool
    aadhaar_verification_date: datetime | None = None
    s3_data_prefix: str | None = None
    insurances: list[PatientInsuranceRead] = []
    model_config = ConfigDict(from_attributes=True)