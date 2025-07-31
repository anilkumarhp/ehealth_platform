"""
Test fixtures and configuration
"""

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

from app.models.base import Base
from app.models.pharmacy import Pharmacy

# Create in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine():
    """Create a SQLAlchemy engine for testing."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def db_session(engine):
    """Create a SQLAlchemy session for testing."""
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def test_pharmacy(db_session):
    """Create a test pharmacy."""
    # Generate unique license and registration numbers
    unique_id = str(uuid4())[:8]
    license_number = f"TEST{unique_id}"
    registration_number = f"REG{unique_id}"
    
    pharmacy = Pharmacy(
        id=uuid4(),
        name="Test Pharmacy",
        license_number=license_number,
        registration_number=registration_number,
        email="test@pharmacy.com",
        phone="+1 123-456-7890",
        address_line1="123 Test Street",
        city="Test City",
        state="Test State",
        postal_code="12345",
        country="Test Country",
        owner_name="Test Owner",
        pharmacist_in_charge="Test Pharmacist",
        verification_status="verified",
        operational_status="active"
    )
    
    db_session.add(pharmacy)
    await db_session.commit()
    await db_session.refresh(pharmacy)
    
    return pharmacy