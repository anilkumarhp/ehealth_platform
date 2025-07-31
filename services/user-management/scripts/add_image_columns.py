"""
Script to add image URL columns directly to the users table
"""
import psycopg2
import os
from sqlalchemy import create_engine, text

def add_columns():
    """Add profile_photo_url and s3_bucket_name columns to users table"""
    # Get database connection parameters from environment variables
    host = os.environ.get("POSTGRES_HOST", "user-management-db")
    port = os.environ.get("POSTGRES_PORT", "5432")
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "postgres")
    dbname = os.environ.get("POSTGRES_DB", "ehealth_user_management")
    
    # Create SQLAlchemy engine
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")
    
    try:
        # Connect to the database
        with engine.connect() as connection:
            # Check if columns already exist
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN ('profile_photo_url', 's3_bucket_name')
            """))
            
            existing_columns = [row[0] for row in result]
            
            # Add columns if they don't exist
            if 'profile_photo_url' not in existing_columns:
                print("Adding profile_photo_url column...")
                connection.execute(text("ALTER TABLE users ADD COLUMN profile_photo_url VARCHAR(500)"))
            else:
                print("profile_photo_url column already exists")
                
            if 's3_bucket_name' not in existing_columns:
                print("Adding s3_bucket_name column...")
                connection.execute(text("ALTER TABLE users ADD COLUMN s3_bucket_name VARCHAR(255)"))
            else:
                print("s3_bucket_name column already exists")
                
            connection.commit()
            print("Columns added successfully!")
            
    except Exception as e:
        print(f"Error adding columns: {str(e)}")
        raise

if __name__ == "__main__":
    add_columns()