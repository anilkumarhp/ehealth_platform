# tests/testing_session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# This is a critical fix: We create a truly synchronous URL by removing '+asyncpg'.
SYNC_DATABASE_URL = settings.DATABASE_URL.replace("+asyncpg", "") + "_test"

# Create a SYNCHRONOUS engine with the synchronous URL
engine_test = create_engine(SYNC_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)