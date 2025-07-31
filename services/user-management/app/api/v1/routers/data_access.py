import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
import uuid
from datetime import date, datetime
from typing import List, Any

from app.api.v1 import deps
from app.core.config import settings
from app.db import models
from app.crud import crud_document, crud_consent

router = APIRouter()

# --- Schemas for this router ---

class DocumentRead(BaseModel):
    id: uuid.UUID
    file_name: str
    content_type: str
    document_category: models.DocumentCategory
    status: models.DocumentStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DataAccessResponse(BaseModel):
    access_url: str
    expires_in_seconds: int

# --- Endpoints ---

@router.get("/data-access/documents", response_model=List[DocumentRead])
def browse_documents(
    # ... (function parameters are the same)
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Get a list of the current user's documents with powerful filtering and search.
    This uses the tenant-aware get_db because a user only browses their own data.
    """
    documents = crud_document.get_documents_for_patient(
        db=db,
        patient_id=current_user.id,
        # ... (filter parameters are the same)
    )
    return documents

@router.get("/data-access/documents/{document_id}/view", response_model=DataAccessResponse)
def access_patient_document(
    document_id: uuid.UUID,
    # --- THIS IS THE CRITICAL FIX ---
    # Use the public DB session to find a document that may exist in another tenant's schema.
    db: Session = Depends(deps.get_public_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Allows a user to access a patient's document, performing a cross-tenant consent check.
    """
    # 1. Get document metadata using the public session.
    doc = crud_document.get_document_by_id(db, doc_id=document_id)
    if not doc:
        # This will now only be raised if the document truly doesn't exist at all.
        raise HTTPException(status_code=404, detail="Document not found.")

    # --- Consent Check Logic ---
    has_access = False
    # Case 1: The user is the patient themselves. They always have access.
    if doc.patient_id == current_user.id:
        has_access = True
    else:
        # Case 2: Check if the current user has active consent from the patient.
        active_consent = crud_consent.find_active_consent(
            db=db,
            patient_id=doc.patient_id,
            fiduciary_id=current_user.id,
            data_category=doc.document_category.value
        )
        if active_consent:
            has_access = True
            # Log the data access event for auditing
            crud_consent.log_data_access(
                db=db,
                consent_id=active_consent.id,
                patient_id=doc.patient_id,
                consumer_id=current_user.id,
                data_accessed=[doc.s3_key]
            )

    if not has_access:
        # This is the 403 Forbidden error the test now expects to see.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. No valid consent found from the patient."
        )

    # --- Generate S3 URL (only if access is granted) ---
    s3_client = boto3.client("s3", region_name=settings.AWS_REGION)
    url_expiry = 300 # URL is valid for 5 minutes

    try:
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_S3_BUCKET_NAME, 'Key': doc.s3_key},
            ExpiresIn=url_expiry
        )
        return {"access_url": presigned_url, "expires_in_seconds": url_expiry}
    except ClientError:
        raise HTTPException(status_code=500, detail="Could not generate access URL.")