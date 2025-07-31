"""
Simplified version of init_db.py that doesn't try to create tables.
"""
import logging
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from app.core.config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def initialize_database():
    """Initialize the database without creating tables."""
    try:
        # Connect to the database
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if the Patients organization exists
            patients_org_id = uuid.UUID('11111111-1111-1111-1111-111111111111')
            result = conn.execute(text("SELECT 1 FROM organizations WHERE id = :id"), {"id": str(patients_org_id)})
            org_exists = result.fetchone() is not None
            
            if not org_exists:
                # Create the default Patients organization
                conn.execute(
                    text("INSERT INTO organizations (id, name, is_active, subscription_tier, created_at, updated_at) VALUES (:id, :name, :is_active, :tier, NOW(), NOW())"),
                    {"id": str(patients_org_id), "name": "Patients", "is_active": True, "tier": "FREE"}
                )
                logger.info("Created Patients organization")
            else:
                logger.info("Patients organization already exists")
            
            # Check if the default role exists
            role_result = conn.execute(
                text("SELECT 1 FROM roles WHERE organization_id = :org_id AND name = 'Patient'"),
                {"org_id": str(patients_org_id)}
            )
            role_exists = role_result.fetchone() is not None
            
            if not role_exists:
                # Check if the roles table has created_at and updated_at columns
                columns_result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'roles' AND column_name = 'created_at'
                    )
                """))
                has_timestamp_columns = columns_result.scalar()
                
                # Create the default role
                role_id = uuid.uuid4()
                if has_timestamp_columns:
                    conn.execute(
                        text("INSERT INTO roles (id, name, description, organization_id, created_at, updated_at) VALUES (:id, :name, :description, :org_id, NOW(), NOW())"),
                        {"id": str(role_id), "name": "Patient", "description": "Default role for patients", "org_id": str(patients_org_id)}
                    )
                else:
                    conn.execute(
                        text("INSERT INTO roles (id, name, description, organization_id) VALUES (:id, :name, :description, :org_id)"),
                        {"id": str(role_id), "name": "Patient", "description": "Default role for patients", "org_id": str(patients_org_id)}
                    )
                logger.info("Created default Patient role")
            else:
                logger.info("Default Patient role already exists")
            
            conn.commit()
            logger.info("Database initialization complete")
        
        return True
    
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Initializing database...")
    initialize_database()
    logger.info("Database initialization script completed")