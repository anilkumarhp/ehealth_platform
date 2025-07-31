from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid
from datetime import datetime, timedelta

from app.db import models
from app.api.v1.schemas import user as user_schema
from app.core.security import hash_password, generate_secure_token
from app.core.exceptions import UserNotFoundException, DetailException
from app.crud import crud_rbac

def get_user_by_id(db: Session, user_id: uuid.UUID) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str, raise_exception: bool = False) -> models.User | None:
    # ... (no changes)
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user and raise_exception:
        raise UserNotFoundException()
    return user

def get_user_by_abha_id(db: Session, abha_id: str, raise_exception: bool = False) -> models.User | None:
    # ... (no changes)
    user = db.query(models.User).filter(models.User.abha_id == abha_id).first()
    if not user and raise_exception:
        raise UserNotFoundException(detail="User with provided ABHA ID not found.")
    return user

def get_users_by_phone(db: Session, phone: str) -> list[models.User]:
    # ... (no changes)
    return db.query(models.User).join(models.Patient).filter(models.Patient.primary_phone == phone).all()

def get_user_by_invitation_token(db: Session, *, token: str) -> models.User | None:
    # ... (no changes)
    return db.query(models.User).filter(models.User.invitation_token == token).first()

def create_user_with_id(db: Session, user: user_schema.UserCreate, organization_id: uuid.UUID = None, user_id: uuid.UUID = None, s3_bucket_name: str = None) -> models.User:
    """Create user with a pre-generated ID"""
    # Ensure organization_id is never null
    if organization_id is None:
        # Use the default Patients organization
        patients_org_id = uuid.UUID('11111111-1111-1111-1111-111111111111')
        patients_org = db.query(models.Organization).filter(models.Organization.id == patients_org_id).first()
        
        if not patients_org:
            from app.api.v1.schemas import organization as org_schema
            from app.crud import crud_organization
            # Create the default Patients organization if it doesn't exist
            patients_org = crud_organization.create_organization(
                db=db,
                organization=org_schema.OrganizationCreate(
                    name="Patients",
                    id=patients_org_id
                )
            )
            db.flush()
        
        organization_id = patients_org_id
    
    # Create the user with the pre-generated ID
    hashed_pass = hash_password(user.password)
    db_user = models.User(
        id=user_id,  # Use the pre-generated ID
        email=user.email,
        hashed_password=hashed_pass,
        organization_id=organization_id,
        is_active=True,
        personal_info=user.personal_info.model_dump() if user.personal_info else None,
        abha_id=user.abha_id,
        role='PATIENT',
        permissions=[],
        s3_bucket_name=s3_bucket_name
    )
    db.add(db_user)
    return db_user

def create_user(db: Session, user: user_schema.UserCreate, organization_id: uuid.UUID = None, s3_bucket_name: str = None) -> models.User:
    # Ensure organization_id is never null
    if organization_id is None:
        # Use the default Patients organization
        patients_org_id = uuid.UUID('11111111-1111-1111-1111-111111111111')
        patients_org = db.query(models.Organization).filter(models.Organization.id == patients_org_id).first()
        
        if not patients_org:
            from app.api.v1.schemas import organization as org_schema
            from app.crud import crud_organization
            # Create the default Patients organization if it doesn't exist
            patients_org = crud_organization.create_organization(
                db=db,
                organization=org_schema.OrganizationCreate(
                    name="Patients",
                    id=patients_org_id
                )
            )
            db.flush()
        
        organization_id = patients_org_id
    
    # Create the user with the organization ID
    hashed_pass = hash_password(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_pass,
        organization_id=organization_id,  # This is now guaranteed to be non-null
        is_active=True,
        personal_info=user.personal_info.model_dump() if user.personal_info else None,
        abha_id=user.abha_id,
        role='PATIENT',  # Default role
        permissions=[],   # Default permissions
        s3_bucket_name=s3_bucket_name  # Add S3 bucket name if provided
    )
    db.add(db_user)
    return db_user

def create_invited_user(db: Session, *, email: str, role: str, organization_id: uuid.UUID) -> models.User:
    # ... (no changes)
    role_obj = crud_rbac.get_role_by_name(db, name=role, org_id=organization_id)
    if not role_obj:
        raise DetailException(detail=f"Role '{role}' does not exist in this organization. Please create it first.")
    token = generate_secure_token()
    expires_at = datetime.utcnow() + timedelta(hours=72)
    db_user = models.User(
        email=email, organization_id=organization_id, is_active=False,
        invitation_token=token, invitation_expires_at=expires_at
    )
    db_user.roles.append(role_obj)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, *, user: models.User, updates: Dict[str, Any]) -> models.User:
    """A generic function to update user fields."""
    # Get a fresh instance of the user from the current session
    user = db.query(models.User).filter(models.User.id == user.id).first()
    if not user:
        raise ValueError(f"User with ID {user.id} not found")
        
    # Handle special case for patient_phone
    if "patient_phone" in updates:
        if hasattr(user, 'patient_profile') and user.patient_profile:
            # Get the patient from the database directly to avoid session issues
            patient = db.query(models.Patient).filter(models.Patient.user_id == user.id).first()
            if patient:
                patient.primary_phone = updates.pop("patient_phone")
    
    # Update regular user fields
    for key, value in updates.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

def update_user_profile_photo(db: Session, *, user: models.User, photo_url: str, s3_bucket: str = None) -> models.User:
    """Update a user's profile photo URL and S3 bucket information."""
    # Update the profile_photo_url field
    user.profile_photo_url = photo_url
    
    # Update the s3_bucket_name if provided
    if s3_bucket:
        user.s3_bucket_name = s3_bucket
    
    # Also update the profile_data JSON field to maintain backward compatibility
    if user.profile_data is None:
        user.profile_data = {}
    
    # Convert from SQLAlchemy JSON type to Python dict if needed
    profile_data = dict(user.profile_data) if user.profile_data else {}
    profile_data["photo"] = photo_url
    user.profile_data = profile_data
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def enable_mfa(db: Session, *, user: models.User, secret: str) -> models.User:
    # ... (no changes)
    user.mfa_secret = secret
    user.mfa_enabled = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_password_reset_token(db: Session, *, user: models.User) -> models.User:
    """Generate and set a password reset token for a user."""
    token = generate_secure_token()
    expires_at = datetime.utcnow() + timedelta(hours=1) # Token is valid for 1 hour
    
    user.password_reset_token = token
    user.password_reset_expires_at = expires_at
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_password_reset_token(db: Session, *, token: str) -> models.User | None:
    """Get a user by their password reset token."""
    return db.query(models.User).filter(models.User.password_reset_token == token).first()
def authenticate(db: Session, *, email: str, password: str) -> models.User | None:
    """Authenticate a user by email and password."""
    from app.core.security import verify_password
    
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user