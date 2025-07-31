from datetime import datetime, timedelta, timezone
from typing import Any
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import settings
import uuid
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: str | Any, expires_delta: timedelta | None = None, claims: dict = {}, mfa_enabled: bool = False) -> str:
    """Creates a short-lived JWT access token with custom claims and a unique jti."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    to_encode.update(claims)
    
    # Add MFA status to the token
    to_encode["mfa_enabled"] = mfa_enabled
    
    # Add a unique identifier to every access token to ensure uniqueness
    to_encode["jti"] = str(uuid.uuid4())
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: str | Any) -> str:
    """Creates a long-lived JWT refresh token with a unique identifier (jti)."""
    expires = datetime.now(timezone.utc) + timedelta(days=15)
    to_encode = {"exp": expires, "sub": str(subject), "jti": str(uuid.uuid4())}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_mfa_token(subject: str | Any) -> str:
    """Creates a short-lived JWT for the second step of MFA verification."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    to_encode = {"exp": expire, "sub": str(subject), "scope": "mfa:verify"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def generate_secure_token(length: int = 32) -> str:
    """Generates a cryptographically secure, URL-safe string."""
    return secrets.token_urlsafe(length)