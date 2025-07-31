from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Generator, Optional

from app.db.session import SessionLocal, engine
from app.core.config import settings
from app.db import models
from app.crud import crud_user
from app.api.v1.schemas.token import TokenData
from app.core.exceptions import UserNotFoundException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_public_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        # Get the new permission claims from the token
        permissions: list[str] = payload.get("perms", [])
        role: str = payload.get("role") # The role the user logged in as
        if email is None:
            raise credentials_exception
        
        return {
            "email": email,
            "role": role,
            "permissions": set(permissions)
        }
    except JWTError:
        raise credentials_exception

def get_current_user_from_db(
    db: Session = Depends(get_public_db),
    user_data: dict = Depends(get_current_user)
) -> models.User:
    try:
        user = crud_user.get_user_by_email(db, email=user_data["email"], raise_exception=True)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Attach token data to the user object for use in endpoints
    user.token_role = user_data["role"]
    user.token_permissions = user_data["permissions"]
    return user

def require_permission(required_permission: str):
    """
    Dependency factory to check for a specific permission in the user's token.
    """
    def permission_checker(current_user: models.User = Depends(get_current_user)):
        if required_permission not in current_user.token_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Requires: {required_permission}"
            )
        return current_user
    return permission_checker

def get_current_user_optional(
    db: Session = Depends(get_public_db),
    authorization: Optional[str] = Header(None)
) -> Optional[models.User]:
    """
    Similar to get_current_user but doesn't raise an exception if no token is provided.
    Returns None instead.
    """
    if not authorization:
        return None
        
    try:
        # Extract token from Authorization header
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            return None
            
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        permissions: list[str] = payload.get("perms", [])
        role: str = payload.get("role")
        
        if not email:
            return None
            
        user = crud_user.get_user_by_email(db, email=email)
        if not user:
            return None
            
        # Attach token data to the user object
        user.token_role = role
        user.token_permissions = set(permissions)
        return user
    except (JWTError, ValueError):
        return None

def get_db(current_user: models.User = Depends(get_current_user_from_db)) -> Generator:
    tenant_schema_name = f"org_{str(current_user.organization_id).replace('-', '')}"
    with engine.connect() as connection:
        connection.exec_driver_sql(f"SET search_path TO {tenant_schema_name}, public")
        db = SessionLocal(bind=connection)
        try:
            yield db
        finally:
            db.close()