from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid

from app.core.config import settings
from tests.api.v1.test_rbac import get_admin_auth_headers # We can reuse this helper
from app.db import models

def test_generate_upload_url(client: TestClient, db_session: Session, s3_mock):
    """
    Test generating a pre-signed URL for document upload.
    The s3_mock fixture is automatically used here.
    """
    headers = get_admin_auth_headers(client) # Login as an admin/user
    
    # We need a patient profile with an S3 prefix to exist first
    user = db_session.query(models.User).filter(models.User.email.contains("admin_")).first()
    user.patient_profile.s3_data_prefix = f"patient-data/{user.id}"
    db_session.commit()
    
    request_data = {
        "file_name": "blood-report-2025.pdf",
        "content_type": "application/pdf",
        "document_category": "LAB_REPORT"
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/documents/generate-upload-url", 
        headers=headers, 
        json=request_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "upload_url" in data
    assert "document_id" in data
    assert "mock_signature=true" in data["upload_url"] # Verify our mock was used

def test_confirm_upload(client: TestClient, db_session: Session, s3_mock):
    """
    Test confirming a document upload, which should change its status.
    """
    headers = get_admin_auth_headers(client)
    user = db_session.query(models.User).filter(models.User.email.contains("admin_")).first()
    user.patient_profile.s3_data_prefix = f"patient-data/{user.id}"
    db_session.commit()
    
    # 1. Generate the URL and get a document_id
    gen_response = client.post(
        f"{settings.API_V1_STR}/documents/generate-upload-url", 
        headers=headers, 
        json={"file_name": "report.pdf", "content_type": "application/pdf", "document_category": "LAB_REPORT"}
    )
    document_id = gen_response.json()["document_id"]
    
    # 2. Confirm the upload
    confirm_response = client.post(
        f"{settings.API_V1_STR}/documents/{document_id}/confirm-upload",
        headers=headers
    )
    assert confirm_response.status_code == 200
    assert confirm_response.json()["message"] == "Upload confirmed successfully."
    
    # 3. Verify status in DB
    db_doc = db_session.query(models.MedicalDocument).filter(models.MedicalDocument.id == document_id).first()
    assert db_doc.status == models.DocumentStatus.UPLOAD_COMPLETE