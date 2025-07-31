"""
Integration tests for medicine API endpoints
"""

import pytest
from httpx import AsyncClient

class TestMedicineAPI:
    """Test medicine API endpoints."""
    
    @pytest.mark.asyncio
    async def test_search_medicines_success(self, client: AsyncClient):
        """Test medicine search via API."""
        response = await client.get("/api/v1/medicines/search?q=paracetamol&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_search_medicines_empty_query(self, client: AsyncClient):
        """Test medicine search with empty query."""
        response = await client.get("/api/v1/medicines/search?q=&limit=10")
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_search_medicines_no_results(self, client: AsyncClient):
        """Test medicine search with no results."""
        response = await client.get("/api/v1/medicines/search?q=nonexistentmedicine&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0