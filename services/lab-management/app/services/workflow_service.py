from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.models.test_order import TestOrder, TestOrderStatusEnum
from app.models.appointment import Appointment, AppointmentStatusEnum
from app.services.test_order_service import test_order_service
from app.services.appointment_service import appointment_service


class TestOrderWorkflowService:
    """Service for managing test order workflows."""

    async def create_order_with_consent_request(
        self,
        db: AsyncSession,
        patient_id: UUID,
        lab_service_id: UUID,
        requesting_entity_id: UUID,
        organization_id: UUID,
        clinical_notes: Optional[str] = None
    ) -> TestOrder:
        """Create test order and initiate consent request workflow."""
        
        # Create test order in PENDING_CONSENT status
        order = await test_order_service.create_order(
            db=db,
            patient_user_id=patient_id,
            lab_service_id=lab_service_id,
            requesting_entity_id=requesting_entity_id,
            organization_id=organization_id,
            clinical_notes=clinical_notes
        )
        
        # TODO: Publish event for notification service
        # await self._publish_consent_request_event(order)
        
        return order

    async def process_consent_approval(
        self,
        db: AsyncSession,
        order_id: UUID,
        patient_id: UUID
    ) -> TestOrder:
        """Process consent approval and move to next workflow step."""
        
        # Update order status to AWAITING_APPOINTMENT
        order = await test_order_service.update_order_status(
            db=db,
            order_id=order_id,
            new_status=TestOrderStatusEnum.AWAITING_APPOINTMENT,
            user_id=patient_id
        )
        
        # TODO: Publish event for notification service
        # await self._publish_consent_approved_event(order)
        
        return order

    async def schedule_appointment_after_consent(
        self,
        db: AsyncSession,
        order_id: UUID,
        appointment_datetime: str,
        lab_id: UUID
    ) -> Appointment:
        """Schedule appointment after consent is approved."""
        
        # Get the test order
        order = await test_order_service.get_order_by_id(db=db, order_id=order_id)
        if not order or order.status != TestOrderStatusEnum.AWAITING_APPOINTMENT:
            raise ValueError("Order not ready for appointment scheduling")
        
        # Create appointment
        appointment = await appointment_service.create_appointment(
            db=db,
            test_order_id=order_id,
            patient_user_id=order.patient_user_id,
            lab_service_id=order.lab_service_id,
            appointment_datetime=appointment_datetime,
            lab_id=lab_id
        )
        
        # Update order status
        await test_order_service.update_order_status(
            db=db,
            order_id=order_id,
            new_status=TestOrderStatusEnum.SCHEDULED,
            user_id=order.patient_user_id
        )
        
        return appointment

    async def complete_test_and_notify(
        self,
        db: AsyncSession,
        appointment_id: UUID,
        completion_notes: Optional[str] = None
    ) -> Appointment:
        """Mark test as completed and trigger notifications."""
        
        # Update appointment status
        appointment = await appointment_service.update_appointment_status(
            db=db,
            appointment_id=appointment_id,
            new_status=AppointmentStatusEnum.COMPLETED,
            completion_notes=completion_notes
        )
        
        # Update related test order status
        if appointment.test_order_id:
            await test_order_service.update_order_status(
                db=db,
                order_id=appointment.test_order_id,
                new_status=TestOrderStatusEnum.COMPLETED,
                user_id=appointment.patient_user_id
            )
        
        # TODO: Publish event for notification service
        # await self._publish_test_completed_event(appointment)
        
        return appointment


# Singleton instance
workflow_service = TestOrderWorkflowService()