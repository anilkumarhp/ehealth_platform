import pytest
import os
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# Set environment variables for tests
os.environ["REDIS_URL"] = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Configure pytest-asyncio to use the event loop
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Add fixtures that can be used across all tests here