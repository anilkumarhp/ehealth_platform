"""
Unit tests for inventory service
"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.inventory_service import InventoryService
from app.models.inventory import InventoryItem
from app.models.medicine import Medicine
from app.schemas.inventory import InventoryItemCreate, InventoryTransactionCreate

class TestInventoryService:
    """Test inventory service operations."""
    
    @pytest.mark.asyncio
    async def test_add_inventory_item_success(self, db_session: AsyncSession, test_pharmacy):
        """Test successful inventory item addition."""
        # Create test medicine
        medicine = Medicine(
            id=uuid4(),
            name="Inventory Test Medicine",
            generic_name="Test Generic",
            manufacturer="Test Manufacturer",
            strength="500mg",
            dosage_form="Tablet",
            route_of_administration="oral",
            active_ingredients=["Test Ingredient"],
            unit_price=10.50,
            prescription_required=True,
            controlled_substance=False
        )
        db_session.add(medicine)
        await db_session.commit()
        
        service = InventoryService(db_session)
        
        item_data = InventoryItemCreate(
            medicine_id=medicine.id,
            current_stock=100,
            minimum_stock=10,
            maximum_stock=200,
            reorder_point=20,
            cost_price=8.50,
            selling_price=12.75,
            mrp=15.00,
            storage_location="Shelf A-1"
        )
        
        inventory_item = await service.add_inventory_item(test_pharmacy.id, item_data)
        
        assert inventory_item.medicine_id == medicine.id
        assert inventory_item.pharmacy_id == test_pharmacy.id
        assert inventory_item.current_stock == 100
        assert inventory_item.selling_price == 12.75
    
    @pytest.mark.asyncio
    async def test_update_inventory_stock(self, db_session: AsyncSession, test_pharmacy):
        """Test updating inventory stock levels."""
        # Create test inventory item
        medicine_id = uuid4()
        inventory_item = InventoryItem(
            id=uuid4(),
            pharmacy_id=test_pharmacy.id,
            medicine_id=medicine_id,
            current_stock=50,
            minimum_stock=10,
            maximum_stock=200,
            reorder_point=20,
            cost_price=8.50,
            selling_price=12.75,
            mrp=15.00
        )
        db_session.add(inventory_item)
        await db_session.commit()
        
        service = InventoryService(db_session)
        
        # Add stock transaction
        transaction_data = InventoryTransactionCreate(
            inventory_item_id=inventory_item.id,
            transaction_type="purchase",
            quantity=25,
            unit_cost=8.50,
            reference_number="PO12345"
        )
        
        updated_item = await service.update_inventory_stock(transaction_data)
        
        assert updated_item.current_stock == 75  # 50 + 25
        assert updated_item.medicine_id == medicine_id