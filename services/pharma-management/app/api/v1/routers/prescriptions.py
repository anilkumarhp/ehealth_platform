"""
Prescription management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from uuid import UUID
import logging
from datetime import datetime

from app.db.session import get_async_session
from app.schemas.prescription import PrescriptionResponse, PrescriptionValidation
from app.services.prescription_service import PrescriptionService
from app.core.exceptions import PrescriptionNotFoundException, InvalidPrescriptionImageException

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=PrescriptionResponse)
async def upload_prescription(
    patient_id: UUID,
    doctor_id: UUID,
    pharmacy_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_session)
):
    """Upload prescription image for OCR processing."""
    try:
        prescription_service = PrescriptionService(db)
        prescription = await prescription_service.upload_prescription(
            patient_id, doctor_id, pharmacy_id, file
        )
        return prescription
    except Exception as e:
        logger.error(f"Error uploading prescription: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{prescription_id}", response_model=PrescriptionResponse)
async def get_prescription(
    prescription_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """Get prescription details."""
    try:
        prescription_service = PrescriptionService(db)
        prescription = await prescription_service.get_prescription(prescription_id)
        return prescription
    except Exception as e:
        logger.error(f"Error getting prescription: {e}")
        raise HTTPException(status_code=404, detail="Prescription not found")


@router.post("/{prescription_id}/validate", response_model=PrescriptionValidation)
async def validate_prescription(
    prescription_id: UUID,
    validation_data: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_async_session)
):
    """Validate prescription by pharmacist."""
    try:
        # Use a mock pharmacist ID for testing
        from uuid import uuid4
        pharmacist_id = uuid4()
        
        # Get the prescription first
        prescription_service = PrescriptionService(db)
        prescription = await prescription_service.get_prescription(prescription_id)
        
        # Update the prescription with validation data
        update_data = {
            "validation_status": validation_data.get("validation_status", "approved"),
            "validation_notes": validation_data.get("validation_notes", ""),
            "validated_by": pharmacist_id,
            "validated_at": datetime.now().date()
        }
        
        await prescription_service.prescription_repo.update(prescription_id, update_data)
        
        # Return validation result
        validation_result = PrescriptionValidation(
            prescription_id=prescription_id,
            validation_status=update_data["validation_status"],
            validated_by=pharmacist_id,
            validated_at=datetime.utcnow(),
            validation_notes=update_data["validation_notes"],
            issues_found=[],
            recommendations=[],
            approved=True
        )
        
        return validation_result
    except Exception as e:
        logger.error(f"Error validating prescription: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{prescription_id}/ocr")
async def get_ocr_results(
    prescription_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """Get OCR processing results."""
    try:
        prescription_service = PrescriptionService(db)
        ocr_results = await prescription_service.get_ocr_results(prescription_id)
        return ocr_results
    except Exception as e:
        logger.error(f"Error getting OCR results: {e}")
        raise HTTPException(status_code=404, detail="OCR results not found")