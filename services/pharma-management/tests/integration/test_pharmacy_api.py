"""
Integration tests for pharmacy API endpoints
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4

class TestPharmacyAPI:
    """Test pharmacy API endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_pharmacy_success(self, client: AsyncClient):
        """Test successful pharmacy creation via API."""
        pharmacy_data = {
            "name": "API Test Pharmacy",
            "license_number": "API001",
            "registration_number": "REGAPI001",
            "email": "api@pharmacy.com",
            "phone": "+91 9876543214",
            "address_line1": "123 API Street",
            "city": "API City",
            "state": "API State",
            "postal_code": "123456",
            "country": "India",
            "owner_name": "API Owner",
            "pharmacist_in_charge": "API Pharmacist"
        }
        
        response = await client.post("/api/v1/pharmacies/", json=pharmacy_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "API Test Pharmacy"
        assert data["license_number"] == "API001"
        assert data["verification_status"] == "pending"
    
    @pytest.mark.asyncio
    async def test_search_pharmacies(self, client: AsyncClient, test_pharmacy):
        """Test pharmacy search functionality."""
        response = await client.get(f"/api/v1/pharmacies/search?name={test_pharmacy.name}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["name"] == test_pharmacy.name
    
    @pytest.mark.asyncio
    async def test_get_pharmacy_suggestions(self, client: AsyncClient, test_pharmacy):
        """Test pharmacy suggestions endpoint."""
        response = await client.get(f"/api/v1/pharmacies/suggestions?name=Test")
        
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert data["count"] >= 1
    
    @pytest.mark.asyncio
    async def test_get_pharmacy_not_found(self, client: AsyncClient):
        """Test getting non-existent pharmacy."""
        fake_id = str(uuid4())
        response = await client.get(f"/api/v1/pharmacies/{fake_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()