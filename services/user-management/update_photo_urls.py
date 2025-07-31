#!/usr/bin/env python3

import os
import sys
sys.path.append('/app')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = f"postgresql://postgres:postgres@user-management-db:5432/ehealth_user_management"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def update_photo_urls():
    db = SessionLocal()
    try:
        # Update profile_photo_url field
        result1 = db.execute(text("""
            UPDATE users 
            SET profile_photo_url = REPLACE(profile_photo_url, '/api/v1/files/secure/', '/files/public/')
            WHERE profile_photo_url LIKE '/api/v1/files/secure/%'
        """))
        
        db.commit()
        print(f"Updated {result1.rowcount} profile_photo_url records")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_photo_urls()