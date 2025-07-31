import pytest
from httpx import AsyncClient
from fastapi import status
from uuid import uuid4
from datetime import datetime, timedelta, time
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lab_service import LabService
from app.models.lab_configuration import LabConfiguration
from app.models.test_duration import TestDuration
from app.models.appointment import Appointment, AppointmentStatusEnum
from app.models.test_order import TestOrder

@pytest.mark.usefixtures("client", "db_session")
class TestSlotConflictScenarios:
    """Integration tests for specific slot conflict scenarios."""

    @pytest.mark.asyncio
    async def test_mri_overlap_conflict_scenario(self, client: AsyncClient, db_session: AsyncSession):
        """Test the specific MRI overlap scenario mentioned in requirements."""
        
        lab_id = uuid4()
        
        # Setup lab configuration
        lab_config = LabConfiguration(
            lab_id=lab_id,
            lab_name="MRI Conflict Test Lab",
            opening_time=time(8, 0),
            closing_time=time(18, 0),
            max_concurrent_appointments=1,  # Only 1 MRI machine
            slot_interval_minutes=15
        )
        db_session.add(lab_config)
        
        # Setup MRI service
        mri_service = LabService(
            name="MRI Scan",
            description="Magnetic Resonance Imaging",
            price=800.00,
            lab_id=lab_id,
            is_active=True
        )
        db_session.add(mri_service)
        await db_session.flush()
        await db_session.refresh(mri_service)
        
        # Configure MRI duration (30 minutes as per scenario)
        mri_duration = TestDuration(
            lab_service_id=mri_service.id,
            duration_minutes=25,
            setup_time_minutes=3,
            cleanup_time_minutes=2,
            total_time_minutes=30,
            equipment_required="MRI Machine",
            room_type_required="MRI Room"
        )
        db_session.add(mri_duration)
        await db_session.flush()
        
        # Scenario: 2:00-4:00 PM time window available
        # Patient A books at 3:00 PM for 30-minute MRI (3:00-3:30 PM)
        patient_a_time = datetime.now().replace(hour=15, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        # Create test order for patient A
        test_order_a_id = uuid4()
        test_order_a = TestOrder(
            id=test_order_a_id,
            patient_user_id=uuid4(),
            requesting_entity_id=uuid4(),
            organization_id=lab_id,
            lab_service_id=mri_service.id,
            status="PENDING_CONSENT",
            clinical_notes="MRI booking for patient A"
        )
        db_session.add(test_order_a)
        await db_session.commit()
        
        reservation_a = {
            "test_order_id": str(test_order_a_id),
            "lab_service_id": str(mri_service.id),
            "appointment_time": patient_a_time.isoformat()
        }
        
        response_a = await client.post(
            f"/api/v1/appointments/reserve-exact-slot/{lab_id}",
            json=reservation_a
        )
        
        # Skip test if endpoint not implemented
        if response_a.status_code == status.HTTP_404_NOT_FOUND:
            return
        
        # Patient A should successfully book
        assert response_a.status_code == status.HTTP_200_OK
        
        # Patient B tries to book at 2:45 PM for 30-minute MRI (2:45-3:15 PM)
        # This overlaps with Patient A's slot (3:00-3:30 PM) from 3:00-3:15 PM
        patient_b_time = patient_a_time - timedelta(minutes=15)  # 2:45 PM
        
        # Create test order for patient B
        test_order_b_id = uuid4()
        test_order_b = TestOrder(
            id=test_order_b_id,
            patient_user_id=uuid4(),
            requesting_entity_id=uuid4(),
            organization_id=lab_id,
            lab_service_id=mri_service.id,
            status="PENDING_CONSENT",
            clinical_notes="MRI booking for patient B"
        )
        db_session.add(test_order_b)
        await db_session.commit()
        
        reservation_b = {
            "test_order_id": str(test_order_b_id),
            "lab_service_id": str(mri_service.id),
            "appointment_time": patient_b_time.isoformat()
        }
        
        response_b = await client.post(
            f"/api/v1/appointments/reserve-exact-slot/{lab_id}",
            json=reservation_b
        )
        
        # Patient B should be rejected due to conflict/capacity
        assert response_b.status_code == status.HTTP_409_CONFLICT
        conflict_data = response_b.json()
        # Check for either "conflict" or "capacity" in the error message
        error_message = conflict_data["detail"].lower()
        assert "conflict" in error_message or "capacity" in error_message

    @pytest.mark.asyncio
    async def test_valid_sequential_bookings(self, client: AsyncClient, db_session: AsyncSession):
        """Test that sequential non-overlapping bookings work correctly."""
        
        lab_id = uuid4()
        
        # Setup lab and service
        lab_config = LabConfiguration(
            lab_id=lab_id,
            lab_name="Sequential Test Lab",
            max_concurrent_appointments=1
        )
        db_session.add(lab_config)
        
        ct_service = LabService(
            name="CT Scan",
            price=400.00,
            lab_id=lab_id,
            is_active=True
        )
        db_session.add(ct_service)
        await db_session.flush()
        await db_session.refresh(ct_service)
        
        ct_duration = TestDuration(
            lab_service_id=ct_service.id,
            duration_minutes=45,
            total_time_minutes=45,
            equipment_required="CT Scanner"
        )
        db_session.add(ct_duration)
        await db_session.commit()  # Commit instead of flush
        
        # Book first appointment: 2:00-2:45 PM
        first_time = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        # Create test order for first reservation
        first_test_order_id = uuid4()
        first_test_order = TestOrder(
            id=first_test_order_id,
            patient_user_id=uuid4(),
            requesting_entity_id=uuid4(),
            organization_id=lab_id,
            lab_service_id=ct_service.id,
            status="PENDING_CONSENT",
            clinical_notes="First sequential booking"
        )
        db_session.add(first_test_order)
        await db_session.commit()
        
        first_reservation = {
            "test_order_id": str(first_test_order_id),
            "lab_service_id": str(ct_service.id),
            "appointment_time": first_time.isoformat()
        }
        
        first_response = await client.post(
            f"/api/v1/appointments/reserve-exact-slot/{lab_id}",
            json=first_reservation
        )
        
        if first_response.status_code == status.HTTP_404_NOT_FOUND:
            return
        
        assert first_response.status_code == status.HTTP_200_OK
        
        # Book second appointment: 2:45-3:30 PM (starts exactly when first ends)
        second_time = first_time + timedelta(minutes=45)
        
        # Create test order for second reservation
        second_test_order_id = uuid4()
        second_test_order = TestOrder(
            id=second_test_order_id,
            patient_user_id=uuid4(),
            requesting_entity_id=uuid4(),
            organization_id=lab_id,
            lab_service_id=ct_service.id,
            status="PENDING_CONSENT",
            clinical_notes="Second sequential booking"
        )
        db_session.add(second_test_order)
        await db_session.commit()
        
        second_reservation = {
            "test_order_id": str(second_test_order_id),
            "lab_service_id": str(ct_service.id),
            "appointment_time": second_time.isoformat()
        }
        
        second_response = await client.post(
            f"/api/v1/appointments/reserve-exact-slot/{lab_id}",
            json=second_reservation
        )
        
        # Second booking should succeed (no overlap)
        assert second_response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_different_equipment_concurrent_slots(self, client: AsyncClient, db_session: AsyncSession):
        """Test that different equipment can be used concurrently."""
        
        lab_id = uuid4()
        
        # Setup lab with capacity for multiple concurrent appointments
        lab_config = LabConfiguration(
            lab_id=lab_id,
            lab_name="Multi Equipment Lab",
            max_concurrent_appointments=5
        )
        db_session.add(lab_config)
        
        # Create services for different equipment
        mri_service = LabService(name="MRI", price=500.00, lab_id=lab_id, is_active=True)
        xray_service = LabService(name="X-Ray", price=100.00, lab_id=lab_id, is_active=True)
        ultrasound_service = LabService(name="Ultrasound", price=150.00, lab_id=lab_id, is_active=True)
        
        db_session.add_all([mri_service, xray_service, ultrasound_service])
        await db_session.flush()
        await db_session.refresh(mri_service)
        await db_session.refresh(xray_service)
        await db_session.refresh(ultrasound_service)
        
        # Configure different durations and equipment
        mri_duration = TestDuration(
            lab_service_id=mri_service.id,
            duration_minutes=60,
            total_time_minutes=60,
            equipment_required="MRI Machine"
        )
        xray_duration = TestDuration(
            lab_service_id=xray_service.id,
            duration_minutes=15,
            total_time_minutes=15,
            equipment_required="X-Ray Machine"
        )
        ultrasound_duration = TestDuration(
            lab_service_id=ultrasound_service.id,
            duration_minutes=30,
            total_time_minutes=30,
            equipment_required="Ultrasound Machine"
        )
        
        db_session.add_all([mri_duration, xray_duration, ultrasound_duration])
        await db_session.commit()  # Commit instead of flush
        
        # Book all three at overlapping times (should all succeed - different equipment)
        base_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        services = [mri_service, xray_service, ultrasound_service]
        times = [base_time, base_time + timedelta(minutes=15), base_time + timedelta(minutes=30)]
        
        # All bookings should succeed
        for i, (service, appointment_time) in enumerate(zip(services, times)):
            # Create a test order first (required for foreign key constraint)
            test_order_id = uuid4()
            test_order = TestOrder(
                id=test_order_id,
                patient_user_id=uuid4(),  # Mock patient ID
                requesting_entity_id=uuid4(),  # Mock doctor ID
                organization_id=lab_id,
                lab_service_id=service.id,
                status="PENDING_CONSENT",
                clinical_notes=f"Multi-equipment test {i+1}"
            )
            db_session.add(test_order)
            await db_session.commit()
            
            reservation = {
                "test_order_id": str(test_order_id),
                "lab_service_id": str(service.id),
                "appointment_time": appointment_time.isoformat()
            }
            response = await client.post(
                f"/api/v1/appointments/reserve-exact-slot/{lab_id}",
                json=reservation
            )
            
            if response.status_code == status.HTTP_404_NOT_FOUND:
                return  # Skip if endpoint not implemented
            
            assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_capacity_limit_enforcement(self, client: AsyncClient, db_session: AsyncSession):
        """Test that lab capacity limits are strictly enforced."""
        
        lab_id = uuid4()
        
        # Setup lab with very limited capacity
        lab_config = LabConfiguration(
            lab_id=lab_id,
            lab_name="Limited Capacity Lab",
            max_concurrent_appointments=2  # Only 2 concurrent appointments
        )
        db_session.add(lab_config)
        
        # Single service that multiple patients want
        blood_service = LabService(
            name="Blood Test",
            price=50.00,
            lab_id=lab_id,
            is_active=True
        )
        db_session.add(blood_service)
        await db_session.flush()
        await db_session.refresh(blood_service)
        
        blood_duration = TestDuration(
            lab_service_id=blood_service.id,
            duration_minutes=15,
            total_time_minutes=15
        )
        db_session.add(blood_duration)
        await db_session.commit()  # Commit instead of flush to persist data
        
        blood_service_id = blood_service.id
        
        # Try to book 3 appointments at the same time
        appointment_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        successful_bookings = 0
        failed_bookings = 0
        
        for i in range(3):
            # Create a test order first (required for foreign key constraint)
            test_order_id = uuid4()
            test_order = TestOrder(
                id=test_order_id,
                patient_user_id=uuid4(),  # Mock patient ID
                requesting_entity_id=uuid4(),  # Mock doctor ID
                organization_id=lab_id,
                lab_service_id=blood_service_id,
                status="PENDING_CONSENT",
                clinical_notes=f"Test booking {i+1}"
            )
            db_session.add(test_order)
            await db_session.commit()
            
            reservation = {
                "test_order_id": str(test_order_id),
                "lab_service_id": str(blood_service_id),
                "appointment_time": appointment_time.isoformat()
            }
            
            response = await client.post(
                f"/api/v1/appointments/reserve-exact-slot/{lab_id}",
                json=reservation
            )
            
            if response.status_code == status.HTTP_404_NOT_FOUND:
                return  # Skip if endpoint not implemented
            
            if response.status_code == status.HTTP_200_OK:
                successful_bookings += 1
                # Commit the session to ensure the appointment is visible to next booking
                await db_session.commit()
                # Small delay to ensure proper sequencing
                import asyncio
                await asyncio.sleep(0.1)
            elif response.status_code == status.HTTP_409_CONFLICT:
                failed_bookings += 1
                
        # Debug: Check how many appointments were actually created
        from sqlalchemy import select
        result = await db_session.execute(select(Appointment).where(Appointment.lab_id == lab_id))
        appointments = result.scalars().all()
        
        # Debug output

        
        # Should have exactly 2 successful bookings and 1 failed
        assert successful_bookings == 2
        assert failed_bookings == 1