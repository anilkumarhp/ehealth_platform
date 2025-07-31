import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lab_service import LabService
from app.models.test_definition import TestDefinition


@pytest.mark.asyncio
async def test_database_connection(db_session: AsyncSession):
    """Test that async database connection works."""
    from sqlalchemy import text
    # Simple query to test connection
    result = await db_session.execute(text("SELECT 1 as test"))
    row = result.fetchone()
    assert row[0] == 1


@pytest.mark.asyncio
async def test_api_health_check(client: AsyncClient):
    """Test that the API is accessible."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_create_lab_service(db_session: AsyncSession):
    """Test creating a lab service with async session."""
    # Create a test lab service
    lab_service = LabService(
        name="Test Blood Panel",
        description="A comprehensive blood test",
        price=99.99,
        lab_id="00000000-0000-0000-0000-000000000123",
        is_active=True
    )
    
    db_session.add(lab_service)
    await db_session.flush()
    await db_session.refresh(lab_service)
    
    assert lab_service.id is not None
    assert lab_service.name == "Test Blood Panel"
    assert float(lab_service.price) == 99.99