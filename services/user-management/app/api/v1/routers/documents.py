import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from typing import List

from app.api.v1 import deps
from app.core.config import settings
from app.db import models
from app.crud import crud_document 
from app.api.v1.schemas import documents as docs_schema

router = APIRouter()

# --- Endpoints ---
@router.post("/documents/generate-upload-url", response_model=docs_schema.GenerateUploadURLResponse)
def generate_upload_url(
    *,
    db: Session = Depends(deps.get_db),
    request: docs_schema.GenerateUploadURLRequest,
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Generate a pre-signed URL for a client to upload a file directly to S3.
    """
    s3_client = boto3.client("s3", region_name=settings.AWS_REGION)
    
    if not current_user.patient_profile or not current_user.patient_profile.s3_data_prefix:
        raise HTTPException(status_code=400, detail="Patient profile is not fully configured for uploads.")

    document_id = uuid.uuid4()
    s3_key = f"{current_user.patient_profile.s3_data_prefix}/{document_id}/{request.file_name}"

    try:
        crud_document.create_document_record(
            db=db, 
            doc_id=document_id,
            patient_id=current_user.id, 
            uploader_id=current_user.id,
            file_name=request.file_name,
            content_type=request.content_type,
            s3_key=s3_key
        )

        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': settings.AWS_S3_BUCKET_NAME, 'Key': s3_key, 'ContentType': request.content_type},
            ExpiresIn=3600 # URL is valid for 1 hour
        )
        return {"upload_url": presigned_url, "document_id": document_id}

    except ClientError as e:
        raise HTTPException(status_code=500, detail="Could not generate upload URL.")

@router.post("/documents/{document_id}/confirm-upload", response_model=docs_schema.MessageResponse)
def confirm_upload(
    document_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Confirm that a file has been successfully uploaded to S3.
    """
    doc = crud_document.get_document_by_id(db, doc_id=document_id)
    if not doc or doc.patient_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found or access denied.")
    
    crud_document.update_document_status(db=db, doc=doc, status=models.DocumentStatus.UPLOAD_COMPLETE)
    return {"message": "Upload confirmed successfully."}

@router.get("/documents", response_model=List[docs_schema.DocumentRead])
def get_my_documents(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Get a list of all documents for the currently logged-in patient.
    """
    return crud_document.get_documents_for_patient(db=db, patient_id=current_user.id)