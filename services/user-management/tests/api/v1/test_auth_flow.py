from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from jose import jwt

from app.core.config import settings
from tests.api.v1.test_data_access import create_and_login_user
from app.crud import crud_token

def test_login_issues_access_and_refresh_tokens(client: TestClient, db_session: Session):
    """Tests that a successful login returns both token types."""
    user, _ = create_and_login_user(client, db_session, "token_user")
    
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": user.email, "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("token") is not None
    assert "access_token" in data["token"]
    assert "refresh_token" in data["token"]

def test_refresh_token_flow(client: TestClient, db_session: Session):
    """Tests that a valid refresh token can be used to get a new access token."""
    user, _ = create_and_login_user(client, db_session, "refresh_user")
    
    login_res = client.post(f"{settings.API_V1_STR}/auth/login", json={"email": user.email, "password": "testpassword"})
    original_access_token = login_res.json()["token"]["access_token"]
    refresh_token = login_res.json()["token"]["refresh_token"]

    refresh_res = client.post(f"{settings.API_V1_STR}/auth/refresh-token", json={"refresh_token": refresh_token})
    assert refresh_res.status_code == 200
    new_access_token = refresh_res.json()["access_token"]
    assert new_access_token != original_access_token

def test_logout_revokes_refresh_token(client: TestClient, db_session: Session):
    """Tests that logging out prevents a refresh token from being used again."""
    user, _ = create_and_login_user(client, db_session, "logout_user")
    
    login_res = client.post(f"{settings.API_V1_STR}/auth/login", json={"email": user.email, "password": "testpassword"})
    refresh_token = login_res.json()["token"]["refresh_token"]

    # 1. Logout: this should add the token's JTI to the blacklist
    logout_res = client.post(f"{settings.API_V1_STR}/auth/logout", json={"refresh_token": refresh_token})
    assert logout_res.status_code == 200

    # 2. Verify in the database that the token is now blacklisted
    payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    jti = payload.get("jti")
    assert crud_token.is_token_revoked(db_session, token_jti=jti) is True

    # 3. Try to use the same refresh token again
    refresh_res_after_logout = client.post(f"{settings.API_V1_STR}/auth/refresh-token", json={"refresh_token": refresh_token})
    assert refresh_res_after_logout.status_code == 401
    assert "revoked" in refresh_res_after_logout.json()["detail"]