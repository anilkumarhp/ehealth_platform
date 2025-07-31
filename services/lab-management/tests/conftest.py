import pytest
import asyncio
from datetime import timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

from app.main import app
from app.db.base import BaseModel
# Import all models to ensure proper SQLAlchemy initialization
from app.models.lab_service import LabService
from app.models.test_definition import TestDefinition
from app.models.test_order import TestOrder
from app.models.appointment import Appointment
from app.models.lab_configuration import LabConfiguration
from app.models.test_duration import TestDuration
from app.core.security import TokenPayload
from app.api.deps import get_current_user
from app.db.session import get_db_session
import pytest_asyncio


# Test database URL - use PostgreSQL from Docker
from app.core.config import settings
TEST_DATABASE_URL = settings.DATABASE_URL


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    
    yield engine
    
    # Clean up
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session():
    """Create a real test database session using PostgreSQL."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from app.db.base import BaseModel
    from app.core.config import settings
    
    # Use the same PostgreSQL database as the app
    test_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False
    )
    
    # Create all tables if they don't exist
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    
    # Create session
    TestSessionLocal = async_sessionmaker(
        bind=test_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
    
    await test_engine.dispose()


# Shared IDs for consistent authorization
SHARED_LAB_ID = uuid4()
SHARED_USER_ID = uuid4()

@pytest.fixture
def mock_current_user():
    """Create a mock current user for testing."""
    return TokenPayload(
        sub=SHARED_USER_ID,
        full_name="Test User",
        date_of_birth="1990-01-01",
        gender="M",
        primary_mobile_number="+1234567890",
        email="test@example.com",
        roles=["patient", "lab-admin"],
        org_id=SHARED_LAB_ID,  # Use shared lab ID for authorization
        national_health_id="TEST123456",
        address="123 Test Street"
    )

@pytest.fixture
def shared_lab_id():
    """Provide the shared lab ID for tests."""
    return SHARED_LAB_ID

@pytest.fixture
def mock_user_id():
    """Provide the mock user's ID for tests."""
    return SHARED_USER_ID


@pytest_asyncio.fixture
async def client(mock_current_user):
    """Create test client with dependency overrides."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from app.db.base import BaseModel
    from app.core.config import settings
    
    # Create test database engine for concurrent access
    test_engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    # Create session factory for concurrent requests
    TestSessionLocal = async_sessionmaker(
        bind=test_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    # Override dependencies to create new session for each request
    async def get_test_db():
        async with TestSessionLocal() as session:
            try:
                yield session
            finally:
                await session.rollback()
    
    app.dependency_overrides[get_db_session] = get_test_db
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    
    # Create client
    async with AsyncClient(app=app, base_url="http://testserver") as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()
    await test_engine.dispose()


@pytest.fixture
def sample_lab_id():
    """Provide a consistent lab ID for testing."""
    return uuid4()


@pytest.fixture
def sample_patient_id():
    """Provide a consistent patient ID for testing."""
    return uuid4()


@pytest.fixture
def sample_test_order_id():
    """Provide a consistent test order ID for testing."""
    return uuid4()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )