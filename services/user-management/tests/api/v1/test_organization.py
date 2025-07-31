from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid
from typing import List
from datetime import datetime, timedelta

from app.core.config import settings
from app.db import models
from app.crud import crud_user
# --- NEW IMPORT ---
from app.core.security import hash_password 
from tests.api.v1.test_data_access import create_and_login_user

def test_admin_can_get_organization_profile(client: TestClient, db_session: Session):
    """Tests an admin can fetch their organization's profile."""
    admin, admin_auth = create_and_login_user(client, db_session, "org_admin")
    response = client.get(f"{settings.API_V1_STR}/organization/profile", headers=admin_auth)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(admin.organization_id)

def test_admin_can_list_users(client: TestClient, db_session: Session):
    """Tests an admin can list users after inviting them."""
    admin, admin_auth = create_and_login_user(client, db_session, "listing_admin")
    client.post(f"{settings.API_V1_STR}/roles", headers=admin_auth, json={"name": "DOCTOR"})
    client.post(f"{settings.API_V1_STR}/roles", headers=admin_auth, json={"name": "PATIENT"})
    client.post(f"{settings.API_V1_STR}/organization/users/invite", headers=admin_auth, json={"email": "doctor@test.com", "role": "DOCTOR"})
    client.post(f"{settings.API_V1_STR}/organization/users/invite", headers=admin_auth, json={"email": "patient@test.com", "role": "PATIENT"})
    response = client.get(f"{settings.API_V1_STR}/organization/users", headers=admin_auth)
    assert response.status_code == 200
    assert len(response.json()) == 3

def test_admin_can_assign_roles(client: TestClient, db_session: Session):
    """Tests an admin can assign a role to a user."""
    admin, admin_auth = create_and_login_user(client, db_session, "role_admin")
    client.post(f"{settings.API_V1_STR}/roles", headers=admin_auth, json={"name": "PATIENT"})
    invitee_res = client.post(f"{settings.API_V1_STR}/organization/users/invite", headers=admin_auth, json={"email": "staff@test.com", "role": "PATIENT"})
    assert invitee_res.status_code == 201
    invitee_id = invitee_res.json()["id"]
    role_res = client.post(f"{settings.API_V1_STR}/roles", headers=admin_auth, json={"name": "Billing Staff"})
    assert role_res.status_code == 201
    role_id = role_res.json()["id"]
    assign_res = client.put(f"{settings.API_V1_STR}/organization/users/{invitee_id}/assign-roles", headers=admin_auth, json=[role_id])
    assert assign_res.status_code == 200
    updated_user_data = assign_res.json()
    assert "Billing Staff" in [r["name"] for r in updated_user_data["roles"]]

def test_non_admin_cannot_access_org_endpoints(client: TestClient, db_session: Session):
    """Tests that a non-admin user is forbidden from accessing admin routes."""
    admin, admin_auth = create_and_login_user(client, db_session, "admin_for_perms")
    
    role_res = client.post(f"{settings.API_V1_STR}/roles", headers=admin_auth, json={"name": "DOCTOR"})
    assert role_res.status_code == 201
    
    invite_res = client.post(f"{settings.API_V1_STR}/organization/users/invite", headers=admin_auth, json={"email": "doctor@test.com", "role": "DOCTOR"})
    assert invite_res.status_code == 201
    doctor_id = invite_res.json()["id"]
    
    # Manually activate the user for this test
    doctor_user = crud_user.get_user_by_id(db_session, user_id=doctor_id)
    doctor_user.is_active = True
    
    # --- THIS IS THE FIX ---
    # Hash the password before saving it to the database
    doctor_user.hashed_password = hash_password("testpassword")
    
    db_session.commit()

    # Login as the doctor
    doctor_login_res = client.post(f"{settings.API_V1_STR}/auth/login", json={"email": "doctor@test.com", "password": "testpassword", "role": "DOCTOR"})
    assert doctor_login_res.status_code == 200
    doctor_token = doctor_login_res.json()["token"]["access_token"]
    doctor_auth = {"Authorization": f"Bearer {doctor_token}"}
    
    # Doctor tries to access an admin-only endpoint
    response = client.get(f"{settings.API_V1_STR}/organization/users", headers=doctor_auth)
    
    assert response.status_code == 403

def test_admin_can_deactivate_user(client: TestClient, db_session: Session):
    """Tests that an admin can change a user's active status."""
    admin, admin_auth = create_and_login_user(client, db_session, "status_admin")
    client.post(f"{settings.API_V1_STR}/roles", headers=admin_auth, json={"name": "DOCTOR"})
    
    invite_res = client.post(
        f"{settings.API_V1_STR}/organization/users/invite",
        headers=admin_auth,
        json={"email": "user_to_deactivate@test.com", "role": "DOCTOR"}
    )
    user_id = invite_res.json()["id"]

    # Manually activate the user first
    user = crud_user.get_user_by_id(db_session, user_id=user_id)
    user.is_active = True
    db_session.commit()

    # Admin deactivates the user
    update_res = client.put(
        f"{settings.API_V1_STR}/organization/users/{user_id}",
        headers=admin_auth,
        json={"is_active": False}
    )
    assert update_res.status_code == 200
    assert update_res.json()["is_active"] is False

    # Verify in DB
    db_session.refresh(user)
    assert user.is_active is False