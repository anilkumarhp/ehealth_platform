from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any
import pyotp
import qrcode
import io
from fastapi.responses import StreamingResponse

from app.api.v1 import deps
from app.db import models
from app.crud import crud_patient
from app.crud import crud_user
from app.api.v1.schemas import user as user_schema
from app.api.v1.schemas import patient as patient_schema
from app.api.v1.schemas import mfa as mfa_schema
from app.core.config import settings

router = APIRouter()


@router.get("/users/me", response_model=user_schema.UserRead)
def read_current_user(
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """
    Get current user's profile.
    """
    return current_user

# --- NEW ENDPOINT ---
@router.put("/users/me/patient-profile", response_model=patient_schema.PatientRead)
def update_current_user_patient_profile(
    *,
    db: Session = Depends(deps.get_db),
    patient_in: patient_schema.PatientUpdate,
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Update the patient profile of the currently logged-in user.
    """
    patient_profile = current_user.patient_profile
    if not patient_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No patient profile found for the current user."
        )
    
    # Get a dictionary of the fields that are actually set in the input
    update_data = patient_in.model_dump(exclude_unset=True)
    
    updated_patient = crud_patient.update_patient(db=db, patient=patient_profile, updates=update_data)
    return updated_patient


@router.post("/users/me/mfa/generate", response_model=mfa_schema.MFAEnableResponse)
def generate_mfa(current_user: models.User = Depends(deps.get_current_user)):
    """
    Generate a new MFA secret and QR code for the current user.
    This is the first step of enabling MFA.
    """
    if current_user.mfa_enabled:
        raise HTTPException(status_code=400, detail="MFA is already enabled for this account.")
    
    # Generate a new secret
    secret = pyotp.random_base32()
    
    # Generate provisioning URI
    provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.email, issuer_name=settings.MFA_ISSUER_NAME
    )
    
    # In a real app, you'd store the secret temporarily in the DB or cache until verified.
    # For simplicity here, we'll return it. The user must verify it in the next step.
    
    # Generate QR code from the URI
    img = qrcode.make(provisioning_uri)
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    # Returning the provisioning URI is often easier for frontends to handle
    # than a raw image.
    
    return {"qr_code": provisioning_uri, "secret": secret}

@router.post("/users/me/mfa/enable")
def enable_mfa(
    *,
    db: Session = Depends(deps.get_db),
    # The frontend must send back the secret from the /generate step
    # along with the first OTP from their authenticator app.
    mfa_secret: str,
    otp: str,
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Verify the OTP and permanently enable MFA for the user's account.
    """
    totp = pyotp.TOTP(mfa_secret)
    if not totp.verify(otp):
        raise HTTPException(status_code=400, detail="Invalid OTP. Please try again.")
    
    # OTP is valid, save the secret and enable MFA
    crud_user.enable_mfa(db=db, user=current_user, secret=mfa_secret)
    
    return {"message": "MFA has been successfully enabled."}