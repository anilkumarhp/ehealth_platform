from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pyotp
from datetime import datetime, timedelta

# --- NEW IMPORT ---
from urllib.parse import quote
import uuid

from app.core.config import settings
from app.db import models
from tests.api.v1.test_data_access import create_and_login_user

def test_generate_mfa_setup(client: TestClient, db_session: Session):
    """
    Tests that a logged-in user can successfully get an MFA secret and provisioning URI.
    """
    user, auth_headers = create_and_login_user(client, db_session, "mfa_user_1")

    response = client.post(
        f"{settings.API_V1_STR}/users/me/mfa/generate",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "secret" in data
    assert "qr_code" in data
    assert f"issuer={settings.MFA_ISSUER_NAME}" in data["qr_code"]
    
    # --- THIS IS THE FIX ---
    # We check that the encoded email exists between the final ':' and '?'
    encoded_email = quote(user.email)
    assert f":{encoded_email}?" in data["qr_code"]
    

def test_enable_mfa_with_valid_otp(client: TestClient, db_session: Session):
    """
    Tests that a user can enable MFA by providing a valid OTP.
    """
    user, auth_headers = create_and_login_user(client, db_session, "mfa_user_2")

    # Step 1: Generate the secret
    gen_response = client.post(f"{settings.API_V1_STR}/users/me/mfa/generate", headers=auth_headers)
    assert gen_response.status_code == 200
    secret = gen_response.json()["secret"]

    # Step 2: Generate the current valid OTP from the secret
    totp = pyotp.TOTP(secret)
    valid_otp = totp.now()

    # Step 3: Enable MFA with the secret and valid OTP
    enable_response = client.post(
        f"{settings.API_V1_STR}/users/me/mfa/enable?mfa_secret={secret}&otp={valid_otp}",
        headers=auth_headers
    )
    
    assert enable_response.status_code == 200
    assert "MFA has been successfully enabled" in enable_response.json()["message"]

    # Step 4: Verify in the database
    db_session.refresh(user)
    assert user.mfa_enabled is True
    assert user.mfa_secret == secret

def test_enable_mfa_fails_with_invalid_otp(client: TestClient, db_session: Session):
    """
    Tests that MFA enablement fails if the provided OTP is incorrect.
    """
    _, auth_headers = create_and_login_user(client, db_session, "mfa_user_3")
    
    gen_response = client.post(f"{settings.API_V1_STR}/users/me/mfa/generate", headers=auth_headers)
    secret = gen_response.json()["secret"]

    invalid_otp = "000000"
    
    enable_response = client.post(
        f"{settings.API_V1_STR}/users/me/mfa/enable?mfa_secret={secret}&otp={invalid_otp}",
        headers=auth_headers
    )
    
    assert enable_response.status_code == 400
    assert "Invalid OTP" in enable_response.json()["detail"]

def test_full_mfa_login_flow(client: TestClient, db_session: Session):
    """
    Tests the complete 2-step login flow for an MFA-enabled user.
    """
    user, _ = create_and_login_user(client, db_session, "mfa_user_4")
    secret = pyotp.random_base32()
    user.mfa_enabled = True
    user.mfa_secret = secret
    db_session.commit()

    # 2. First login step with password
    login_response_1 = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": user.email, "password": "testpassword"}
    )
    assert login_response_1.status_code == 200
    data_1 = login_response_1.json()
    assert data_1["mfa_required"] is True
    assert "mfa_token" in data_1
    mfa_token = data_1["mfa_token"]

    # 3. Second login step with OTP
    valid_otp = pyotp.TOTP(secret).now()
    login_response_2 = client.post(
        f"{settings.API_V1_STR}/auth/login/verify-mfa",
        json={"mfa_token": mfa_token, "otp": valid_otp}
    )
    
    assert login_response_2.status_code == 200
    data_2 = login_response_2.json()
    assert "access_token" in data_2
    assert data_2["token_type"] == "bearer"