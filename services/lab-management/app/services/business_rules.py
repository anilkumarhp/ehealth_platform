from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timedelta

from app.models.test_order import TestOrderStatusEnum


class BusinessRulesService:
    """Service for enforcing business rules and validation."""

    async def validate_test_order_eligibility(
        self,
        db: AsyncSession,
        patient_id: UUID,
        lab_service_id: UUID
    ) -> bool:
        """Validate if patient is eligible for the test order."""
        
        # Check if lab service exists and is active
        from app.services.lab_service_service import lab_service_service
        service = await lab_service_service.get_service(db=db, service_id=lab_service_id)
        if not service or not service.is_active:
            return False
        
        return True

    def check_consent_requirements(self, test_type: str) -> bool:
        """Check if specific test type requires special consent."""
        special_consent_tests = [
            "genetic_testing",
            "hiv_test", 
            "drug_screening"
        ]
        return test_type.lower() in special_consent_tests

    async def validate_appointment_scheduling(
        self,
        db: AsyncSession,
        lab_id: UUID,
        appointment_datetime: datetime
    ) -> bool:
        """Validate if appointment can be scheduled at given time."""
        
        # Check if appointment is in the future
        if appointment_datetime <= datetime.utcnow():
            return False
        
        # Check business hours (9 AM - 5 PM)
        if appointment_datetime.hour < 9 or appointment_datetime.hour >= 17:
            return False
        
        # Check weekdays only (Monday=0, Sunday=6)
        if appointment_datetime.weekday() >= 5:  # Saturday=5, Sunday=6
            return False
        
        return True

    def calculate_estimated_completion_time(self, test_count: int) -> datetime:
        """Calculate estimated test completion time."""
        base_time_per_test = 30  # minutes
        processing_time = test_count * base_time_per_test
        buffer_time = processing_time * 0.2
        total_time = processing_time + buffer_time
        
        return datetime.utcnow() + timedelta(minutes=total_time)


# Singleton instance
business_rules = BusinessRulesService()