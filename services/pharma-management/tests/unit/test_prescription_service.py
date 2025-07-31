"""
Unit tests for prescription service
"""

import pytest
from uuid import uuid4
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.prescription_service import PrescriptionService
from app.schemas.prescription import PrescriptionCreate, PrescriptionItemCreate
from app.models.prescription import Prescription

class TestPrescriptionService:
    """Test prescription service operations."""
    
    @pytest.mark.asyncio
    async def test_create_prescription_success(self, db_session: AsyncSession, test_pharmacy):
        """Test successful prescription creation."""
        service = PrescriptionService(db_session)
        
        # Create prescription data with unique prescription number
        unique_id = str(uuid4())[:8]
        prescription_number = f"RX-TEST-{unique_id}"
        
        prescription_data = PrescriptionCreate(
            prescription_number=prescription_number,
            patient_id=uuid4(),
            doctor_id=uuid4(),
            patient_name="Test Patient",
            patient_age=35,
            patient_gender="male",
            doctor_name="Dr. Test Doctor",
            doctor_license="MED12345",
            issue_date=date(2024, 1, 1),
            expiry_date=date(2024, 7, 1),
            diagnosis="Test Diagnosis",
            special_instructions="Take with food",
            items=[]  # Add empty items list
        )
        
        prescription = await service.create_prescription(test_pharmacy.id, prescription_data)
        
        assert prescription.prescription_number == prescription_number
        assert prescription.patient_name == "Test Patient"
        assert prescription.doctor_name == "Dr. Test Doctor"
        assert prescription.pharmacy_id == test_pharmacy.id
        assert prescription.status == "uploaded"
    
    @pytest.mark.asyncio
    async def test_add_prescription_item(self, db_session: AsyncSession, test_pharmacy):
        """Test adding item to prescription."""
        # Create test prescription with unique prescription number
        unique_id = str(uuid4())[:8]
        prescription_number = f"RX-ITEM-{unique_id}"
        
        prescription = Prescription(
            id=uuid4(),
            prescription_number=prescription_number,
            patient_id=uuid4(),
            doctor_id=uuid4(),
            pharmacy_id=test_pharmacy.id,
            patient_name="Test Patient",
            doctor_name="Dr. Test Doctor",
            issue_date=date(2024, 1, 1),
            expiry_date=date(2024, 7, 1),
            status="uploaded"
        )
        db_session.add(prescription)
        await db_session.commit()
        
        # Create test medicine
        medicine_id = uuid4()
        
        service = PrescriptionService(db_session)
        
        # Add prescription item
        item_data = PrescriptionItemCreate(
            medicine_id=medicine_id,
            medicine_name="Test Medicine",
            strength="500mg",
            dosage_form="Tablet",
            quantity_prescribed=30,
            unit="tablets",
            dosage_instructions="Take one tablet twice daily"
        )
        
        prescription_item = await service.add_prescription_item(prescription.id, item_data)
        
        assert prescription_item.prescription_id == prescription.id
        assert prescription_item.medicine_id == medicine_id
        assert prescription_item.medicine_name == "Test Medicine"
        assert prescription_item.quantity_prescribed == 30