import uuid
from sqlalchemy import (Column, String, DateTime)
from sqlalchemy.dialects.postgresql import UUID
from ..base import Base

class RevokedRefreshToken(Base):
    __tablename__ = 'revoked_refresh_tokens'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # 'jti' is the standard "JWT ID" claim, used to uniquely identify a token.
    token_jti = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    token = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)