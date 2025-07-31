import uuid
from sqlalchemy import (Column, String, DateTime, ForeignKey, func, Enum as SQLEnum)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..base import Base
import enum

class ConnectionStatus(str, enum.Enum):
    VERIFICATION_PENDING = "VERIFICATION_PENDING"
    VERIFIED = "VERIFIED"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"

class FamilyConnection(Base):
    __tablename__ = 'family_connections'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    requester_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    approver_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    relationship_type = Column(String(50), nullable=False)
    status = Column(SQLEnum(ConnectionStatus), nullable=False, default=ConnectionStatus.VERIFICATION_PENDING)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    requester = relationship("User", foreign_keys=[requester_id])
    approver = relationship("User", foreign_keys=[approver_id])