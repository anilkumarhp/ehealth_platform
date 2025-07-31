import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.organization import Organization
from app.db.models.user import User
from app.scripts.ensure_patients_org import ensure_patients_organization_exists

def fix_null_organization_ids():
    """
    Fixes any existing users with null organization_id by assigning them to the Patients organization.
    """
    db = SessionLocal()
    try:
        # First ensure the Patients organization exists
        patients_org_id = ensure_patients_organization_exists()
        
        if not patients_org_id:
            print("Failed to get or create Patients organization. Aborting.")
            return
            
        # Find users with null organization_id
        users_with_null_org = db.query(User).filter(User.organization_id.is_(None)).all()
        
        if not users_with_null_org:
            print("No users found with null organization_id. Nothing to fix.")
            return
            
        print(f"Found {len(users_with_null_org)} users with null organization_id.")
        
        # Update each user
        for user in users_with_null_org:
            user.organization_id = patients_org_id
            print(f"Updating user {user.email} with organization_id: {patients_org_id}")
            
        # Commit the changes
        db.commit()
        print(f"Successfully updated {len(users_with_null_org)} users.")
        
    except Exception as e:
        db.rollback()
        print(f"Error fixing null organization IDs: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_null_organization_ids()