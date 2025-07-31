"""
Test configuration and fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient
from uuid import uuid4

from app.main import app
from app.models.base import BaseModel
from app.db.session import get_async_session
from app.models.pharmacy import Pharmacy
from app.models.medicine import Medicine
from app.models.staff import PharmacyStaff

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    def get_test_db():
        return db_session
    
    app.dependency_overrides[get_async_session] = get_test_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest.fixture
async def test_pharmacy(db_session: AsyncSession) -> Pharmacy:
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
        phone="+91 9876543210",
        address_line1="123 Test Street",
        city="Test City",
        state="Test State",
        postal_code="123456",
        country="India",
        owner_name="Test Owner",
        pharmacist_in_charge="Test Pharmacist",
        verification_status="verified",
        operational_status="active",
        delivery_radius_km=10.0,
        home_delivery_available=True
    )
    
    db_session.add(pharmacy)
    await db_session.commit()
    await db_session.refresh(pharmacy)
    return pharmacy