"""
Script to add created_at and updated_at columns to the roles table if they don't exist.
This is a fallback in case the migration doesn't run properly.
"""
import logging
import sys
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_timestamp_columns():
    """Add created_at and updated_at columns to roles table if they don't exist"""
    # Get database connection parameters from environment variables
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "postgres")
    dbname = os.environ.get("POSTGRES_DB", "ehealth_user_management")
    
    try:
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
        
        # Check if created_at column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='roles' AND column_name='created_at';
        """)
        created_at_exists = cursor.fetchone() is not None
        
        # Check if updated_at column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='roles' AND column_name='updated_at';
        """)
        updated_at_exists = cursor.fetchone() is not None
        
        # Add columns if they don't exist
        if not created_at_exists:
            logger.info("Adding created_at column to roles table")
            cursor.execute("""
                ALTER TABLE roles 
                ADD COLUMN created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
            """)
        
        if not updated_at_exists:
            logger.info("Adding updated_at column to roles table")
            cursor.execute("""
                ALTER TABLE roles 
                ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
            """)
        
        # Close cursor and connection
        cursor.close()
        conn.close()
        
        logger.info("Successfully added timestamp columns to roles table")
        return True
    
    except Exception as e:
        logger.error(f"Error adding timestamp columns to roles table: {str(e)}")
        return False

if __name__ == "__main__":
    success = add_timestamp_columns()
    sys.exit(0 if success else 1)