from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta

from app.core.config import settings
from app.db import models
from tests.api.v1.test_data_access import create_and_login_user

def test_initiate_verification_success(client: TestClient, db_session: Session):
    """Test successfully initiating Aadhaar verification."""
    user_a, user_a_auth = create_and_login_user(client, db_session, "userA")
    
    response = client.post(
        f"{settings.API_V1_STR}/connections/initiate-verification",
        headers=user_a_auth,
        json={"member_aadhaar_number": "123456789012", "relationship_type": "Spouse"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "verification_transaction_id" in data

def test_initiate_verification_fails_if_mobile_not_linked(client: TestClient, db_session: Session):
    """Test the specific failure case where a mobile number is not linked to the Aadhaar."""
    user_a, user_a_auth = create_and_login_user(client, db_session, "userA")
    
    response = client.post(
        f"{settings.API_V1_STR}/connections/initiate-verification",
        headers=user_a_auth,
        json={"member_aadhaar_number": "111122220000", "relationship_type": "Spouse"}
    )
    
    assert response.status_code == 422
    data = response.json()
    assert data["detail"]["error_code"] == "AADHAAR_MOBILE_NOT_LINKED"

def test_complete_verification_flow(client: TestClient, db_session: Session):
    """Test the full, successful end-to-end verification and connection flow."""
    user_a, user_a_auth = create_and_login_user(client, db_session, "userA")
    
    user_b, _ = create_and_login_user(client, db_session, "userB")
    user_b.abha_id = "abha_for_123456789012"
    db_session.commit()
    db_session.refresh(user_b)
    
    # Step 1: Initiate
    init_res = client.post(
        f"{settings.API_V1_STR}/connections/initiate-verification",
        headers=user_a_auth,
        json={"member_aadhaar_number": "123456789012", "relationship_type": "Spouse"}
    )
    assert init_res.status_code == 200
    txn_id = init_res.json()["verification_transaction_id"]
    
    # Step 2: Complete with correct OTP
    # We pass the extra info needed by the endpoint as query parameters
    complete_res = client.post(
        f"{settings.API_V1_STR}/connections/complete-verification", # URL no longer has query params
        headers=user_a_auth,
        json={
            "verification_transaction_id": txn_id, 
            "otp": "123456",
            "relationship_type": "Spouse", # Now part of the JSON body
            "member_aadhaar_number": "123456789012" # Now part of the JSON body
        }
    )
    
    assert complete_res.status_code == 201
    data = complete_res.json()
    assert data["status"] == "VERIFIED"
    assert data["requester"]["id"] == str(user_a.id)
    assert data["approver"]["id"] == str(user_b.id)