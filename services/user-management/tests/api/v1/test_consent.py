from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta

from app.core.config import settings
from tests.api.v1.test_data_access import create_and_login_user

def test_patient_can_grant_and_list_consent(client: TestClient, db_session: Session):
    """
    Tests that a patient can grant consent and then see it in their list of grants.
    """
    patient, patient_auth = create_and_login_user(client, db_session, "patient_for_consent")
    doctor, _ = create_and_login_user(client, db_session, "doctor_for_consent")
    
    # 1. Patient grants consent to the Doctor
    consent_data = {
        "data_fiduciary_id": str(doctor.id),
        "purpose": "General Checkup",
        "data_categories": ["LAB_REPORT", "PRESCRIPTION"],
        "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }
    response = client.post(f"{settings.API_V1_STR}/consent/grant", headers=patient_auth, json=consent_data)
    
    assert response.status_code == 201
    created_consent = response.json()
    assert created_consent["data_fiduciary_id"] == str(doctor.id)
    assert created_consent["status"] == "GRANTED"

    # 2. Patient lists their granted consents
    response = client.get(f"{settings.API_V1_STR}/consent/my-grants", headers=patient_auth)
    assert response.status_code == 200
    grants = response.json()
    assert isinstance(grants, list)
    assert len(grants) == 1
    assert grants[0]["id"] == created_consent["id"]

def test_patient_can_revoke_consent(client: TestClient, db_session: Session):
    """
    Tests that a patient can revoke a consent they have granted.
    """
    patient, patient_auth = create_and_login_user(client, db_session, "patient_for_revoke")
    doctor, _ = create_and_login_user(client, db_session, "doctor_for_revoke")
    
    # 1. Grant consent first
    consent_data = {
        "data_fiduciary_id": str(doctor.id),
        "purpose": "Second Opinion",
        "data_categories": ["LAB_REPORT"],
        "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }
    grant_response = client.post(f"{settings.API_V1_STR}/consent/grant", headers=patient_auth, json=consent_data)
    consent_id = grant_response.json()["id"]

    # 2. Revoke the consent
    revoke_response = client.put(f"{settings.API_V1_STR}/consent/{consent_id}/revoke", headers=patient_auth)
    assert revoke_response.status_code == 200
    revoked_consent = revoke_response.json()
    assert revoked_consent["status"] == "REVOKED"
    assert revoked_consent["withdrawn_at"] is not None

def test_patient_cannot_grant_self_consent(client: TestClient, db_session: Session):
    """
    Tests that our logic prevents a user from granting consent to themselves.
    """
    patient, patient_auth = create_and_login_user(client, db_session, "self_consent_patient")
    
    consent_data = {
        "data_fiduciary_id": str(patient.id), # Using own ID
        "purpose": "Self Check",
        "data_categories": ["LAB_REPORT"],
        "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }
    response = client.post(f"{settings.API_V1_STR}/consent/grant", headers=patient_auth, json=consent_data)
    
    assert response.status_code == 400
    assert "Cannot grant consent to yourself" in response.json()["detail"]

def test_patient_cannot_revoke_others_consent(client: TestClient, db_session: Session):
    """
    Tests that Patient A cannot revoke a consent granted by Patient B.
    """
    patient_a, patient_a_auth = create_and_login_user(client, db_session, "patientA_revoke")
    patient_b, patient_b_auth = create_and_login_user(client, db_session, "patientB_revoke")
    doctor, _ = create_and_login_user(client, db_session, "doctor_revoke")

    # Patient B grants consent to the Doctor
    consent_data = {
        "data_fiduciary_id": str(doctor.id),
        "purpose": "Patient B's Checkup",
        "data_categories": ["LAB_REPORT"],
        "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }
    grant_response = client.post(
        f"{settings.API_V1_STR}/consent/grant", # <-- The real URL
        headers=patient_b_auth, 
        json=consent_data
    )
    assert grant_response.status_code == 201
    consent_id = grant_response.json()["id"]
    
    # Now, Patient A tries to revoke Patient B's consent
    revoke_response = client.put(
        f"{settings.API_V1_STR}/consent/{consent_id}/revoke", # <-- The real URL
        headers=patient_a_auth
    )

    # Assert that Patient A is forbidden from this action
    assert revoke_response.status_code == 403
    assert "Not authorized to revoke this consent" in revoke_response.json()["detail"]