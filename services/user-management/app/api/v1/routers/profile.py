from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Any, Optional
from pydantic import BaseModel
import os

from app.api.v1 import deps
from app.crud import crud_user
from app.db import models
from app.db.models import User
from app.integrations.s3_client import s3_client
from app.crud import crud_patient

router = APIRouter(prefix="/profile", tags=["User Profile"])

class InsuranceInfo(BaseModel):
    provider_name: Optional[str] = None
    policy_number: Optional[str] = None
    scheme_name: Optional[str] = None
    insurance_category: Optional[str] = None
    group_number: Optional[str] = None
    plan_type: Optional[str] = None
    effective_date: Optional[str] = None
    expiration_date: Optional[str] = None
    copay_amount: Optional[str] = None
    deductible_amount: Optional[str] = None
    policy_holder_name: Optional[str] = None
    relationship_to_policy_holder: Optional[str] = None
    document_url: Optional[str] = None  # For uploaded insurance documents

class ProfileUpdateRequest(BaseModel):
    # Personal information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None
    phone: Optional[str] = None
    aadhar_id: Optional[str] = None
    email: Optional[str] = None  # Allow email updates
    
    # Address fields
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    address_type: Optional[str] = None
    
    # MFA settings
    enable_mfa: Optional[bool] = None
    
    # Insurance information
    has_insurance: Optional[bool] = None
    insurance: Optional[list[InsuranceInfo]] = None
    
    # Profile photo
    photo: Optional[str] = None  # Base64 encoded photo

class ProfileResponse(BaseModel):
    message: str
    updated_fields: list[str]

@router.get("/me")
def get_my_profile(
    current_user: User = Depends(deps.get_current_user_from_db),
    db: Session = Depends(deps.get_public_db)
) -> Any:
    """Get the current user's profile information"""
    # Get patient profile with insurance information
    patient_info = {}
    insurance_info = []
    
    # Get phone number from patient record if available
    primary_phone = None
    
    if current_user.patient_profile:
        # Get patient data
        patient = db.query(models.Patient).filter(models.Patient.user_id == current_user.id).first()
        if patient:
            primary_phone = patient.primary_phone
            patient_info.update({
                "primary_phone": patient.primary_phone,
                "alternate_phone": patient.alternate_phone,
                "blood_group": patient.blood_group,
                "aadhaar_id": patient.aadhaar_id,
                "aadhaar_verified": patient.aadhaar_verified
            })
            
            # Get insurance information
            insurances = db.query(models.PatientInsurance).filter(
                models.PatientInsurance.patient_id == current_user.id
            ).all()
            
            for insurance in insurances:
                insurance_info.append({
                    "id": str(insurance.id),
                    "provider_name": insurance.provider_name,
                    "policy_number": insurance.policy_number,
                    "scheme_name": insurance.scheme_name,
                    "insurance_category": insurance.insurance_category,
                    "group_number": insurance.group_number,
                    "plan_type": insurance.plan_type,
                    "effective_date": insurance.effective_date,
                    "expiration_date": insurance.expiration_date,
                    "copay_amount": insurance.copay_amount,
                    "deductible_amount": insurance.deductible_amount,
                    "policy_holder_name": insurance.policy_holder_name,
                    "relationship_to_policy_holder": insurance.relationship_to_policy_holder,
                    "is_active": insurance.is_active,
                    "document_url": getattr(insurance, 'document_url', None)
                })
    
    # Organize data into tabs similar to registration page
    personal_info_dict = current_user.personal_info if current_user.personal_info else {}
    patient_info_dict = {k: v for k, v in patient_info.items() if k not in ["primary_phone", "insurance_info"]}
    
    # Generate presigned URL for profile photo if it exists
    profile_photo_url = current_user.profile_photo_url
    if profile_photo_url:
        try:
            # Clean up the S3 key - remove /files/public/ prefix if present
            s3_key = profile_photo_url
            if s3_key.startswith('/files/public/'):
                s3_key = s3_key.replace('/files/public/', '')
            
            # Generate presigned URL if it's not already a full URL
            if not s3_key.startswith(('http://', 'https://')):
                profile_photo_url = s3_client.generate_presigned_url(s3_key, expiration=3600)
        except Exception as e:
            print(f"Error generating presigned URL in /me endpoint: {str(e)}")
    
    return {
        "title": "My Profile",
        "id": str(current_user.id),
        "email": current_user.email,
        "primary_phone": patient_info.get("primary_phone"),
        "profile_photo_url": profile_photo_url,
        "organization_id": str(current_user.organization_id) if current_user.organization_id else None,
        "mfa_enabled": current_user.mfa_enabled,
        "roles": [role.name for role in current_user.roles],
        
        "tabs": [
            {
                "id": "personal",
                "title": "Personal Information",
                "fields": {
                    "first_name": personal_info_dict.get("first_name", ""),
                    "last_name": personal_info_dict.get("last_name", ""),
                    "display_name": personal_info_dict.get("display_name", ""),
                    "date_of_birth": personal_info_dict.get("date_of_birth", ""),
                    "gender": personal_info_dict.get("gender", ""),
                    "blood_group": personal_info_dict.get("blood_group", patient_info_dict.get("blood_group", "")),
                    "emergency_contact": personal_info_dict.get("emergency_contact", ""),
                    "aadhar_id": personal_info_dict.get("aadhar_id", patient_info_dict.get("aadhaar_id", ""))
                }
            },
            {
                "id": "address",
                "title": "Address Information",
                "fields": {
                    "street": personal_info_dict.get("address", {}).get("street", ""),
                    "city": personal_info_dict.get("address", {}).get("city", ""),
                    "state": personal_info_dict.get("address", {}).get("state", ""),
                    "zip_code": personal_info_dict.get("address", {}).get("zip_code", ""),
                    "country": personal_info_dict.get("address", {}).get("country", ""),
                    "address_type": personal_info_dict.get("address", {}).get("address_type", "")
                }
            },
            {
                "id": "account",
                "title": "Account Settings",
                "fields": {
                    "email": current_user.email,
                    "phone": primary_phone,
                    "enable_mfa": current_user.mfa_enabled
                }
            },
            {
                "id": "insurance",
                "title": "Insurance Information",
                "fields": {
                    "has_insurance": len(insurance_info) > 0,
                    "insurance": insurance_info
                }
            }
        ],
        
        # For backward compatibility
        "personal_info": {**personal_info_dict, **patient_info_dict},
        "address": current_user.personal_info.get("address", {}) if current_user.personal_info else {},
        "account_settings": {
            "mfa_enabled": current_user.mfa_enabled,
            "email": current_user.email,
            "primary_phone": patient_info.get("primary_phone")
        },
        "insurance_info": insurance_info,
        "has_insurance": len(insurance_info) > 0,
        "profile_data": current_user.profile_data
    }

@router.put("/me", response_model=ProfileResponse)
def update_my_profile(
    profile_data: ProfileUpdateRequest,
    db: Session = Depends(deps.get_public_db),
    current_user: models.User = Depends(deps.get_current_user_from_db)
) -> Any:
    """Update the current user's profile information"""
    # Convert the profile data to a dictionary
    updates = profile_data.model_dump(exclude_unset=True)
    updated_fields = []
    
    # Update personal_info
    personal_info = dict(current_user.personal_info) if current_user.personal_info else {}
    
    # Map fields to personal_info
    personal_info_fields = {
        "first_name": "first_name",
        "last_name": "last_name",
        "display_name": "display_name",
        "date_of_birth": "date_of_birth",
        "gender": "gender",
        "blood_group": "blood_group",
        "emergency_contact": "emergency_contact",
        "aadhar_id": "aadhar_id"
    }
    
    for field, db_field in personal_info_fields.items():
        if field in updates and updates[field] is not None:
            personal_info[db_field] = updates[field]
            updated_fields.append(field)
    
    # Handle address fields
    address_fields = ["street", "city", "state", "zip_code", "country", "address_type"]
    if any(field in updates for field in address_fields):
        address = personal_info.get("address", {})
        
        for field in address_fields:
            if field in updates and updates[field] is not None:
                address[field] = updates[field]
                updated_fields.append(f"address.{field}")
        
        personal_info["address"] = address
    
    # Update the user
    user_updates = {"personal_info": personal_info}
    
    # Update phone in patient record if provided
    if "phone" in updates and updates["phone"] is not None:
        # Update patient record if it exists
        patient = db.query(models.Patient).filter(models.Patient.user_id == current_user.id).first()
        if patient:
            patient.primary_phone = updates["phone"]
            db.add(patient)
            updated_fields.append("phone")
        else:
            # Create patient record if it doesn't exist
            patient_data = {
                "primary_phone": updates["phone"],
                "user_id": current_user.id
            }
            new_patient = models.Patient(**patient_data)
            db.add(new_patient)
            updated_fields.append("phone")
    
    # Update email if provided (requires verification in a production system)
    if "email" in updates and updates["email"] is not None and updates["email"] != current_user.email:
        # In a real system, you would send a verification email before changing this
        user_updates["email"] = updates["email"]
        updated_fields.append("email")
    
    # Update MFA settings if provided
    if "enable_mfa" in updates:
        if updates["enable_mfa"] is False and current_user.mfa_enabled:
            # Disable MFA
            user_updates["mfa_enabled"] = False
            user_updates["mfa_secret"] = None
            updated_fields.append("mfa_disabled")
        elif updates["enable_mfa"] is True and not current_user.mfa_enabled:
            # MFA enabling requires a separate flow with QR code and verification
            # Just note that it was requested
            updated_fields.append("mfa_requested")
    
    # Handle profile photo if provided
    if "photo" in updates and updates["photo"]:
        try:
            # Use existing bucket if available, otherwise create a new one
            user_bucket = current_user.s3_bucket_name
            if not user_bucket:
                user_name = f"{personal_info.get('first_name', '')}-{personal_info.get('last_name', '')}"
                if not user_name.strip('-'):
                    user_name = current_user.email.split('@')[0]
                
                user_bucket = s3_client.create_user_bucket(str(current_user.id), user_name)
                user_updates["s3_bucket_name"] = user_bucket
            
            # Upload to S3 if configured
            if os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
                photo_url = s3_client.upload_base64_image(
                    base64_data=updates["photo"],
                    user_bucket=user_bucket,
                    file_type="profile_photo"
                )
                
                user_updates["profile_photo_url"] = photo_url
                updated_fields.append("profile_photo")
        except Exception as e:
            print(f"Failed to upload profile photo: {str(e)}")
    
    # Apply user updates
    crud_user.update_user(db=db, user=current_user, updates=user_updates)
    
    # Handle insurance updates if provided
    if "has_insurance" in updates or "insurance" in updates:
        has_insurance = updates.get("has_insurance", False)
        insurance_data = updates.get("insurance", [])
        
        # Get existing patient or create one if it doesn't exist
        patient = db.query(models.Patient).filter(models.Patient.user_id == current_user.id).first()
        if not patient and has_insurance:
            # Create patient record if it doesn't exist
            patient_data = {
                "primary_phone": updates.get("phone"),
                "blood_group": personal_info.get("blood_group"),
                "aadhaar_id": personal_info.get("aadhar_id")
            }
            patient = models.Patient(user_id=current_user.id, **{k: v for k, v in patient_data.items() if v is not None})
            db.add(patient)
            db.flush()
            updated_fields.append("patient_profile_created")
        
        if patient and has_insurance and insurance_data:
            # Process insurance records
            for insurance in insurance_data:
                insurance_dict = {}
                if isinstance(insurance, dict):
                    insurance_dict = insurance
                else:
                    try:
                        insurance_dict = insurance.model_dump()
                    except AttributeError:
                        try:
                            insurance_dict = insurance.__dict__
                        except:
                            # If all else fails, try to extract attributes directly
                            for attr in ["provider_name", "policy_number", "scheme_name", "insurance_category", 
                                        "group_number", "plan_type", "effective_date", "expiration_date", 
                                        "copay_amount", "deductible_amount", "policy_holder_name", 
                                        "relationship_to_policy_holder"]:
                                if hasattr(insurance, attr):
                                    insurance_dict[attr] = getattr(insurance, attr)
                
                if not insurance_dict.get("policy_number"):
                    continue  # Skip records without policy number
                
                # Check if this insurance already exists
                existing_insurance = db.query(models.PatientInsurance).filter(
                    models.PatientInsurance.patient_id == current_user.id,
                    models.PatientInsurance.policy_number == insurance_dict["policy_number"]
                ).first()
                
                if existing_insurance:
                    # Update existing insurance
                    for key, value in insurance_dict.items():
                        if value is not None:
                            setattr(existing_insurance, key, value)
                    db.add(existing_insurance)
                    updated_fields.append(f"insurance.{insurance_dict['policy_number']}.updated")
                else:
                    # Create new insurance
                    new_insurance = models.PatientInsurance(
                        patient_id=current_user.id,
                        **{k: v for k, v in insurance_dict.items() if v is not None}
                    )
                    db.add(new_insurance)
                    updated_fields.append(f"insurance.{insurance_dict['policy_number']}.added")
            
            # If has_insurance is False, deactivate all insurance records
        elif patient and not has_insurance:
            insurances = db.query(models.PatientInsurance).filter(
                models.PatientInsurance.patient_id == current_user.id
            ).all()
            
            for insurance in insurances:
                insurance.is_active = False
                db.add(insurance)
                updated_fields.append(f"insurance.{insurance.policy_number}.deactivated")
        
        db.commit()
    
    return {
        "message": "Profile updated successfully",
        "updated_fields": updated_fields
    }

@router.post("/me/photo")
async def update_profile_photo(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_public_db),
    current_user: User = Depends(deps.get_current_user_from_db)
) -> Any:
    """Update the current user's profile photo"""
    try:
        # First save locally as a fallback
        import os
        import shutil
        from datetime import datetime
        
        # Configure upload directory
        UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/uploads")
        os.makedirs(os.path.join(UPLOAD_DIR, "profile_photo"), exist_ok=True)
        
        # Generate unique filename
        file_id = str(current_user.id)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{file_id}_{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, "profile_photo", filename)
        
        # Save the file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Generate local URL
        local_url = f"/api/v1/files/profile_photo/{filename}"
        
        # Try to upload to S3 if configured
        s3_url = None
        if os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
            try:
                # Use existing bucket if available, otherwise create a new one
                user_bucket = current_user.s3_bucket_name
                if not user_bucket:
                    personal_info = current_user.personal_info or {}
                    user_name = f"{personal_info.get('first_name', '')}-{personal_info.get('last_name', '')}"
                    if not user_name.strip('-'):
                        user_name = current_user.email.split('@')[0]
                    
                    user_bucket = s3_client.create_user_bucket(str(current_user.id), user_name)
                    
                    # Save the bucket name to the user record
                    current_user.s3_bucket_name = user_bucket
                    db.add(current_user)
                    db.flush()
                
                # Reset file pointer
                file.file.seek(0)
                
                # Upload to S3
                s3_url = s3_client.upload_file_object(
                    file.file, 
                    user_bucket, 
                    "profile_photo", 
                    file.filename
                )
            except Exception as s3_error:
                print(f"S3 upload failed: {str(s3_error)}")
        
        # Update user profile with the photo URL (prefer S3 if available)
        final_url = s3_url or local_url
        user_bucket = current_user.s3_bucket_name or (user_bucket if 'user_bucket' in locals() else None)
        
        # Save the bucket name if it was created but not saved
        if user_bucket and not current_user.s3_bucket_name:
            current_user.s3_bucket_name = user_bucket
            db.add(current_user)
            db.flush()
        
        crud_user.update_user_profile_photo(
            db=db, 
            user=current_user, 
            photo_url=final_url,
            s3_bucket=user_bucket
        )
        
        return {
            "message": "Profile photo updated successfully",
            "photo_url": final_url,
            "s3_url": s3_url
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile photo: {str(e)}"
        )

class Base64PhotoRequest(BaseModel):
    photo: str
    
@router.post("/me/photo/base64")
def update_profile_photo_base64(
    photo_data: Base64PhotoRequest,
    db: Session = Depends(deps.get_public_db),
    current_user: User = Depends(deps.get_current_user_from_db)
) -> Any:
    """Update the current user's profile photo using base64 encoded image"""
    try:
        print(f"Starting base64 photo upload for user {current_user.id}")
        
        # Try to upload to S3 if configured
        s3_url = None
        if os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
            try:
                print("AWS credentials found, proceeding with S3 upload")
                
                # Use existing bucket if available, otherwise create a new one
                user_bucket = current_user.s3_bucket_name
                if not user_bucket:
                    personal_info = current_user.personal_info or {}
                    user_name = f"{personal_info.get('first_name', '')}-{personal_info.get('last_name', '')}"
                    if not user_name.strip('-'):
                        user_name = current_user.email.split('@')[0]
                    
                    print(f"Creating user bucket for {user_name}")
                    user_bucket = s3_client.create_user_bucket(str(current_user.id), user_name)
                    
                    # Save the bucket name to the user record
                    current_user.s3_bucket_name = user_bucket
                    db.add(current_user)
                    db.flush()
                    print(f"User bucket created: {user_bucket}")
                
                print(f"Uploading to S3 bucket: {user_bucket}")
                # Upload to S3 and get S3 key
                s3_key = s3_client.upload_base64_image(
                    base64_data=photo_data.photo,
                    user_bucket=user_bucket,
                    file_type="profile_photo"
                )
                print(f"S3 upload successful: {s3_key}")
                
                # Generate presigned URL for immediate use
                presigned_url = s3_client.generate_presigned_url(s3_key, expiration=86400)  # 24 hours
                
                # Update user profile with the S3 key (not the presigned URL)
                print(f"Updating user profile with S3 key: {s3_key}")
                print(f"User bucket: {user_bucket}")
                print(f"Current user ID: {current_user.id}")
                
                updated_user = crud_user.update_user_profile_photo(
                    db=db, 
                    user=current_user, 
                    photo_url=s3_key,  # Store S3 key, not presigned URL
                    s3_bucket=user_bucket
                )
                print(f"Profile photo updated in database. S3 key: {updated_user.profile_photo_url}")
                print(f"Profile data: {updated_user.profile_data}")
                
                return {
                    "message": "Profile photo updated successfully",
                    "photo_url": presigned_url  # Return presigned URL for immediate display
                }
            except Exception as s3_error:
                import traceback
                print(f"S3 upload error: {str(s3_error)}")
                print(f"S3 error traceback: {traceback.format_exc()}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"S3 upload failed: {str(s3_error)}"
                )
        else:
            print("AWS credentials not configured")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="S3 storage not configured. Cannot upload base64 images without S3."
            )
    except Exception as e:
        import traceback
        print(f"General error in base64 photo upload: {str(e)}")
        print(f"General error traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile photo: {str(e)}"
        )

@router.get("/me/tabs")
def get_profile_tabs(
    current_user: User = Depends(deps.get_current_user_from_db),
    db: Session = Depends(deps.get_public_db)
) -> Any:
    """Get the profile tabs structure similar to registration page"""
    # Get patient profile with insurance information
    patient_info = {}
    insurance_info = []
    
    # Get phone number
    primary_phone = None
    
    if current_user.patient_profile:
        # Get patient data
        patient = db.query(models.Patient).filter(models.Patient.user_id == current_user.id).first()
        if patient:
            primary_phone = patient.primary_phone
            patient_info = {
                "blood_group": patient.blood_group,
                "aadhaar_id": patient.aadhaar_id,
                "aadhaar_verified": patient.aadhaar_verified
            }
            
            # Get insurance information
            insurances = db.query(models.PatientInsurance).filter(
                models.PatientInsurance.patient_id == current_user.id
            ).all()
            
            for insurance in insurances:
                if insurance.is_active:
                    insurance_info.append({
                        "id": str(insurance.id),
                        "provider_name": insurance.provider_name,
                        "policy_number": insurance.policy_number,
                        "scheme_name": insurance.scheme_name,
                        "insurance_category": insurance.insurance_category,
                        "group_number": insurance.group_number,
                        "plan_type": insurance.plan_type,
                        "effective_date": insurance.effective_date,
                        "expiration_date": insurance.expiration_date,
                        "copay_amount": insurance.copay_amount,
                        "deductible_amount": insurance.deductible_amount,
                        "policy_holder_name": insurance.policy_holder_name,
                        "relationship_to_policy_holder": insurance.relationship_to_policy_holder
                    })
    
    # Extract personal info
    personal_info = current_user.personal_info or {}
    address = personal_info.get("address", {})
    
    return {
        "title": "My Profile",
        "tabs": [
            {
                "id": "personal",
                "title": "Personal Information",
                "fields": {
                    "first_name": personal_info.get("first_name", ""),
                    "last_name": personal_info.get("last_name", ""),
                    "display_name": personal_info.get("display_name", ""),
                    "date_of_birth": personal_info.get("date_of_birth", ""),
                    "gender": personal_info.get("gender", ""),
                    "blood_group": personal_info.get("blood_group", patient_info.get("blood_group", "")),
                    "emergency_contact": personal_info.get("emergency_contact", ""),
                    "aadhar_id": personal_info.get("aadhar_id", patient_info.get("aadhaar_id", ""))
                }
            },
            {
                "id": "address",
                "title": "Address Information",
                "fields": {
                    "street": address.get("street", ""),
                    "city": address.get("city", ""),
                    "state": address.get("state", ""),
                    "zip_code": address.get("zip_code", ""),
                    "country": address.get("country", ""),
                    "address_type": address.get("address_type", "")
                }
            },
            {
                "id": "account",
                "title": "Account Settings",
                "fields": {
                    "email": current_user.email,
                    "phone": primary_phone,
                    "enable_mfa": current_user.mfa_enabled
                }
            },
            {
                "id": "insurance",
                "title": "Insurance Information",
                "fields": {
                    "has_insurance": len(insurance_info) > 0,
                    "insurance": insurance_info
                }
            }
        ],
        "profile_photo_url": current_user.profile_photo_url
    }
@router.get("/me/profile-tabs")
def get_profile_tabs_v2(
    current_user: User = Depends(deps.get_current_user_from_db),
    db: Session = Depends(deps.get_public_db)
) -> Any:
    """Get the profile tabs structure for the frontend"""
    # Get patient profile with insurance information
    patient_info = {}
    insurance_info = []
    
    # Get phone number
    primary_phone = None
    
    if current_user.patient_profile:
        # Get patient data
        patient = db.query(models.Patient).filter(models.Patient.user_id == current_user.id).first()
        if patient:
            primary_phone = patient.primary_phone
            patient_info = {
                "blood_group": patient.blood_group,
                "aadhaar_id": patient.aadhaar_id,
                "aadhaar_verified": patient.aadhaar_verified
            }
            
            # Get insurance information
            insurances = db.query(models.PatientInsurance).filter(
                models.PatientInsurance.patient_id == current_user.id
            ).all()
            
            for insurance in insurances:
                if insurance.is_active:
                    insurance_info.append({
                        "id": str(insurance.id),
                        "provider_name": insurance.provider_name,
                        "policy_number": insurance.policy_number,
                        "scheme_name": insurance.scheme_name,
                        "insurance_category": insurance.insurance_category,
                        "group_number": insurance.group_number,
                        "plan_type": insurance.plan_type,
                        "effective_date": insurance.effective_date,
                        "expiration_date": insurance.expiration_date,
                        "copay_amount": insurance.copay_amount,
                        "deductible_amount": insurance.deductible_amount,
                        "policy_holder_name": insurance.policy_holder_name,
                        "relationship_to_policy_holder": insurance.relationship_to_policy_holder
                    })
    
    # Extract personal info
    personal_info = current_user.personal_info or {}
    address = personal_info.get("address", {})
    
    # Create a response with exactly 4 tabs and "My Profile" title
    return {
        "title": "My Profile",
        "tabs": [
            {
                "id": "personal",
                "title": "Personal Information",
                "fields": {
                    "first_name": personal_info.get("first_name", ""),
                    "last_name": personal_info.get("last_name", ""),
                    "display_name": personal_info.get("display_name", ""),
                    "date_of_birth": personal_info.get("date_of_birth", ""),
                    "gender": personal_info.get("gender", ""),
                    "blood_group": personal_info.get("blood_group", patient_info.get("blood_group", "")),
                    "emergency_contact": personal_info.get("emergency_contact", ""),
                    "aadhar_id": personal_info.get("aadhar_id", patient_info.get("aadhaar_id", ""))
                }
            },
            {
                "id": "address",
                "title": "Address Information",
                "fields": {
                    "street": address.get("street", ""),
                    "city": address.get("city", ""),
                    "state": address.get("state", ""),
                    "zip_code": address.get("zip_code", ""),
                    "country": address.get("country", ""),
                    "address_type": address.get("address_type", "")
                }
            },
            {
                "id": "account",
                "title": "Account Settings",
                "fields": {
                    "email": current_user.email,
                    "phone": primary_phone,
                    "enable_mfa": current_user.mfa_enabled
                }
            },
            {
                "id": "insurance",
                "title": "Insurance Information",
                "fields": {
                    "has_insurance": len(insurance_info) > 0,
                    "insurance": insurance_info
                }
            }
        ],
        "profile_photo_url": current_user.profile_photo_url
    }

@router.get("/me/photo-url")
def get_profile_photo_url(
    current_user: User = Depends(deps.get_current_user_from_db),
    db: Session = Depends(deps.get_public_db)
) -> Any:
    """Get presigned URL for user's profile photo"""
    if not current_user.profile_photo_url:
        return {"photo_url": None}
    
    # If it's already a full URL, return as is
    if current_user.profile_photo_url.startswith(('http://', 'https://')):
        return {"photo_url": current_user.profile_photo_url}
    
    # Clean up the S3 key - remove /files/public/ prefix if present
    s3_key = current_user.profile_photo_url
    if s3_key.startswith('/files/public/'):
        s3_key = s3_key.replace('/files/public/', '')
    
    # If it's an S3 key, generate presigned URL
    try:
        presigned_url = s3_client.generate_presigned_url(
            s3_key, 
            expiration=3600  # 1 hour
        )
        return {"photo_url": presigned_url}
    except Exception as e:
        print(f"Error generating presigned URL: {str(e)}")
        return {"photo_url": None}

@router.post("/me/insurance/document")
async def upload_insurance_document(
    file: UploadFile = File(...),
    policy_number: str = Form(...),
    db: Session = Depends(deps.get_public_db),
    current_user: User = Depends(deps.get_current_user_from_db)
) -> Any:
    """Upload insurance document"""
    try:
        # Get user bucket
        user_bucket = current_user.s3_bucket_name
        if not user_bucket:
            personal_info = current_user.personal_info or {}
            user_name = f"{personal_info.get('first_name', '')}-{personal_info.get('last_name', '')}"
            if not user_name.strip('-'):
                user_name = current_user.email.split('@')[0]
            user_bucket = s3_client.create_user_bucket(str(current_user.id), user_name)
            current_user.s3_bucket_name = user_bucket
            db.add(current_user)
            db.flush()
        
        # Upload document to S3
        document_url = s3_client.upload_file_object(
            file.file,
            user_bucket,
            "insurance_documents",
            file.filename
        )
        
        # Update insurance record with document URL
        insurance = db.query(models.PatientInsurance).filter(
            models.PatientInsurance.patient_id == current_user.id,
            models.PatientInsurance.policy_number == policy_number
        ).first()
        
        if insurance:
            insurance.document_url = document_url
            db.add(insurance)
            db.commit()
            print(f"Updated insurance {policy_number} with document URL: {document_url}")
        else:
            print(f"Insurance record not found for policy number: {policy_number}")
            # Create a basic insurance record if it doesn't exist
            try:
                new_insurance = models.PatientInsurance(
                    patient_id=current_user.id,
                    policy_number=policy_number,
                    document_url=document_url,
                    is_active=True
                )
                db.add(new_insurance)
                db.commit()
                print(f"Created new insurance record with policy number: {policy_number}")
            except Exception as create_error:
                print(f"Failed to create insurance record: {str(create_error)}")
        
        return {
            "message": "Insurance document uploaded successfully",
            "document_url": document_url,
            "policy_number": policy_number,
            "updated_record": insurance is not None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload insurance document: {str(e)}"
        )

@router.get("/dropdown-options")
def get_dropdown_options() -> Any:
    """Get dropdown options for profile forms"""
    return {
        "gender_options": [
            {"value": "male", "label": "Male"},
            {"value": "female", "label": "Female"},
            {"value": "other", "label": "Other"}
        ],
        "blood_group_options": [
            {"value": "A+", "label": "A+"},
            {"value": "A-", "label": "A-"},
            {"value": "B+", "label": "B+"},
            {"value": "B-", "label": "B-"},
            {"value": "AB+", "label": "AB+"},
            {"value": "AB-", "label": "AB-"},
            {"value": "O+", "label": "O+"},
            {"value": "O-", "label": "O-"}
        ],
        "insurance_category_options": [
            {"value": "private", "label": "Private Insurance"},
            {"value": "government", "label": "Government Scheme"}
        ],
        "plan_type_options": [
            {"value": "individual", "label": "Individual"},
            {"value": "family", "label": "Family"},
            {"value": "group", "label": "Group"},
            {"value": "employer", "label": "Employer Sponsored"}
        ],
        "relationship_options": [
            {"value": "self", "label": "Self"},
            {"value": "spouse", "label": "Spouse"},
            {"value": "child", "label": "Child"},
            {"value": "parent", "label": "Parent"},
            {"value": "sibling", "label": "Sibling"},
            {"value": "other", "label": "Other"}
        ],
        "field_configurations": {
            "insurance": {
                "document_upload": {
                    "enabled": True,
                    "field_name": "document_url",
                    "label": "Insurance Document",
                    "accept_types": ".pdf,.jpg,.jpeg,.png,.doc,.docx",
                    "max_size_mb": 10,
                    "upload_endpoint": "/api/v1/profile/me/insurance/document"
                }
            }
        }
    }

@router.get("/profile-tabs")
def get_frontend_profile_tabs(
    current_user: User = Depends(deps.get_current_user_from_db),
    db: Session = Depends(deps.get_public_db)
) -> Any:
    """Get the profile tabs structure for the frontend"""
    # Get patient profile with insurance information
    patient_info = {}
    insurance_info = []
    
    # Get phone number
    primary_phone = None
    
    if current_user.patient_profile:
        # Get patient data
        patient = db.query(models.Patient).filter(models.Patient.user_id == current_user.id).first()
        if patient:
            primary_phone = patient.primary_phone
            patient_info = {
                "blood_group": patient.blood_group,
                "aadhaar_id": patient.aadhaar_id,
                "aadhaar_verified": patient.aadhaar_verified
            }
            
            # Get insurance information
            insurances = db.query(models.PatientInsurance).filter(
                models.PatientInsurance.patient_id == current_user.id
            ).all()
            
            for insurance in insurances:
                if insurance.is_active:
                    insurance_info.append({
                        "id": str(insurance.id),
                        "provider_name": insurance.provider_name,
                        "policy_number": insurance.policy_number,
                        "scheme_name": insurance.scheme_name,
                        "insurance_category": insurance.insurance_category,
                        "group_number": insurance.group_number,
                        "plan_type": insurance.plan_type,
                        "effective_date": insurance.effective_date,
                        "expiration_date": insurance.expiration_date,
                        "copay_amount": insurance.copay_amount,
                        "deductible_amount": insurance.deductible_amount,
                        "policy_holder_name": insurance.policy_holder_name,
                        "relationship_to_policy_holder": insurance.relationship_to_policy_holder
                    })
    
    # Extract personal info
    personal_info = current_user.personal_info or {}
    address = personal_info.get("address", {})
    
    # Create a response with exactly 4 tabs and "My Profile" title
    return {
        "title": "My Profile",
        "tabs": [
            {
                "id": "personal",
                "title": "Personal Information",
                "fields": {
                    "first_name": personal_info.get("first_name", ""),
                    "last_name": personal_info.get("last_name", ""),
                    "display_name": personal_info.get("display_name", ""),
                    "date_of_birth": personal_info.get("date_of_birth", ""),
                    "gender": personal_info.get("gender", ""),
                    "blood_group": personal_info.get("blood_group", patient_info.get("blood_group", "")),
                    "emergency_contact": personal_info.get("emergency_contact", ""),
                    "aadhar_id": personal_info.get("aadhar_id", patient_info.get("aadhaar_id", ""))
                }
            },
            {
                "id": "address",
                "title": "Address Information",
                "fields": {
                    "street": address.get("street", ""),
                    "city": address.get("city", ""),
                    "state": address.get("state", ""),
                    "zip_code": address.get("zip_code", ""),
                    "country": address.get("country", ""),
                    "address_type": address.get("address_type", "")
                }
            },
            {
                "id": "account",
                "title": "Account Settings",
                "fields": {
                    "email": current_user.email,
                    "phone": primary_phone,
                    "enable_mfa": current_user.mfa_enabled
                }
            },
            {
                "id": "insurance",
                "title": "Insurance Information",
                "fields": {
                    "has_insurance": len(insurance_info) > 0,
                    "insurance": insurance_info
                }
            }
        ],
        "profile_photo_url": current_user.profile_photo_url
    }