import uuid
from sqlalchemy import (Boolean, Column, String, DateTime, ForeignKey, func, Date, Integer)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..base import Base
from .rbac import user_role_association # Import the association table

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Personal Information
    first_name = Column(String(100), nullable=True)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    
    # Contact Information
    email = Column(String(100), unique=True, index=True, nullable=False)
    primary_contact = Column(String(20), nullable=True)
    secondary_contact = Column(String(20), nullable=True)
    emergency_contact = Column(String(20), nullable=True)
    
    # Authentication
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String, nullable=True)
    
    # Identity
    aadhaar_last_4 = Column(String(4), nullable=True)
    hashed_aadhaar = Column(String, unique=True, index=True, nullable=True)
    
    # Storage
    bucket_name = Column(String(255), nullable=True)
    profile_pic = Column(String(500), nullable=True)
    
    # System
    last_login = Column(DateTime, nullable=True)
    invitation_token = Column(String, unique=True, index=True, nullable=True)
    invitation_expires_at = Column(DateTime, nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    roles = relationship("Role", secondary=user_role_association, backref="users")
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    insurances = relationship("PatientInsurance", back_populates="user", cascade="all, delete-orphan")
    family_members = relationship("FamilyMember", back_populates="user", cascade="all, delete-orphan")

    
    # Legacy fields for backward compatibility
    password_reset_token = Column(String, unique=True, nullable=True)
    password_reset_expires_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


