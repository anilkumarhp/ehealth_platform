# tests/testing_session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Use the same test database URL
TEST_DATABASE_URL = f"{settings.DATABASE_URL}_test"

# Create a SYNCHRONOUS engine
engine_test = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)