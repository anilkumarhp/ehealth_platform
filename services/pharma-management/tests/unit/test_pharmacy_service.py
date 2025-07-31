"""
Unit tests for pharmacy service
"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.pharmacy_service import PharmacyService
from app.schemas.pharmacy import PharmacyCreate, PharmacyUpdate
from app.core.exceptions import PharmacyNotFoundException

class TestPharmacyService:
    """Test pharmacy service operations."""
    
    @pytest.mark.asyncio
    async def test_create_pharmacy_success(self, db_session: AsyncSession):
        """Test successful pharmacy creation."""
        service = PharmacyService(db_session)
        
        pharmacy_data = PharmacyCreate(
            name="New Pharmacy",
            license_number="NEW001",
            registration_number="REGNEW001",
            email="new@pharmacy.com",
            phone="+91 9876543212",
            address_line1="456 New Street",
            city="New City",
            state="New State",
            postal_code="654321",
            country="India",
            owner_name="New Owner",
            pharmacist_in_charge="New Pharmacist"
        )
        
        pharmacy = await service.create_pharmacy(pharmacy_data)
        
        assert pharmacy.name == "New Pharmacy"
        assert pharmacy.license_number == "NEW001"
        assert pharmacy.verification_status == "pending"
        assert pharmacy.operational_status == "active"
    
    @pytest.mark.asyncio
    async def test_create_pharmacy_duplicate_license(self, db_session: AsyncSession, test_pharmacy):
        """Test pharmacy creation with duplicate license number."""
        service = PharmacyService(db_session)
        
        pharmacy_data = PharmacyCreate(
            name="Duplicate Pharmacy",
            license_number=test_pharmacy.license_number,
            registration_number="REGDUP001",
            email="dup@pharmacy.com",
            phone="+91 9876543213",
            address_line1="789 Dup Street",
            city="Dup City",
            state="Dup State",
            postal_code="789123",
            country="India",
            owner_name="Dup Owner",
            pharmacist_in_charge="Dup Pharmacist"
        )
        
        with pytest.raises(ValueError, match="already exists"):
            await service.create_pharmacy(pharmacy_data)
    
    @pytest.mark.asyncio
    async def test_get_pharmacy_not_found(self, db_session: AsyncSession):
        """Test pharmacy retrieval with non-existent ID."""
        service = PharmacyService(db_session)
        
        with pytest.raises(PharmacyNotFoundException):
            await service.get_pharmacy(uuid4())