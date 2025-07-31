"""
Script to add the refresh_tokens table directly using SQL.
"""
import os
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_refresh_tokens_table():
    """Add the refresh_tokens table directly using SQL."""
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
        
        # Check if the refresh_tokens table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'refresh_tokens'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            # Create the refresh_tokens table
            cursor.execute("""
                CREATE TABLE refresh_tokens (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL,
                    token TEXT NOT NULL,
                    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
                );
                CREATE INDEX ix_refresh_tokens_token ON refresh_tokens (token);
                CREATE INDEX ix_refresh_tokens_user_id ON refresh_tokens (user_id);
            """)
            logger.info("Created refresh_tokens table")
        else:
            logger.info("refresh_tokens table already exists")
        
        # Close cursor and connection
        cursor.close()
        conn.close()
        
        return True
    
    except Exception as e:
        logger.error(f"Error adding refresh_tokens table: {str(e)}")
        return False

if __name__ == "__main__":
    add_refresh_tokens_table()