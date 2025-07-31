"""
Integration tests for inventory API endpoints
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4

class TestInventoryAPI:
    """Test inventory API endpoints."""
    
    @pytest.mark.asyncio
    async def test_add_inventory_item(self, client: AsyncClient, test_pharmacy):
        """Test adding inventory item via API."""
        # First create a medicine
        medicine_data = {
            "name": "API Inventory Medicine",
            "generic_name": "API Generic",
            "manufacturer": "API Manufacturer",
            "strength": "250mg",
            "dosage_form": "Tablet",
            "route_of_administration": "oral",
            "active_ingredients": ["API Ingredient"],
            "unit_price": 15.75,
            "prescription_required": True,
            "controlled_substance": False
        }
        
        medicine_response = await client.post("/api/v1/medicines/", json=medicine_data)
        assert medicine_response.status_code == 200
        medicine_id = medicine_response.json()["id"]
        
        # Now add inventory item
        inventory_data = {
            "medicine_id": medicine_id,
            "current_stock": 100,
            "minimum_stock": 10,
            "maximum_stock": 200,
            "reorder_point": 20,
            "cost_price": 8.50,
            "selling_price": 12.75,
            "mrp": 15.00,
            "storage_location": "Shelf A-1"
        }
        
        response = await client.post(f"/api/v1/pharmacies/{test_pharmacy.id}/inventory", json=inventory_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["medicine_id"] == medicine_id
        assert data["current_stock"] == 100
    
    @pytest.mark.asyncio
    async def test_get_pharmacy_inventory(self, client: AsyncClient, test_pharmacy):
        """Test getting pharmacy inventory via API."""
        response = await client.get(f"/api/v1/pharmacies/{test_pharmacy.id}/inventory")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_low_stock_items(self, client: AsyncClient, test_pharmacy):
        """Test getting low stock items via API."""
        response = await client.get(f"/api/v1/pharmacies/{test_pharmacy.id}/inventory/low-stock")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)