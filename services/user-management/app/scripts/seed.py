import asyncio
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import SessionLocal
from app.db import models
from app.core.config import settings
from app.scripts.ensure_patients_org import PATIENTS_ORG_UUID

# --- DEFINE ALL SYSTEM PERMISSIONS HERE ---
PERMISSIONS = {
    # Document Permissions
    "document:create": "Allow creating/uploading new documents.",
    "document:read_own": "Allow reading documents owned by the user.",
    "document:read_shared": "Allow reading documents shared via consent.",
    "document:delete": "Allow deleting a document.",

    # Connection Permissions
    "connection:create": "Allow sending new connection requests.",
    "connection:manage": "Allow approving/rejecting connection requests.",

    # Consent Permissions
    "consent:create": "Allow granting consent to others.",
    "consent:revoke": "Allow revoking consent given to others.",

    # User Management Permissions (Admin)
    "user:list": "Allow listing all users within the organization.",
    "user:invite": "Allow inviting new users to the organization.",
    "user:update_role": "Allow changing the roles of users in the organization.",

    # Role Management Permissions (Admin)
    "role:create": "Allow creating new roles.",
    "role:read": "Allow viewing roles and their permissions.",
    "role:update": "Allow updating roles and their permissions.",
    "role:delete": "Allow deleting custom roles.",
}

async def seed_permissions(db: Session):
    print("Seeding permissions...")
    for name, desc in PERMISSIONS.items():
        permission = db.query(models.Permission).filter(models.Permission.name == name).first()
        if not permission:
            db_permission = models.Permission(name=name, description=desc)
            db.add(db_permission)
            print(f"  - Created permission: {name}")
    db.commit()
    print("Permissions seeding complete.")

async def seed_patients_organization(db: Session):
    print("Checking for Patients organization...")
    patients_org = db.query(models.Organization).filter(models.Organization.name == "Patients").first()
    
    if not patients_org:
        print("Creating Patients organization with fixed UUID...")
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
            print(f"Created Patients organization with ID: {PATIENTS_ORG_UUID}")
        except Exception as e:
            db.rollback()
            print(f"Error creating Patients organization: {str(e)}")
    else:
        print(f"Patients organization already exists with ID: {patients_org.id}")

async def main():
    db = SessionLocal()
    try:
        await seed_permissions(db)
        await seed_patients_organization(db)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())