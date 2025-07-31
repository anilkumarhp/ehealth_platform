from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any
from pydantic import BaseModel, EmailStr
from datetime import datetime
import pyotp
from datetime import timezone
import traceback
import os

from app.crud import crud_token
from app.core.security import create_refresh_token
from fastapi import Response
import uuid

# --- NEW: Add JWTError to this import from jose ---
from jose import jwt, JWTError
from app.tasks.email_tasks import send_password_reset_email
from app.integrations.s3_client import s3_client

from app.api.v1 import deps
from app.crud import crud_user, crud_organization, crud_patient, crud_rbac, crud_token
from app.api.v1.schemas import (
    user as user_schema,
    organization as org_schema,
    token as token_schema,
    patient as patient_schema,
    rbac as rbac_schema,
    register as register_schema,
    mfa as mfa_schema
)
from app.core.security import create_access_token, verify_password, hash_password, create_mfa_token
from app.core.config import settings
from app.db import models

router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- Schemas used only by this router ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: str | None = None

class Token(token_schema.Token):
    refresh_token: str

class UserAndOrgCreate(user_schema.UserCreate):
    organization_name: str

class InvitationAcceptRequest(BaseModel):
    invitation_token: str
    password: str
    personal_info: user_schema.PersonalInfo | None = None

class MessageResponse(BaseModel):
    message: str

class LoginResponse(BaseModel):
    token: token_schema.Token | None = None
    mfa_required: bool = False
    mfa_token: str | None = None

class MFAVerifyRequest(BaseModel):
    mfa_token: str
    otp: str

class CompleteMFASetupRequest(BaseModel):
    user_id: str
    mfa_secret: str
    otp: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class Token(token_schema.Token): # Inherit from the existing Token schema
    refresh_token: str

class LoginResponse(BaseModel):
    token: Token | None = None # This will now contain both tokens
    mfa_required: bool = False
    mfa_token: str | None = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# --- Endpoints ---

@router.post("/register", response_model=register_schema.RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(
    *,
    db: Session = Depends(deps.get_public_db),
    user_in: register_schema.RegisterWithMFARequest
) -> Any:
    """Register a new user without MFA setup"""
    # Set enable_mfa to False to ensure MFA is not enabled
    user_in.enable_mfa = False
    # Call the register_with_mfa function with MFA disabled
    return register_with_mfa(db=db, user_in=user_in)

@router.post("/register-with-mfa", response_model=register_schema.RegisterResponse, status_code=status.HTTP_201_CREATED)
def register_with_mfa(
    *,
    db: Session = Depends(deps.get_public_db),
    user_in: register_schema.RegisterWithMFARequest
) -> Any:
    """Register a new user with optional MFA setup"""
    user = crud_user.get_user_by_email(db=db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    try:
        # Get organization ID - either directly provided or from organization_name
        # Default to the Patients organization ID
        patients_org_id = uuid.UUID('11111111-1111-1111-1111-111111111111')
        organization_id = patients_org_id
        
        # First, ensure the Patients organization exists
        patients_org = db.query(models.Organization).filter(models.Organization.id == patients_org_id).first()
        if not patients_org:
            # Create the default Patients organization if it doesn't exist
            patients_org = crud_organization.create_organization(
                db=db,
                organization=org_schema.OrganizationCreate(
                    name="Patients",
                    id=patients_org_id
                )
            )
            db.flush()
            organization_id = patients_org.id
        
        # If organization_id is directly provided, use it
        if hasattr(user_in, 'organization_id') and user_in.organization_id:
            try:
                org_uuid = uuid.UUID(user_in.organization_id)
                org = db.query(models.Organization).get(org_uuid)
                if org:
                    organization_id = org.id
                else:
                    # If the specified organization doesn't exist, fall back to Patients org
                    print(f"Organization with ID {user_in.organization_id} not found. Using default Patients organization.")
            except ValueError:
                # If the ID format is invalid, fall back to Patients org
                print(f"Invalid organization ID format: {user_in.organization_id}. Using default Patients organization.")
        
        # Otherwise use organization_name if provided
        elif user_in.organization_name:
            # Check if the organization already exists
            existing_org = db.query(models.Organization).filter(models.Organization.name == user_in.organization_name).first()
            
            if existing_org:
                organization_id = existing_org.id
            else:
                # Create new organization
                organization = crud_organization.create_organization(
                    db=db, 
                    organization=org_schema.OrganizationCreate(name=user_in.organization_name)
                )
                db.flush()
                organization_id = organization.id
                
                # Create admin role for organization
                admin_role_in = rbac_schema.RoleCreate(
                    name="Org Admin", 
                    description="Full administrative access for the organization."
                )
                admin_role = crud_rbac.create_role(db=db, role_in=admin_role_in, org_id=organization.id)
        
        # Log the organization ID being used
        print(f"Using organization_id: {organization_id} for user registration")
        
        # Ensure organization_id is not None
        if organization_id is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to determine organization ID for user registration."
            )
        
        # Get phone number from either field
        primary_phone = user_in.phone or user_in.primary_phone
        if not primary_phone:
            raise HTTPException(
                status_code=400,
                detail="Either 'phone' or 'primary_phone' must be provided."
            )
        
        # Create or update personal info
        personal_info = {}
        
        # If personal_info is provided as an object, convert to dict
        if user_in.personal_info:
            if isinstance(user_in.personal_info, dict):
                personal_info = user_in.personal_info
            else:
                try:
                    personal_info = user_in.personal_info.model_dump()
                except AttributeError:
                    personal_info = user_in.personal_info.__dict__
            
        # Update personal info with new fields if provided
        for field in ['first_name', 'last_name', 'display_name', 'date_of_birth', 
                      'gender', 'blood_group', 'emergency_contact', 'aadhar_id']:
            if hasattr(user_in, field) and getattr(user_in, field) is not None:
                personal_info[field] = getattr(user_in, field)
            
        # Handle address if provided
        if hasattr(user_in, 'address') and user_in.address:
            if isinstance(user_in.address, dict):
                personal_info["address"] = user_in.address
            else:
                try:
                    personal_info["address"] = user_in.address.model_dump()
                except AttributeError:
                    personal_info["address"] = user_in.address.__dict__
                
        # Create profile data
        profile_data = {}
        
        # If profile_data is provided, use it
        if user_in.profile_data:
            if isinstance(user_in.profile_data, dict):
                profile_data = user_in.profile_data
            else:
                try:
                    profile_data = user_in.profile_data.model_dump()
                except AttributeError:
                    profile_data = user_in.profile_data.__dict__
        
        # Generate user ID manually before creating user
        user_id = uuid.uuid4()
        print(f"Generated user ID: {user_id}")
        
        # Add photo URL if provided - we'll update this later if we upload to S3
        photo_base64 = None
        if hasattr(user_in, 'photo') and user_in.photo:
            photo_base64 = user_in.photo
            profile_data["photo"] = user_in.photo
            
        # Create user with pre-generated ID
        user_create = user_schema.UserCreate(
            email=user_in.email,
            password=user_in.password,
            primary_phone=primary_phone,
            personal_info=personal_info,
            profile_data=profile_data
        )
        
        new_user = crud_user.create_user_with_id(
            db=db, 
            user=user_create, 
            organization_id=organization_id,
            user_id=user_id
        )
        db.flush()
        
        # Create user folder in the main S3 bucket and save the path
        try:
            # Generate user name for folder creation
            user_name = f"{personal_info.get('first_name', '')}-{personal_info.get('last_name', '')}"
            if not user_name.strip('-'):
                user_name = user_in.email.split('@')[0]
            
            # Create user folder in the main bucket using pre-generated ID
            user_folder_path = s3_client.create_user_bucket(str(user_id), user_name)
            
            # Save folder path to user record
            new_user.s3_bucket_name = user_folder_path
            
            # Upload profile photo to S3 if provided
            if photo_base64 and os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
                try:
                    # Upload the base64 image to S3
                    photo_url = s3_client.upload_base64_image(
                        base64_data=photo_base64,
                        user_bucket=user_folder_path,
                        file_type="profile_photo"
                    )
                    
                    # Update the user's profile_photo_url field
                    new_user.profile_photo_url = photo_url
                    
                    # Also update the profile_data JSON field
                    if not profile_data:
                        profile_data = {}
                    profile_data["photo"] = photo_url
                    new_user.profile_data = profile_data
                    
                    print(f"Uploaded profile photo to S3: {photo_url}")
                except Exception as photo_error:
                    print(f"Failed to upload profile photo to S3: {str(photo_error)}")
            
            db.add(new_user)
            db.flush()
        except Exception as e:
            # Log the error but continue with registration
            print(f"Failed to create user folder in S3: {str(e)}")
            
        # Assign role if organization was created
        if organization_id and 'admin_role' in locals():
            crud_rbac.assign_roles_to_user(db, user=new_user, role_ids=[admin_role.id])
        
        # Create patient profile with insurance information if provided
        patient_data = {
            "primary_phone": primary_phone,
            "insurance_info": []
        }
        
        # Add additional patient fields from personal_info
        if "blood_group" in personal_info:
            patient_data["blood_group"] = personal_info["blood_group"]
            
        # Check if Aadhaar ID exists and is valid
        if "aadhar_id" in personal_info and personal_info["aadhar_id"]:
            aadhaar_id = personal_info["aadhar_id"]
            print(f"Checking Aadhaar ID: {aadhaar_id}")
            try:
                # Check if this Aadhaar ID is already in use
                existing_user = db.query(models.User).filter(models.User.aadhaar_last_4 == aadhaar_id[-4:]).first()
                if existing_user:
                    print(f"Aadhaar ID {aadhaar_id} already exists for user {existing_user.id}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Aadhaar ID {aadhaar_id} is already registered with another account."
                    )
                patient_data["aadhaar_id"] = aadhaar_id
                print(f"Aadhaar ID {aadhaar_id} is available")
            except HTTPException:
                raise
            except Exception as aadhaar_error:
                print(f"Error checking Aadhaar ID: {str(aadhaar_error)}")
                print(f"Aadhaar check traceback: {traceback.format_exc()}")
                raise
        
        # Add insurance information if provided
        if hasattr(user_in, 'insurance') and user_in.insurance:
            print(f"Processing {len(user_in.insurance)} insurance records")
            for insurance in user_in.insurance:
                insurance_data = {}
                if isinstance(insurance, dict):
                    insurance_data = insurance
                else:
                    try:
                        insurance_data = insurance.model_dump()
                    except AttributeError:
                        insurance_data = insurance.__dict__
                
                # Ensure policy_number is present
                if 'policy_number' not in insurance_data or not insurance_data['policy_number']:
                    print(f"Skipping insurance record without policy number: {insurance_data}")
                    continue
                    
                patient_data["insurance_info"].append(insurance_data)
        else:
            print("No insurance information provided for patient")
        
        try:
            patient_schema_in = patient_schema.PatientCreate(**patient_data)
            crud_patient.create_patient(db=db, patient_in=patient_schema_in, user_id=user_id)
        except Exception as e:
            # Log the error but continue - we don't want to fail the whole registration
            # if just the patient profile creation fails
            print(f"Error creating patient profile: {str(e)}")
            # We could add a flag to the response indicating the patient profile wasn't created
        
        # Generate MFA setup if requested
        mfa_setup = None
        if user_in.enable_mfa:
            # Generate a new secret - use exactly 32 characters (160 bits) to meet security requirements
            # Base32 encoding: each character represents 5 bits, so 32 chars = 160 bits
            secret = pyotp.random_base32(32)
            
            # Generate provisioning URI with a shorter issuer name and parameters
            # Keep the URI as short as possible for QR code compatibility
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(
                name=new_user.email.split('@')[0],  # Use only username part of email
                issuer_name="eHealth"  # Short issuer name
            )
            
            # Create a pre-encoded QR code URL for the frontend
            qr_code_url = f"otpauth://totp/eHealth:{new_user.email.split('@')[0]}?secret={secret}&issuer=eHealth"
            
            mfa_setup = {
                "qr_code": qr_code_url,
                "secret": secret
            }
        
        # Commit all changes
        db.commit()
        db.refresh(new_user)
        
        # Always generate tokens - for MFA we'll still need them to access the dashboard
        # The MFA verification will happen separately
        user_permissions = {perm.name for role in new_user.roles for perm in role.permissions}
        user_role_names = {role.name for role in new_user.roles}
        default_role = list(user_role_names)[0] if user_role_names else "PATIENT"
        
        access_token = create_access_token(
            subject=new_user.email,
            claims={"role": default_role, "org_id": str(new_user.organization_id), "perms": list(user_permissions)},
            mfa_enabled=user_in.enable_mfa
        )
        refresh_token = create_refresh_token(subject=new_user.email)
        token = {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token
        }
        
        return {
            "user_id": str(new_user.id),
            "email": new_user.email,
            "mfa_setup": mfa_setup,
            "mfa_enabled": user_in.enable_mfa,
            "token": token  # Always return token regardless of MFA status
        }
        
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions (like duplicate Aadhaar) with original status and message
        db.rollback()
        raise http_exc
    except Exception as e:
        db.rollback()
        print(f"Registration error: {str(e)}")
        print(f"Registration traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )

@router.post("/complete-mfa-setup", response_model=MessageResponse)
def complete_mfa_setup(
    *,
    db: Session = Depends(deps.get_db),
    setup_request: CompleteMFASetupRequest
) -> Any:
    """Complete MFA setup by verifying the OTP and enabling MFA for the user"""
    try:
        # Get the user
        user_id = uuid.UUID(setup_request.user_id)
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify the OTP
        totp = pyotp.TOTP(setup_request.mfa_secret)
        if not totp.verify(setup_request.otp):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP"
            )
        
        # Enable MFA for the user
        user.mfa_secret = setup_request.mfa_secret
        user.mfa_enabled = True
        db.add(user)
        db.commit()
        
        return {"message": "MFA setup completed successfully"}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during MFA setup: {str(e)}"
        )
@router.post("/login", response_model=LoginResponse)
def login(
    *,
    db: Session = Depends(deps.get_public_db),
    login_request: LoginRequest
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud_user.authenticate(
        db, email=login_request.email, password=login_request.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )
    
    # Check if MFA is enabled for this user
    if user.mfa_enabled and user.mfa_secret:
        # Generate a temporary MFA token
        mfa_token = create_mfa_token(user.email)
        return {
            "mfa_required": True,
            "mfa_token": mfa_token,
            "token": None
        }
    
    # Get user permissions and roles
    user_permissions = {perm.name for role in user.roles for perm in role.permissions}
    user_role_names = {role.name for role in user.roles}
    
    # Use the requested role if provided and valid, otherwise use the first role
    role = None
    if login_request.role and login_request.role in user_role_names:
        role = login_request.role
    else:
        role = list(user_role_names)[0] if user_role_names else "PATIENT"
    
    # Create access token
    access_token = create_access_token(
        subject=user.email,
        claims={"role": role, "org_id": str(user.organization_id), "perms": list(user_permissions)},
        mfa_enabled=user.mfa_enabled
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(subject=user.email)
    
    # Store refresh token in database
    crud_token.create_refresh_token(
        db=db,
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.now(timezone.utc) + settings.REFRESH_TOKEN_EXPIRE_TIMEDELTA
    )
    
    return {
        "mfa_required": False,
        "mfa_token": None,
        "token": {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token
        }
    }

@router.post("/login/verify-mfa", response_model=token_schema.Token)
def verify_mfa(
    *,
    db: Session = Depends(deps.get_public_db),
    mfa_request: MFAVerifyRequest
) -> Any:
    """
    Verify MFA token and OTP, then issue access token
    """
    try:
        # Verify the MFA token
        payload = jwt.decode(
            mfa_request.mfa_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA token",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA token",
        )
    
    # Get the user
    user = crud_user.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Verify the OTP
    if not user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not set up for this user",
        )
    
    totp = pyotp.TOTP(user.mfa_secret)
    if not totp.verify(mfa_request.otp):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP",
        )
    
    # Get user permissions and roles
    user_permissions = {perm.name for role in user.roles for perm in role.permissions}
    user_role_names = {role.name for role in user.roles}
    role = list(user_role_names)[0] if user_role_names else "PATIENT"
    
    # Create access token
    access_token = create_access_token(
        subject=user.email,
        claims={"role": role, "org_id": str(user.organization_id), "perms": list(user_permissions)},
        mfa_verified=True
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(subject=user.email)
    
    # Store refresh token in database
    crud_token.create_refresh_token(
        db=db,
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.now(timezone.utc) + settings.REFRESH_TOKEN_EXPIRE_TIMEDELTA
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

@router.post("/refresh-token", response_model=token_schema.Token)
def refresh_token(
    *,
    db: Session = Depends(deps.get_public_db),
    refresh_request: RefreshTokenRequest
) -> Any:
    """
    Refresh access token using refresh token
    """
    try:
        # Verify the refresh token
        payload = jwt.decode(
            refresh_request.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    # Get the user
    user = crud_user.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Verify the refresh token exists in the database
    token_record = crud_token.get_refresh_token(db, token=refresh_request.refresh_token)
    if not token_record or token_record.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    # Check if the token has expired
    if token_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )
    
    # Get user permissions and roles
    user_permissions = {perm.name for role in user.roles for perm in role.permissions}
    user_role_names = {role.name for role in user.roles}
    role = list(user_role_names)[0] if user_role_names else "PATIENT"
    
    # Create new access token
    access_token = create_access_token(
        subject=user.email,
        claims={"role": role, "org_id": str(user.organization_id), "perms": list(user_permissions)},
        mfa_enabled=user.mfa_enabled
    )
    
    # Create new refresh token
    new_refresh_token = create_refresh_token(subject=user.email)
    
    # Update refresh token in database
    crud_token.delete_refresh_token(db, token=refresh_request.refresh_token)
    crud_token.create_refresh_token(
        db=db,
        user_id=user.id,
        token=new_refresh_token,
        expires_at=datetime.now(timezone.utc) + settings.REFRESH_TOKEN_EXPIRE_TIMEDELTA
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token
    }

@router.post("/logout")
def logout(
    *,
    db: Session = Depends(deps.get_db),
    refresh_request: RefreshTokenRequest
) -> Any:
    """
    Logout user by invalidating refresh token
    """
    try:
        # Delete the refresh token from the database
        crud_token.delete_refresh_token(db, token=refresh_request.refresh_token)
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during logout: {str(e)}"
        )