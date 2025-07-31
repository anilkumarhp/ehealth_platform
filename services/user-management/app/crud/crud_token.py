from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models import RevokedRefreshToken, RefreshToken

def add_token_to_blacklist(db: Session, *, token_jti: str, expires_at: datetime) -> RevokedRefreshToken:
    db_token = RevokedRefreshToken(token_jti=token_jti, expires_at=expires_at)
    db.add(db_token)
    return db_token

def is_token_revoked(db: Session, *, token_jti: str) -> bool:
    token = db.query(RevokedRefreshToken).filter(RevokedRefreshToken.token_jti == token_jti).first()
    return token is not None

def create_refresh_token(db: Session, *, user_id: str, token: str, expires_at: datetime) -> RefreshToken:
    """Create a new refresh token in the database."""
    db_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_refresh_token(db: Session, *, token: str) -> RefreshToken:
    """Get a refresh token from the database."""
    return db.query(RefreshToken).filter(RefreshToken.token == token).first()

def delete_refresh_token(db: Session, *, token: str) -> None:
    """Delete a refresh token from the database."""
    db.query(RefreshToken).filter(RefreshToken.token == token).delete()
    db.commit()