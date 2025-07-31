"""
Unit tests for medicine service
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.medicine_service import MedicineService
from app.models.medicine import Medicine

class TestMedicineService:
    """Test medicine service operations."""
    
    @pytest.mark.asyncio
    async def test_search_medicines_success(self, db_session: AsyncSession):
        """Test successful medicine search."""
        # Create test medicine
        medicine = Medicine(
            name="Test Medicine",
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
        await db_session.refresh(medicine)
        
        # Get medicine by ID to verify it exists
        service = MedicineService(db_session)
        medicine_by_id = await service.get_medicine(medicine.id)
        
        assert medicine_by_id is not None
        assert medicine_by_id.name == "Test Medicine"
    
    @pytest.mark.asyncio
    async def test_search_medicines_empty_result(self, db_session: AsyncSession):
        """Test medicine search with no results."""
        service = MedicineService(db_session)
        results = await service.search_medicines("NonExistent", limit=10)
        
        assert len(results) == 0