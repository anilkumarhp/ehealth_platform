from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import logging
import uuid

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

# Import all models
from app.db.base_class import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_database_if_not_exists():
    """Create the database and required tables if they don't exist."""
    try:
        # Connect to default postgres database to create our app database
        postgres_engine = create_engine(f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/postgres")
        
        with postgres_engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{settings.POSTGRES_DB}'"))
            if not result.fetchone():
                # Database doesn't exist, create it
                # Need to use a separate connection for CREATE DATABASE
                conn.execute(text("COMMIT"))  # Close current transaction
                conn.execute(text(f"CREATE DATABASE {settings.POSTGRES_DB}"))
                logger.info(f"Created database {settings.POSTGRES_DB}")
            else:
                logger.info(f"Database {settings.POSTGRES_DB} already exists")
    
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        return
    
    try:
        # Connect to our app database to create tables
        app_engine = create_engine(settings.DATABASE_URL)
        
        with app_engine.connect() as conn:
            # Create uuid-ossp extension
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
            conn.commit()
            
        # Create all tables defined in the models
        logger.info("Creating all tables from SQLAlchemy models")
        Base.metadata.create_all(bind=app_engine)
        logger.info("All tables created successfully")
        
        # Insert default organization if needed
        with app_engine.connect() as conn:
            # Insert Patients organization if it doesn't exist
            patients_org_id = uuid.UUID('11111111-1111-1111-1111-111111111111')
            result = conn.execute(text("SELECT 1 FROM organizations WHERE id = :id"), {"id": str(patients_org_id)})
            if not result.fetchone():
                # Create the default Patients organization
                conn.execute(
                    text("INSERT INTO organizations (id, name, is_active, subscription_tier, created_at, updated_at) VALUES (:id, :name, :is_active, :tier, NOW(), NOW())"),
                    {"id": str(patients_org_id), "name": "Patients", "is_active": True, "tier": "FREE"}
                )
                logger.info("Created Patients organization")
                
                # Create a default role for the Patients organization
                role_id = uuid.uuid4()
                conn.execute(
                    text("""DO $$ 
                    BEGIN 
                        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name=\'roles\' AND column_name=\'created_at\') THEN 
                            INSERT INTO roles (id, name, description, organization_id, created_at, updated_at) VALUES (:id, :name, :description, :org_id, NOW(), NOW()); 
                        ELSE 
                            INSERT INTO roles (id, name, description, organization_id) VALUES (:id, :name, :description, :org_id); 
                        END IF; 
                    END $$;"""),
                    {"id": str(role_id), "name": "Patient", "description": "Default role for patients", "org_id": str(patients_org_id)}
                )
                logger.info("Created default Patient role")
            else:
                logger.info("Patients organization already exists")
                
                # Check if the default role exists
                role_result = conn.execute(
                    text("SELECT 1 FROM roles WHERE organization_id = :org_id AND name = 'Patient'"),
                    {"org_id": str(patients_org_id)}
                )
                if not role_result.fetchone():
                    # Create the default role if it doesn't exist
                    role_id = uuid.uuid4()
                    conn.execute(
                        text("""DO $$ 
                    BEGIN 
                        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name=\'roles\' AND column_name=\'created_at\') THEN 
                            INSERT INTO roles (id, name, description, organization_id, created_at, updated_at) VALUES (:id, :name, :description, :org_id, NOW(), NOW()); 
                        ELSE 
                            INSERT INTO roles (id, name, description, organization_id) VALUES (:id, :name, :description, :org_id); 
                        END IF; 
                    END $$;"""),
                        {"id": str(role_id), "name": "Patient", "description": "Default role for patients", "org_id": str(patients_org_id)}
                    )
                    logger.info("Created default Patient role")
            
            conn.commit()
            logger.info("Database initialization complete")
    
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")


if __name__ == "__main__":
    logger.info("Initializing database...")
    create_database_if_not_exists()
    logger.info("Database initialization script completed")