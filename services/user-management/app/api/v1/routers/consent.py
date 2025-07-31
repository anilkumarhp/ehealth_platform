from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from typing import List

from app.api.v1 import deps
from app.db import models
from app.crud import crud_consent
from app.api.v1.schemas import consent as consent_schema

router = APIRouter()

@router.post("/consent/grant", response_model=consent_schema.ConsentRead, status_code=status.HTTP_201_CREATED)
def grant_consent(
    *,
    db: Session = Depends(deps.get_db),
    consent_in: consent_schema.ConsentGrant,
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Grant consent to another user (a data fiduciary like a doctor).
    """
    # --- NEW: Add check to prevent self-consent ---
    if consent_in.data_fiduciary_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot grant consent to yourself."
        )

    # The logged-in user is the patient giving consent.
    consent = crud_consent.create_consent(db=db, patient_id=current_user.id, consent_in=consent_in)
    return consent

@router.get("/consent/my-grants", response_model=List[consent_schema.ConsentRead])
def get_my_granted_consents(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Get a list of all consents granted by the currently logged-in user.
    """
    return crud_consent.get_consents_given_by_patient(db=db, patient_id=current_user.id)

@router.put("/consent/{consent_id}/revoke", response_model=consent_schema.ConsentRead)
def revoke_a_consent(
    consent_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Revoke a consent that was previously granted.
    """
    consent = crud_consent.get_consent_by_id(db=db, consent_id=consent_id)
    if not consent:
        raise HTTPException(status_code=404, detail="Consent record not found.")
    if consent.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to revoke this consent.")
    
    return crud_consent.revoke_consent(db=db, consent=consent)
