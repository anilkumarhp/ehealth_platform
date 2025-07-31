"""
Script to directly add timestamp columns to the roles table using SQL.
"""
import os
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database():
    """Fix the database by adding timestamp columns and skipping table creation"""
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
        
        # Check if roles table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'roles'
            );
        """)
        roles_exist = cursor.fetchone()[0]
        
        if roles_exist:
            # Check if created_at column exists in roles table
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'roles' AND column_name = 'created_at'
                );
            """)
            created_at_exists = cursor.fetchone()[0]
            
            # Check if updated_at column exists in roles table
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'roles' AND column_name = 'updated_at'
                );
            """)
            updated_at_exists = cursor.fetchone()[0]
            
            # Add columns if they don't exist
            if not created_at_exists:
                logger.info("Adding created_at column to roles table")
                cursor.execute("""
                    ALTER TABLE roles 
                    ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL;
                """)
            
            if not updated_at_exists:
                logger.info("Adding updated_at column to roles table")
                cursor.execute("""
                    ALTER TABLE roles 
                    ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL;
                """)
                
            logger.info("Database fixed successfully")
        else:
            logger.info("Roles table doesn't exist yet, nothing to fix")
        
        # Close cursor and connection
        cursor.close()
        conn.close()
        
        return True
    
    except Exception as e:
        logger.error(f"Error fixing database: {str(e)}")
        return False

if __name__ == "__main__":
    fix_database()