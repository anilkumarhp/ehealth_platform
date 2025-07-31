"""
Integration tests for prescription API endpoints
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4

class TestPrescriptionAPI:
    """Test prescription API endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_prescription(self, client: AsyncClient, test_pharmacy):
        """Test creating prescription via API."""
        # Create unique prescription number
        unique_id = str(uuid4())[:8]
        prescription_number = f"API-TEST-{unique_id}"
        
        prescription_data = {
            "prescription_number": prescription_number,
            "patient_id": str(uuid4()),
            "doctor_id": str(uuid4()),
            "patient_name": "API Test Patient",
            "patient_age": 45,
            "patient_gender": "female",
            "doctor_name": "Dr. API Test",
            "doctor_license": "API12345",
            "issue_date": "2024-01-15",
            "expiry_date": "2024-07-15",
            "diagnosis": "API Test Diagnosis",
            "special_instructions": "Take as directed"
        }
        
        response = await client.post(f"/api/v1/pharmacies/{test_pharmacy.id}/prescriptions", json=prescription_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["prescription_number"] == prescription_number
        assert data["patient_name"] == "API Test Patient"
        assert data["status"] == "uploaded"
    
    @pytest.mark.asyncio
    async def test_get_pharmacy_prescriptions(self, client: AsyncClient, test_pharmacy):
        """Test getting pharmacy prescriptions via API."""
        response = await client.get(f"/api/v1/pharmacies/{test_pharmacy.id}/prescriptions")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_validate_prescription(self, client: AsyncClient, test_pharmacy):
        """Test validating prescription via API."""
        # First create a prescription with unique prescription number
        unique_id = str(uuid4())[:8]
        prescription_number = f"VALIDATE-{unique_id}"
        
        prescription_data = {
            "prescription_number": prescription_number,
            "patient_id": str(uuid4()),
            "doctor_id": str(uuid4()),
            "patient_name": "Validation Patient",
            "doctor_name": "Dr. Validator",
            "issue_date": "2024-01-20",
            "expiry_date": "2024-07-20"
        }
        
        create_response = await client.post(f"/api/v1/pharmacies/{test_pharmacy.id}/prescriptions", json=prescription_data)
        assert create_response.status_code == 200
        prescription_id = create_response.json()["id"]
        
        # Now validate it
        validation_data = {
            "validation_status": "approved",
            "validation_notes": "All medications verified"
        }
        
        response = await client.post(f"/api/v1/prescriptions/{prescription_id}/validate", json=validation_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["validation_status"] == "approved"