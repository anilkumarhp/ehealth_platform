from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid
from app.crud import crud_rbac

from app.core.config import settings
from tests.api.v1.test_data_access import create_and_login_user

def get_admin_auth_headers(client: TestClient) -> dict[str, str]:
    """Helper function to register and login as an ORG_ADMIN."""
    email = f"admin_{uuid.uuid4()}@test.com"
    password = "adminpassword"
    
    # Register
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": email, "password": password, 
            "organization_name": "Admin Test Org", "primary_phone": str(uuid.uuid4().int)[:10]
        }
    )
    
    # Login
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": password, "role": "Org Admin"}
    )

    # --- ADD THESE DEBUGGING LINES ---
    print("\n--- LOGIN API RESPONSE ---")
    print(response.json())
    print("--------------------------\n")
    # --------------------------------

    # Original line that fails
    token = response.json()["token"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_list_all_permissions(client: TestClient):
    """Test that any user can list all available system permissions."""
    headers = get_admin_auth_headers(client) # Needs auth to get a DB session
    response = client.get(f"{settings.API_V1_STR}/permissions", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 5 # Check that our seeded permissions are there
    assert "document:create" in [p["name"] for p in data]

def test_org_admin_can_create_role(client: TestClient, db_session: Session):
    """Test that an ORG_ADMIN can create a new role."""
    headers = get_admin_auth_headers(client)
    
    # Get permissions to assign to the new role
    perms_response = client.get(f"{settings.API_V1_STR}/permissions", headers=headers)
    permissions = perms_response.json()
    doc_create_perm_id = next(p["id"] for p in permissions if p["name"] == "document:create")

    role_data = {
        "name": "Document Uploader",
        "description": "Can only create new documents.",
        "permission_ids": [doc_create_perm_id]
    }
    
    response = client.post(f"{settings.API_V1_STR}/roles", headers=headers, json=role_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Document Uploader"
    assert len(data["permissions"]) == 1
    assert data["permissions"][0]["id"] == doc_create_perm_id


def test_admin_can_delete_role(client: TestClient, db_session: Session):
    """Tests that an ORG_ADMIN can delete a custom role."""
    admin, admin_auth = create_and_login_user(client, db_session, "role_deleter")
    
    # 1. Create a custom role to be deleted
    role_data = {"name": "Temporary Role"}
    role_res = client.post(f"{settings.API_V1_STR}/roles", headers=admin_auth, json=role_data)
    assert role_res.status_code == 201
    role_id = role_res.json()["id"]

    # 2. Delete the role
    delete_res = client.delete(f"{settings.API_V1_STR}/roles/{role_id}", headers=admin_auth)
    assert delete_res.status_code == 204

    # 3. Verify the role is gone
    role_in_db = crud_rbac.get_role_by_id(db_session, role_id=role_id, org_id=admin.organization_id)
    assert role_in_db is None