from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid

from app.core.config import settings
from app.db import models # Import models for the new test

# We will need the admin user helper for setup
from tests.api.v1.test_data_access import create_and_login_user
from app.core.security import verify_password

def test_user_registration(client: TestClient, db_session: Session):
    """Test successful user and organization registration."""
    email = f"testuser_{uuid.uuid4()}@example.com"
    password = "aVerySecurePassword"
    org_name = f"Test Org {uuid.uuid4()}"
    primary_phone = str(uuid.uuid4().int)[:10]

    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": email,
            "password": password,
            "primary_phone": primary_phone,
            "organization_name": org_name
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert "id" in data
    assert data["is_active"] is True # Self-registered user is active immediately

def test_duplicate_email_registration(client: TestClient, db_session: Session):
    """Test that registering with a duplicate email fails."""
    email = f"testuser_{uuid.uuid4()}@example.com"
    password = "aVerySecurePassword"
    
    # First registration should succeed
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": email, "password": password, 
            "primary_phone": str(uuid.uuid4().int)[:10], "organization_name": f"Test Org {uuid.uuid4()}"
        }
    )
    
    # Second registration with the same email should fail
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": email, "password": "anotherpassword", 
            "primary_phone": str(uuid.uuid4().int)[:10], "organization_name": "Another Org"
        }
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


# --- NEW TESTS FOR INVITATION ACCEPTANCE ---

def test_accept_invitation_success(client: TestClient, db_session: Session):
    """
    Tests that an invited user can successfully accept an invitation,
    set their password, and become an active user.
    """
    # 1. Setup: An admin invites a new user
    admin, admin_auth = create_and_login_user(client, db_session, "inviting_admin")
    client.post(f"{settings.API_V1_STR}/roles", headers=admin_auth, json={"name": "DOCTOR"})
    
    invitee_email = f"invited_user_{uuid.uuid4()}@test.com"
    invite_res = client.post(
        f"{settings.API_V1_STR}/organization/users/invite",
        headers=admin_auth,
        json={"email": invitee_email, "role": "DOCTOR"}
    )
    assert invite_res.status_code == 201
    invitation_token = invite_res.json()["invitation_token"]
    assert invitation_token is not None

    # 2. Action: The invited user accepts the invitation
    new_password = "aNewSecurePassword123"
    accept_res = client.post(
        f"{settings.API_V1_STR}/auth/accept-invitation",
        json={"invitation_token": invitation_token, "password": new_password}
    )
    assert accept_res.status_code == 200
    assert "Account successfully activated" in accept_res.json()["message"]

    # 3. Verification: The user is now active and can log in
    db_user = db_session.query(models.User).filter(models.User.email == invitee_email).first()
    assert db_user.is_active is True
    assert db_user.invitation_token is None # Token should be nullified

    login_res = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": invitee_email, "password": new_password}
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()["token"]

def test_cannot_accept_invitation_with_invalid_token(client: TestClient):
    """
    Tests that the accept invitation endpoint rejects a bad token.
    """
    response = client.post(
        f"{settings.API_V1_STR}/auth/accept-invitation",
        json={"invitation_token": "a-fake-token", "password": "password"}
    )
    assert response.status_code == 400
    assert "Invitation is invalid or has expired" in response.json()["detail"]


def test_password_reset_flow(client: TestClient, db_session: Session):
    """
    Tests the full password reset flow, from request to reset.
    """
    # 1. Setup: Create an active user
    user, _ = create_and_login_user(client, db_session, "reset_user")
    old_hashed_password = user.hashed_password

    # 2. Action: Request a password reset
    response = client.post(
        f"{settings.API_V1_STR}/auth/forgot-password",
        json={"email": user.email}
    )
    assert response.status_code == 200
    assert "link has been sent" in response.json()["message"]

    # 3. Verification: Check that a token was set in the DB
    db_session.refresh(user)
    assert user.password_reset_token is not None
    reset_token = user.password_reset_token

    # 4. Action: Use the token to set a new password
    new_password = "a-brand-new-secure-password"
    response = client.post(
        f"{settings.API_V1_STR}/auth/reset-password",
        json={"token": reset_token, "new_password": new_password}
    )
    assert response.status_code == 200
    assert "reset successfully" in response.json()["message"]

    # 5. Verification: The new password works, the old one does not
    db_session.refresh(user)
    assert user.password_reset_token is None # Token should be nullified
    assert verify_password(new_password, user.hashed_password) is True
    assert user.hashed_password != old_hashed_password