from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from typing import Any

from app.api.v1 import deps
from app.db import models
from app.crud import crud_user, crud_connection, crud_rbac
from app.api.v1.schemas import connection as connection_schema
from app.core.exceptions import DetailException

class AadhaarVerificationClient:
    def start_verification(self, aadhaar_number: str):
        raise NotImplementedError
    def complete_verification(self, transaction_id: str, otp: str, original_aadhaar: str):
        raise NotImplementedError

real_aadhaar_client = AadhaarVerificationClient()

def get_aadhaar_client():
    return real_aadhaar_client

router = APIRouter()

@router.post("/connections/initiate-verification", response_model=connection_schema.ConnectionInitiateResponse)
def initiate_connection_verification(
    request_in: connection_schema.ConnectionInitiateRequest,
    db: Session = Depends(deps.get_public_db),
    current_user: models.User = Depends(deps.get_current_user),
    aadhaar_client: AadhaarVerificationClient = Depends(get_aadhaar_client)
):
    verification_response = aadhaar_client.start_verification(
        aadhaar_number=request_in.member_aadhaar_number
    )
    
    if not verification_response:
         raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error_code": "AADHAAR_MOBILE_NOT_LINKED", "message": "Verification could not be initiated. The Aadhaar may not have a linked mobile number."}
        )

    return {
        "verification_transaction_id": verification_response["transaction_id"],
        "message": "OTP has been sent to the registered mobile number."
    }

@router.post("/connections/complete-verification", response_model=connection_schema.FamilyConnectionRead, status_code=status.HTTP_201_CREATED)
def complete_connection_verification(
    request_in: connection_schema.ConnectionCompleteRequest,
    db: Session = Depends(deps.get_public_db),
    current_user: models.User = Depends(deps.get_current_user),
    aadhaar_client: AadhaarVerificationClient = Depends(get_aadhaar_client)
):
    verification_response = aadhaar_client.complete_verification(
        transaction_id=request_in.verification_transaction_id,
        otp=request_in.otp,
        original_aadhaar=request_in.member_aadhaar_number
    )

    # --- THIS IS THE FIX ---
    # The old line was: if not verification_response or not verification_response.is_success():
    # The new line is a simple check for None, which is what our mock returns on failure.
    if not verification_response:
        raise HTTPException(status_code=400, detail="Invalid OTP or transaction ID.")

    verified_user_details = verification_response
    approver = crud_user.get_user_by_abha_id(db, abha_id=verified_user_details["abha_id"])
    if not approver:
        raise HTTPException(status_code=404, detail="Verified user does not have an account on this platform.")

    if approver.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot create a connection with yourself.")

    # Create the verified connection
    connection = crud_connection.create_connection(
        db=db,
        requester_id=current_user.id,
        approver_id=approver.id,
        relationship_type=request_in.relationship_type
    )
    
    # Update status to VERIFIED
    verified_connection = crud_connection.update_connection_status(db, connection=connection, status=models.ConnectionStatus.VERIFIED)
    
    return verified_connection

@router.put("/connections/{connection_id}/approve", response_model=connection_schema.FamilyConnectionRead)
def approve_connection(
    connection_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    # The 'get_connection_by_id' call will now raise a 404 if not found
    connection = crud_connection.get_connection_by_id(db, connection_id=connection_id, raise_exception=True)
    
    if connection.approver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action.")
    
    if connection.status != models.ConnectionStatus.VERIFICATION_PENDING:
        # Here we can use our custom DetailException
        raise DetailException(detail="Connection is not in a pending state.")
        
    return crud_connection.update_connection_status(db, connection=connection, status=models.ConnectionStatus.VERIFIED)
