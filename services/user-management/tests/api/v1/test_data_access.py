from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any

from app.core.config import settings
from app.db import models

# ... (imports) ...
from app.db.models import User, Role # Add Role import
from app.api.v1.schemas.rbac import RoleCreate # Add rbac schema import

def create_and_login_user(client: TestClient, db: Session, user_type_prefix: str) -> Tuple[User, Dict[str, str]]:
    """
    Simplified helper. Creates a user (who becomes an Org Admin) and logs them in.
    Returns the user DB object and their auth headers.
    """
    email = f"{user_type_prefix}_{uuid.uuid4()}@test.com"
    password = "testpassword"
    
    # Register the user. This flow makes them the 'Org Admin'.
    reg_res = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": email, "password": password, 
            "organization_name": f"{user_type_prefix} Test Org", "primary_phone": str(uuid.uuid4().int)[:10]
        }
    )
    assert reg_res.status_code == 201
    user_id = reg_res.json()["id"]

    # Login to get the token
    login_res = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": password} # No need to specify role, it will use default
    )
    assert login_res.status_code == 200
    token = login_res.json()["token"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Fetch the created user object from the database
    user = db.query(User).filter(User.id == user_id).first()
    assert user is not None
    
    return user, headers
def test_doctor_cannot_access_document_without_consent(client: TestClient, db_session: Session, s3_mock):
    """
    Test that a 403 Forbidden error is returned for access without consent.
    """
    # 1. Setup Patient and Doctor users using the new helper
    patient, patient_auth = create_and_login_user(client, db_session, "patient")
    doctor, doctor_auth = create_and_login_user(client, db_session, "doctor")

    # 2. Patient uploads a document
    client.put(f"{settings.API_V1_STR}/users/me/patient-profile", headers=patient_auth, json={"s3_data_prefix": f"patient-data/{patient.id}"})
    gen_res = client.post(f"{settings.API_V1_STR}/documents/generate-upload-url", headers=patient_auth, json={"file_name": "private.pdf", "content_type": "application/pdf", "document_category": "LAB_REPORT"})
    assert gen_res.status_code == 200
    doc_id = gen_res.json()["document_id"]
    
    # 3. Doctor tries to access it WITHOUT consent
    access_response = client.get(
        f"{settings.API_V1_STR}/data-access/documents/{doc_id}/view",
        headers=doctor_auth
    )
    
    # Assert the correct "Forbidden" error
    assert access_response.status_code == 403
    assert "No valid consent found" in access_response.json()["detail"]

def test_doctor_can_access_document_with_valid_consent(client: TestClient, db_session: Session, s3_mock):
    """
    Test the full successful flow: upload -> grant consent -> access.
    """
    # 1. Setup Patient and Doctor users
    patient, patient_auth = create_and_login_user(client, db_session, "patient")
    doctor, doctor_auth = create_and_login_user(client, db_session, "doctor")
    
    # 2. Patient uploads a document
    client.put(f"{settings.API_V1_STR}/users/me/patient-profile", headers=patient_auth, json={"s3_data_prefix": f"patient-data/{patient.id}"})
    gen_res = client.post(f"{settings.API_V1_STR}/documents/generate-upload-url", headers=patient_auth, json={"file_name": "shared.pdf", "content_type": "application/pdf", "document_category": "LAB_REPORT"})
    assert gen_res.status_code == 200
    doc_id = gen_res.json()["document_id"]

    # 3. Patient grants consent to the Doctor
    consent_data = {
        "data_fiduciary_id": str(doctor.id), # This now works because 'doctor' is defined
        "purpose": "Consultation",
        "data_categories": ["LAB_REPORT"],
        "expires_at": (datetime.utcnow() + timedelta(days=1)).isoformat()
    }
    consent_res = client.post(f"{settings.API_V1_STR}/consent/grant", headers=patient_auth, json=consent_data)
    assert consent_res.status_code == 201

    # 4. Doctor successfully accesses the document
    access_response = client.get(f"{settings.API_V1_STR}/data-access/documents/{doc_id}/view", headers=doctor_auth)
    
    assert access_response.status_code == 200
    data = access_response.json()
    assert "access_url" in data
    assert "mock_signature=true" in data["access_url"]