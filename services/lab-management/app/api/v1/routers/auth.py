from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.core.security import TokenPayload

router = APIRouter()

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Mock login endpoint for testing lab management independently.
    In production, this would call the User Management Service.
    """
    # Mock credentials for testing
    if form_data.username == "testuser" and form_data.password == "testpass":
        # Return a mock token that the gRPC client will recognize
        mock_token = "mock_token_for_testing_12345"
        return TokenResponse(access_token=mock_token, token_type="bearer")
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials. Use username: testuser, password: testpass",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.get("/me", response_model=TokenPayload)
async def read_users_me(current_user: TokenPayload = Depends(get_current_user)):
    """
    Get current user information from token.
    Use this endpoint to test your authentication.
    """
    return current_user