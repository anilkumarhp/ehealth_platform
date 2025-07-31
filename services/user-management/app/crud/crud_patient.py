import uuid
from sqlalchemy.orm import Session

from app.db import models
from app.api.v1.schemas import patient as patient_schema
from typing import Dict, Any

def create_patient(db: Session, patient_in: patient_schema.PatientCreate, user_id: uuid.UUID) -> models.User:
    """
    Creates insurance information for a user (patient data is now in User model).
    """
    # Get the user
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Add insurance information if provided
    if patient_in.insurance_info and len(patient_in.insurance_info) > 0:
        print(f"Creating {len(patient_in.insurance_info)} insurance records for user")
        for insurance_data in patient_in.insurance_info:
            # Ensure policy_number is present
            policy_number = insurance_data.get('policy_number')
            if not policy_number:
                print(f"Skipping insurance record without policy number")
                continue  # Skip this insurance record if no policy number
                
            db_insurance = models.PatientInsurance(
                user_id=user_id,  # Link directly to user
                provider_name=insurance_data.get('provider_name'),
                policy_number=policy_number,
                scheme_name=insurance_data.get('scheme_name') or insurance_data.get('type'),  # Try both fields
                insurance_category=insurance_data.get('insurance_category') or insurance_data.get('category'),
                group_number=insurance_data.get('group_number'),
                plan_type=insurance_data.get('plan_type'),
                effective_date=insurance_data.get('effective_date'),
                expiration_date=insurance_data.get('expiration_date'),
                copay_amount=str(insurance_data.get('copay_amount')) if insurance_data.get('copay_amount') is not None else None,
                deductible_amount=str(insurance_data.get('deductible_amount')) if insurance_data.get('deductible_amount') is not None else None,
                policy_holder_name=insurance_data.get('policy_holder_name'),
                relationship_to_policy_holder=insurance_data.get('relationship_to_policy_holder')
            )
            db.add(db_insurance)
            print(f"Added insurance record with policy number {policy_number}")
    else:
        print("No insurance information provided for user")
    
    # The commit is handled in the endpoint to ensure all creations succeed or fail together.
    return user


def update_patient(db: Session, user: models.User, updates: Dict[str, Any]) -> models.User:
    """
    Updates a user's profile (patient data is now in User model).
    """
    for key, value in updates.items():
        setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user