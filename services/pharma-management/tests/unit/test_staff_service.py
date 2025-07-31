"""
Unit tests for staff service
"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.staff_service import StaffService
from app.schemas.staff import StaffCreate
from app.core.exceptions import PharmacyNotFoundException

class TestStaffService:
    """Test staff service operations."""
    
    @pytest.mark.asyncio
    async def test_add_staff_member_success(self, db_session: AsyncSession, test_pharmacy):
        """Test successful staff member addition."""
        service = StaffService(db_session)
        
        staff_data = StaffCreate(
            user_id=uuid4(),
            first_name="New",
            last_name="Staff",
            email="new.staff@pharmacy.com",
            phone="+91 9876543215",
            role="pharmacist",
            license_number="NEWSTAFF001",
            hire_date="2024-01-01",
            can_validate_prescriptions=True,
            can_dispense_controlled_substances=True,
            can_manage_inventory=True,
            can_process_payments=True
        )
        
        staff = await service.add_staff_member(test_pharmacy.id, staff_data)
        
        assert staff.first_name == "New"
        assert staff.last_name == "Staff"
        assert staff.role == "pharmacist"
        assert staff.pharmacy_id == test_pharmacy.id
    
    @pytest.mark.asyncio
    async def test_add_staff_member_pharmacy_not_found(self, db_session: AsyncSession):
        """Test adding staff to non-existent pharmacy."""
        service = StaffService(db_session)
        
        staff_data = StaffCreate(
            user_id=uuid4(),
            first_name="Test",
            last_name="Staff",
            email="test@pharmacy.com",
            phone="+91 9876543216",
            role="pharmacist",
            license_number="TEST001",
            hire_date="2024-01-01"
        )
        
        with pytest.raises(PharmacyNotFoundException):
            await service.add_staff_member(uuid4(), staff_data)