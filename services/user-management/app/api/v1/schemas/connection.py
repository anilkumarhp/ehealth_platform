from pydantic import BaseModel, EmailStr, ConfigDict, Field, model_validator
import uuid
from datetime import datetime
from app.db.models.connection import ConnectionStatus
from .user import UserRead

class FamilyConnectionBase(BaseModel):
    relationship_type: str

class FamilyConnectionCreate(FamilyConnectionBase):
    approver_abha_id: str | None = None
    approver_email: EmailStr | None = None
    approver_phone: str | None = None

    @model_validator(mode='before')
    @classmethod
    def check_at_least_one_identifier(cls, values):
        identifiers = [
            values.get('approver_abha_id'), 
            values.get('approver_email'), 
            values.get('approver_phone')
        ]
        if sum(1 for i in identifiers if i) != 1:
            raise ValueError('Please provide exactly one of: approver_abha_id, approver_email, or approver_phone.')
        return values

class ConnectionInitiateRequest(BaseModel):
    member_aadhaar_number: str = Field(..., description="The 12-digit Aadhaar number of the family member to add.")
    relationship_type: str

class ConnectionInitiateResponse(BaseModel):
    verification_transaction_id: str
    message: str = "OTP has been sent to the registered mobile number."

# ... other schemas ...
class ConnectionCompleteRequest(BaseModel):
    verification_transaction_id: str
    otp: str = Field(..., description="The OTP received on the member's phone.")
    # Add the fields that were previously query parameters
    relationship_type: str
    member_aadhaar_number: str

class FamilyConnectionRead(FamilyConnectionBase):
    id: uuid.UUID
    status: ConnectionStatus
    requester: UserRead
    approver: UserRead
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)