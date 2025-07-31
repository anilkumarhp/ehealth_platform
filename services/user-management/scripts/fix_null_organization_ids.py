#!/usr/bin/env python
"""
Script to fix users with null organization_id by assigning them to the default Patients organization.
"""
import uuid
import logging
from sqlalchemy import create_engine, text
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_null_organization_ids():
    """Fix users with null organization_id by assigning them to the default Patients organization."""
    try:
        # Connect to the database
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Get the default Patients organization ID
            patients_org_id = uuid.UUID('11111111-1111-1111-1111-111111111111')
            
            # Check if the Patients organization exists
            result = conn.execute(text("SELECT 1 FROM organizations WHERE id = :id"), {"id": str(patients_org_id)})
            if not result.fetchone():
                # Create the Patients organization if it doesn't exist
                conn.execute(
                    text("INSERT INTO organizations (id, name, is_active, subscription_tier, created_at, updated_at) VALUES (:id, :name, :is_active, :tier, NOW(), NOW())"),
                    {"id": str(patients_org_id), "name": "Patients", "is_active": True, "tier": "FREE"}
                )
                logger.info("Created Patients organization")
                
                # Create a default role for the Patients organization
                role_id = uuid.uuid4()
                conn.execute(
                    text("INSERT INTO roles (id, name, description, organization_id, created_at, updated_at) VALUES (:id, :name, :description, :org_id, NOW(), NOW())"),
                    {"id": str(role_id), "name": "Patient", "description": "Default role for patients", "org_id": str(patients_org_id)}
                )
                logger.info("Created default Patient role")
            
            # Count users with null organization_id
            count_result = conn.execute(text("SELECT COUNT(*) FROM users WHERE organization_id IS NULL"))
            count = count_result.scalar()
            logger.info(f"Found {count} users with null organization_id")
            
            if count > 0:
                # Update users with null organization_id
                conn.execute(
                    text("UPDATE users SET organization_id = :org_id WHERE organization_id IS NULL"),
                    {"org_id": str(patients_org_id)}
                )
                logger.info(f"Updated {count} users with the default Patients organization ID")
            
            conn.commit()
            logger.info("Fix completed successfully")
    
    except Exception as e:
        logger.error(f"Error fixing null organization IDs: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting fix for null organization IDs...")
    fix_null_organization_ids()
    logger.info("Fix script completed")