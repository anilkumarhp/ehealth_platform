import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import SessionLocal
from app.db.models.organization import Organization
from app.api.v1.schemas.organization import OrganizationCreate
from app.crud.crud_organization import create_organization
import uuid

# Define a fixed UUID for the Patients organization
# This ensures it's always the same across all instances
PATIENTS_ORG_UUID = uuid.UUID('11111111-1111-1111-1111-111111111111')

def ensure_patients_organization_exists():
    """
    Ensures that a global 'Patients' organization exists in the database.
    This uses a fixed UUID to ensure consistency across all instances.
    """
    db = SessionLocal()
    try:
        # Check if the Patients organization already exists
        patients_org = db.query(Organization).filter(Organization.name == "Patients").first()
        
        if not patients_org:
            print("Creating global 'Patients' organization...")
            
            # Create the organization with the fixed UUID
            # First check if we can use direct SQL to insert with a specific UUID
            try:
                # Try direct SQL insert with the fixed UUID
                db.execute(
                    text("INSERT INTO organizations (id, name, is_active, subscription_tier, created_at, updated_at) "
                         "VALUES (:id, :name, :is_active, :subscription_tier, NOW(), NOW())"),
                    {
                        "id": PATIENTS_ORG_UUID,
                        "name": "Patients",
                        "is_active": True,
                        "subscription_tier": "FREE"
                    }
                )
                db.commit()
                patients_org = db.query(Organization).get(PATIENTS_ORG_UUID)
                print(f"Created 'Patients' organization with fixed ID: {patients_org.id}")
            except Exception as sql_error:
                print(f"Could not create organization with fixed UUID: {str(sql_error)}")
                # Fallback to regular creation (will generate a random UUID)
                org_schema = OrganizationCreate(name="Patients")
                patients_org = create_organization(db=db, organization=org_schema)
                db.commit()
                print(f"Created 'Patients' organization with generated ID: {patients_org.id}")
        else:
            print(f"'Patients' organization already exists with ID: {patients_org.id}")
            
        return patients_org.id
    except Exception as e:
        db.rollback()
        print(f"Error ensuring Patients organization exists: {str(e)}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    ensure_patients_organization_exists()