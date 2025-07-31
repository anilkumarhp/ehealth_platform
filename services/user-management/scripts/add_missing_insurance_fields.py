"""
Script to add missing insurance fields to the patient_insurances table.
"""
import os
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_missing_insurance_fields():
    """Add missing fields to the patient_insurances table."""
    try:
        # Get database connection parameters from environment variables
        host = os.environ.get("POSTGRES_HOST", "localhost")
        port = os.environ.get("POSTGRES_PORT", "5432")
        user = os.environ.get("POSTGRES_USER", "postgres")
        password = os.environ.get("POSTGRES_PASSWORD", "postgres")
        dbname = os.environ.get("POSTGRES_DB", "ehealth_user_management")
        
        # Connect to the database
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Check if the patient_insurances table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'patient_insurances'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            logger.info("patient_insurances table doesn't exist, nothing to do")
            return True
        
        # List of fields to check and add if missing
        fields_to_check = [
            ("insurance_category", "VARCHAR(50)"),
            ("group_number", "VARCHAR(100)"),
            ("plan_type", "VARCHAR(100)"),
            ("effective_date", "VARCHAR(20)"),
            ("expiration_date", "VARCHAR(20)"),
            ("copay_amount", "VARCHAR(50)"),
            ("deductible_amount", "VARCHAR(50)"),
            ("policy_holder_name", "VARCHAR(200)"),
            ("relationship_to_policy_holder", "VARCHAR(50)")
        ]
        
        # Check each field and add if missing
        for field_name, field_type in fields_to_check:
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'patient_insurances' AND column_name = '{field_name}'
                );
            """)
            field_exists = cursor.fetchone()[0]
            
            if not field_exists:
                logger.info(f"Adding {field_name} column to patient_insurances table")
                cursor.execute(f"""
                    ALTER TABLE patient_insurances 
                    ADD COLUMN {field_name} {field_type};
                """)
        
        # Close cursor and connection
        cursor.close()
        conn.close()
        
        logger.info("Successfully added missing insurance fields")
        return True
    
    except Exception as e:
        logger.error(f"Error adding missing insurance fields: {str(e)}")
        return False

if __name__ == "__main__":
    add_missing_insurance_fields()