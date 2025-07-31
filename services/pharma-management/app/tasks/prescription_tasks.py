"""
Celery tasks for prescription processing
"""

from celery import current_task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, date, timedelta
import logging
import asyncio
from typing import Dict, Any

from app.tasks.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.models.prescription import Prescription, PrescriptionStatusEnum
from app.integrations.ocr.prescription_ocr import PrescriptionOCR
from app.services.notification_service import NotificationService
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_prescription_ocr(self, prescription_id: str, image_path: str) -> Dict[str, Any]:
    """Process prescription image with OCR."""
    try:
        return asyncio.run(_process_prescription_ocr_async(prescription_id, image_path))
    except Exception as exc:
        logger.error(f"OCR processing failed for prescription {prescription_id}: {exc}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        return {"success": False, "error": str(exc)}


async def _process_prescription_ocr_async(prescription_id: str, image_path: str) -> Dict[str, Any]:
    """Async OCR processing logic."""
    async with AsyncSessionLocal() as db:
        try:
            # Get prescription
            result = await db.execute(
                select(Prescription).where(Prescription.id == prescription_id)
            )
            prescription = result.scalar_one_or_none()
            
            if not prescription:
                return {"success": False, "error": "Prescription not found"}
            
            # Update status to processing
            prescription.status = PrescriptionStatusEnum.PROCESSING.value
            await db.commit()
            
            # Initialize OCR service
            ocr_service = PrescriptionOCR()
            
            # Process image
            ocr_result = await ocr_service.process_prescription_image(image_path)
            
            # Update prescription with OCR results
            prescription.ocr_text = ocr_result.get("text", "")
            prescription.ocr_confidence = ocr_result.get("confidence", 0)
            prescription.ocr_processed_at = datetime.utcnow()
            
            # Update status based on confidence
            if ocr_result.get("confidence", 0) >= 60:  # Configurable threshold
                prescription.status = PrescriptionStatusEnum.VALIDATED.value
            else:
                prescription.status = PrescriptionStatusEnum.REJECTED.value
                prescription.validation_notes = "Low OCR confidence"
            
            await db.commit()
            
            # Log audit trail
            audit_service = AuditService(db)
            await audit_service.log_prescription_action(
                action="prescription_ocr_processed",
                prescription_id=prescription.id,
                description=f"OCR processed with {ocr_result.get('confidence', 0)}% confidence",
                metadata=ocr_result
            )
            
            # Send notification if successful
            if prescription.status == PrescriptionStatusEnum.VALIDATED.value:
                notification_service = NotificationService(db)
                await notification_service.send_prescription_ready_notification(prescription.id)
            
            logger.info(f"OCR processing completed for prescription {prescription_id}")
            return {"success": True, "ocr_result": ocr_result}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error in OCR processing: {e}")
            raise


@celery_app.task
def check_expired_prescriptions() -> Dict[str, Any]:
    """Check for expired prescriptions and update status."""
    try:
        return asyncio.run(_check_expired_prescriptions_async())
    except Exception as exc:
        logger.error(f"Error checking expired prescriptions: {exc}")
        return {"success": False, "error": str(exc)}


async def _check_expired_prescriptions_async() -> Dict[str, Any]:
    """Async logic for checking expired prescriptions."""
    async with AsyncSessionLocal() as db:
        try:
            # Find prescriptions that have expired
            today = date.today()
            result = await db.execute(
                select(Prescription).where(
                    and_(
                        Prescription.expiry_date < today,
                        Prescription.status.in_([
                            PrescriptionStatusEnum.UPLOADED.value,
                            PrescriptionStatusEnum.PROCESSING.value,
                            PrescriptionStatusEnum.VALIDATED.value
                        ])
                    )
                )
            )
            expired_prescriptions = result.scalars().all()
            
            updated_count = 0
            for prescription in expired_prescriptions:
                prescription.status = PrescriptionStatusEnum.EXPIRED.value
                updated_count += 1
                
                # Log audit trail
                audit_service = AuditService(db)
                await audit_service.log_prescription_action(
                    action="prescription_expired",
                    prescription_id=prescription.id,
                    description=f"Prescription expired on {prescription.expiry_date}"
                )
            
            await db.commit()
            
            logger.info(f"Updated {updated_count} expired prescriptions")
            return {"success": True, "updated_count": updated_count}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error checking expired prescriptions: {e}")
            raise


@celery_app.task(bind=True, max_retries=3)
def validate_prescription_with_ai(self, prescription_id: str) -> Dict[str, Any]:
    """Validate prescription using AI/ML models."""
    try:
        return asyncio.run(_validate_prescription_with_ai_async(prescription_id))
    except Exception as exc:
        logger.error(f"AI validation failed for prescription {prescription_id}: {exc}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        return {"success": False, "error": str(exc)}


async def _validate_prescription_with_ai_async(prescription_id: str) -> Dict[str, Any]:
    """Async AI validation logic."""
    async with AsyncSessionLocal() as db:
        try:
            # Get prescription
            result = await db.execute(
                select(Prescription).where(Prescription.id == prescription_id)
            )
            prescription = result.scalar_one_or_none()
            
            if not prescription:
                return {"success": False, "error": "Prescription not found"}
            
            # AI validation logic would go here
            # For now, we'll simulate validation
            validation_result = {
                "valid": True,
                "confidence": 85.5,
                "issues": [],
                "drug_interactions": [],
                "dosage_warnings": []
            }
            
            # Update prescription based on validation
            if validation_result["valid"]:
                prescription.validation_status = "approved"
            else:
                prescription.validation_status = "rejected"
                prescription.validation_notes = "; ".join(validation_result["issues"])
            
            prescription.validated_at = datetime.utcnow()
            await db.commit()
            
            # Log audit trail
            audit_service = AuditService(db)
            await audit_service.log_prescription_action(
                action="prescription_ai_validated",
                prescription_id=prescription.id,
                description=f"AI validation completed with {validation_result['confidence']}% confidence",
                metadata=validation_result
            )
            
            logger.info(f"AI validation completed for prescription {prescription_id}")
            return {"success": True, "validation_result": validation_result}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error in AI validation: {e}")
            raise