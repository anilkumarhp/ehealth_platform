from pydantic import BaseModel, EmailStr
from .token import Token

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: str | None = None

class LoginResponse(BaseModel):
    # If MFA is not enabled, we get a normal token
    token: Token | None = None
    # If MFA is enabled, these fields will be populated
    mfa_required: bool = False
    mfa_token: str | None = None

class MFAVerifyRequest(BaseModel):
    mfa_token: str
    otp: str