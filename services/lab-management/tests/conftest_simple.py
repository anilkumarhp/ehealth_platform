import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.core.security import TokenPayload


@pytest.fixture
def mock_current_user():
    """Create a mock current user for testing."""
    return TokenPayload(
        sub=uuid4(),
        full_name="Test User",
        date_of_birth="1990-01-01",
        gender="M",
        primary_mobile_number="+1234567890",
        email="test@example.com",
        roles=["patient", "lab-admin"],
        org_id=uuid4(),
        national_health_id="TEST123456",
        address="123 Test Street"
    )


@pytest.fixture
def db_session():
    """Create a simple mock database session."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    # Async execute mock
    mock_result = MagicMock()
    mock_result.fetchone.return_value = [1]
    mock_result.scalars.return_value.all.return_value = []
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    return mock_db


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "asyncio: mark test as async")
    config.addinivalue_line("markers", "unit: mark test as unit test")