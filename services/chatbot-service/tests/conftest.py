import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator, Generator

from app.db.base import Base
from app.main import app
from app.core.config import settings
from app.db.base import get_db

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine and session
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
    
    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for each test."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with the test database."""
    # Override the get_db dependency
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clear dependency overrides
    app.dependency_overrides.clear()

@pytest.fixture
def mock_llm_response():
    """Mock response from LLM service."""
    return {
        "intent": "find_doctor",
        "entities": {"specialty": "cardiologist"},
        "confidence": 0.9
    }

@pytest.fixture
def mock_healthcare_providers():
    """Mock healthcare providers response."""
    return [
        {
            "id": "123",
            "name": "Dr. John Doe",
            "type": "doctor",
            "specialty": "cardiologist",
            "address": "123 Main St",
            "city": "Mumbai",
            "state": "Maharashtra",
            "rating": 4.5,
            "distance": 2.5
        },
        {
            "id": "456",
            "name": "Dr. Jane Smith",
            "type": "doctor",
            "specialty": "cardiologist",
            "address": "456 Oak St",
            "city": "Mumbai",
            "state": "Maharashtra",
            "rating": 4.8,
            "distance": 3.2
        }
    ]