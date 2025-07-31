from pydantic import BaseModel 

class MFAEnableRequest(BaseModel):
    otp: str

class MFAEnableResponse(BaseModel):
    qr_code: str # This will be a base64 encoded image or a provisioning URI
    secret: str # Only return this during setup for recovery purposes
