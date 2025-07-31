"""
Prescription management service
"""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from typing import Optional
from uuid import UUID
import logging
from datetime import datetime
import uuid
import os

from app.models.prescription import Prescription, PrescriptionItem
from app.repositories.base_repository import BaseRepository
from app.schemas.prescription import PrescriptionResponse, PrescriptionValidation
from app.core.exceptions import PrescriptionNotFoundException
from app.services.audit_service import AuditService
# from app.tasks.prescription_tasks import process_prescription_ocr
from app.core.config import settings

logger = logging.getLogger(__name__)


class PrescriptionService:
    """Service for prescription management operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.prescription_repo = BaseRepository(db, Prescription)
        self.prescription_item_repo = BaseRepository(db, PrescriptionItem)
        self.audit_service = AuditService(db)
    
    async def upload_prescription(
        self, 
        patient_id: UUID, 
        doctor_id: UUID, 
        pharmacy_id: UUID,
        file: UploadFile
    ) -> PrescriptionResponse:
        """Upload prescription image for OCR processing."""
        try:
            # Validate file
            if not file.content_type.startswith('image/'):
                raise ValueError("File must be an image")
            
            if file.size > settings.MAX_FILE_SIZE:
                raise ValueError("File size exceeds maximum allowed size")
            
            # Generate prescription number
            prescription_number = await self._generate_prescription_number()
            
            # Save file
            file_path = await self._save_prescription_file(file, prescription_number)
            
            # Create prescription record
            prescription_dict = {
                "prescription_number": prescription_number,
                "patient_id": patient_id,
                "doctor_id": doctor_id,
                "pharmacy_id": pharmacy_id,
                "patient_name": f"Patient-{str(patient_id)[:8]}",  # Would get from user service
                "doctor_name": f"Doctor-{str(doctor_id)[:8]}",  # Would get from user service
                "issue_date": datetime.now().date(),
                "expiry_date": datetime.now().date(),  # Would calculate based on prescription type
                "status": "uploaded",
                "original_image_path": file_path,
                "validation_status": "pending"
            }
            
            prescription = await self.prescription_repo.create(prescription_dict)
            
            # Start OCR processing in background
            process_prescription_ocr.delay(str(prescription.id), file_path)
            
            # Log audit trail
            await self.audit_service.log_prescription_action(
                action="prescription_uploaded",
                prescription_id=prescription.id,
                pharmacy_id=pharmacy_id,
                description=f"Uploaded prescription {prescription_number}",
                metadata={
                    "prescription_number": prescription_number,
                    "file_name": file.filename,
                    "file_size": file.size
                }
            )
            
            response = PrescriptionResponse.from_orm(prescription)
            
            logger.info(f"Uploaded prescription {prescription_number}")
            return response
        except Exception as e:
            logger.error(f"Error uploading prescription: {e}")
            raise
    
    async def get_prescription(self, prescription_id: UUID) -> PrescriptionResponse:
        """Get prescription details."""
        try:
            prescription = await self.prescription_repo.get_by_id(prescription_id)
            if not prescription:
                raise PrescriptionNotFoundException(str(prescription_id))
            
            # Get prescription items
            prescription_items = await self.prescription_item_repo.get_multi(
                filters={"prescription_id": prescription_id}
            )
            
            # Convert to response format
            response = PrescriptionResponse.from_orm(prescription)
            response.items = [item for item in prescription_items]  # Would convert to PrescriptionItemResponse
            
            return response
        except Exception as e:
            logger.error(f"Error getting prescription {prescription_id}: {e}")
            raise
    
    async def validate_prescription(
        self, 
        prescription_id: UUID, 
        pharmacist_id: UUID
    ) -> PrescriptionValidation:
        """Validate prescription by pharmacist."""
        try:
            prescription = await self.prescription_repo.get_by_id(prescription_id)
            if not prescription:
                raise PrescriptionNotFoundException(str(prescription_id))
            
            # Perform validation checks
            issues_found = []
            recommendations = []
            
            # Check expiry
            if prescription.expiry_date < datetime.now().date():
                issues_found.append("Prescription has expired")
            
            # Check OCR confidence
            if prescription.ocr_confidence and prescription.ocr_confidence < 80:
                issues_found.append("Low OCR confidence - manual review required")
                recommendations.append("Verify prescription details manually")
            
            # Determine approval status
            approved = len(issues_found) == 0
            validation_status = "approved" if approved else "rejected"
            
            # Update prescription
            update_data = {
                "validation_status": validation_status,
                "validated_by": pharmacist_id,
                "validated_at": datetime.now().date(),
                "validation_notes": "; ".join(issues_found) if issues_found else "Prescription validated successfully"
            }
            
            await self.prescription_repo.update(prescription_id, update_data)
            
            # Log audit trail
            await self.audit_service.log_prescription_action(
                action="prescription_validated",
                prescription_id=prescription_id,
                user_id=pharmacist_id,
                description=f"Prescription validated by pharmacist",
                metadata={
                    "validation_status": validation_status,
                    "issues_found": issues_found,
                    "approved": approved
                }
            )
            
            validation_result = PrescriptionValidation(
                prescription_id=prescription_id,
                validation_status=validation_status,
                validated_by=pharmacist_id,
                validated_at=datetime.utcnow(),
                validation_notes="; ".join(issues_found) if issues_found else None,
                issues_found=issues_found,
                recommendations=recommendations,
                approved=approved
            )
            
            logger.info(f"Validated prescription {prescription_id} - Status: {validation_status}")
            return validation_result
        except Exception as e:
            logger.error(f"Error validating prescription: {e}")
            raise
    
    async def get_ocr_results(self, prescription_id: UUID) -> dict:
        """Get OCR processing results."""
        try:
            prescription = await self.prescription_repo.get_by_id(prescription_id)
            if not prescription:
                raise PrescriptionNotFoundException(str(prescription_id))
            
            ocr_results = {
                "prescription_id": prescription_id,
                "ocr_text": prescription.ocr_text,
                "ocr_confidence": float(prescription.ocr_confidence) if prescription.ocr_confidence else None,
                "ocr_processed_at": prescription.ocr_processed_at.isoformat() if prescription.ocr_processed_at else None,
                "status": prescription.status
            }
            
            return ocr_results
        except Exception as e:
            logger.error(f"Error getting OCR results: {e}")
            raise
    
    async def _generate_prescription_number(self) -> str:
        """Generate unique prescription number."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            prescription_number = f"RX-{timestamp}-{str(uuid.uuid4())[:4].upper()}"
            return prescription_number
        except Exception as e:
            logger.error(f"Error generating prescription number: {e}")
            return f"RX-{str(uuid.uuid4())[:8].upper()}"
    
    async def _save_prescription_file(self, file: UploadFile, prescription_number: str) -> str:
        """Save prescription file to storage."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(settings.PRESCRIPTION_STORAGE_PATH, exist_ok=True)
            
            # Generate file path
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
            file_name = f"{prescription_number}.{file_extension}"
            file_path = os.path.join(settings.PRESCRIPTION_STORAGE_PATH, file_name)
            
            # Save file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            logger.info(f"Saved prescription file: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving prescription file: {e}")
            raise
    
    async def create_prescription(self, pharmacy_id: UUID, prescription_data) -> Prescription:
        """Create a new prescription."""
        try:
            # Convert to dict and modify
            prescription_dict = prescription_data.dict()
            
            # Add pharmacy ID if not provided
            if not prescription_dict.get("pharmacy_id"):
                prescription_dict["pharmacy_id"] = pharmacy_id
            
            # Set default status
            prescription_dict["status"] = "uploaded"
            prescription_dict["validation_status"] = "pending"
            
            # Generate prescription number if not provided
            if not prescription_dict.get("prescription_number"):
                prescription_dict["prescription_number"] = await self._generate_prescription_number()
            
            # Remove items field as it's not in the Prescription model
            if "items" in prescription_dict:
                prescription_dict.pop("items")
            
            # Create prescription
            prescription = await self.prescription_repo.create(prescription_dict)
            
            # Log audit trail
            await self.audit_service.log_action(
                action="prescription_created",
                resource_type="prescription",
                resource_id=prescription.id,
                description=f"Created prescription {prescription.prescription_number}"
            )
            
            logger.info(f"Created prescription {prescription.prescription_number}")
            return prescription
        except Exception as e:
            logger.error(f"Error creating prescription: {e}")
            raise
    
    async def add_prescription_item(self, prescription_id: UUID, item_data) -> PrescriptionItem:
        """Add item to prescription."""
        try:
            # Check if prescription exists
            prescription = await self.prescription_repo.get_by_id(prescription_id)
            if not prescription:
                raise PrescriptionNotFoundException(str(prescription_id))
            
            # Create item data
            item_dict = item_data.dict()
            item_dict["prescription_id"] = prescription_id
            item_dict["dispensed"] = False
            
            # Ensure medicine_id is present
            if not item_dict.get("medicine_id"):
                raise ValueError("medicine_id is required")
            
            # Create prescription item
            prescription_item = await self.prescription_item_repo.create(item_dict)
            
            # Log audit trail
            await self.audit_service.log_action(
                action="prescription_item_added",
                resource_type="prescription_item",
                resource_id=prescription_item.id,
                description=f"Added item to prescription {prescription.prescription_number}"
            )
            
            logger.info(f"Added item to prescription {prescription.prescription_number}")
            return prescription_item
        except Exception as e:
            logger.error(f"Error adding prescription item: {e}")
            raise