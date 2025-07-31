import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_dependency_override_works(client: AsyncClient):
    """Test that the dependency override is working."""
    response = await client.get("/api/v1/lab-services/by-lab/00000000-0000-0000-0000-000000000123")
    # Should not get 401 Unauthorized if override works
    assert response.status_code != 401