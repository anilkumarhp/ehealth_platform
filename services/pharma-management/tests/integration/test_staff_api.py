"""
Integration tests for staff API endpoints
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4

class TestStaffAPI:
    """Test staff API endpoints."""
    
    @pytest.mark.asyncio
    async def test_add_staff_member_success(self, client: AsyncClient, test_pharmacy):
        """Test successful staff member addition via API."""
        staff_data = {
            "user_id": str(uuid4()),
            "first_name": "API",
            "last_name": "Staff",
            "email": "api.staff@pharmacy.com",
            "phone": "+91 9876543217",
            "role": "pharmacist",
            "license_number": "APISTAFF001",
            "hire_date": "2024-01-01",
            "can_validate_prescriptions": True,
            "can_dispense_controlled_substances": True,
            "can_manage_inventory": True,
            "can_process_payments": True
        }
        
        response = await client.post(f"/api/v1/pharmacies/{test_pharmacy.id}/staff", json=staff_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "API"
        assert data["last_name"] == "Staff"
        assert data["role"] == "pharmacist"
    
    @pytest.mark.asyncio
    async def test_add_staff_member_pharmacy_not_found(self, client: AsyncClient):
        """Test adding staff to non-existent pharmacy."""
        fake_id = str(uuid4())
        staff_data = {
            "user_id": str(uuid4()),
            "first_name": "Test",
            "last_name": "Staff",
            "email": "test.staff@pharmacy.com",
            "phone": "+91 9876543218",
            "role": "pharmacist",
            "license_number": "TESTSTAFF001",
            "hire_date": "2024-01-01"
        }
        
        response = await client.post(f"/api/v1/pharmacies/{fake_id}/staff", json=staff_data)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_pharmacy_staff(self, client: AsyncClient, test_pharmacy):
        """Test getting all staff for a pharmacy."""
        response = await client.get(f"/api/v1/pharmacies/{test_pharmacy.id}/staff")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)