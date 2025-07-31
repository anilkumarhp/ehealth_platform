import pytest
from datetime import datetime, date, time, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock

from app.services.advanced_slot_service import AdvancedSlotService, TimeSlot, BookedSlot
from app.models.lab_configuration import LabConfiguration
from app.models.test_duration import TestDuration
from app.models.appointment import Appointment, AppointmentStatusEnum


@pytest.fixture
def slot_service():
    return AdvancedSlotService()


@pytest.fixture
def sample_lab_config():
    return LabConfiguration(
        lab_id=uuid4(),
        lab_name="Test Lab",
        opening_time=time(8, 0),
        closing_time=time(18, 0),
        lunch_start=time(12, 0),
        lunch_end=time(13, 0),
        max_concurrent_appointments=5,
        slot_interval_minutes=15
    )


class TestTimeSlotGeneration:
    """Test time slot generation logic."""

    def test_generate_possible_slots_basic(self, slot_service, sample_lab_config):
        """Test basic slot generation."""
        target_date = date(2024, 1, 20)
        duration_minutes = 60
        
        slots = slot_service._generate_possible_slots(
            target_date, sample_lab_config, duration_minutes
        )
        
        assert len(slots) > 0
        first_slot = slots[0]
        assert first_slot.start_time.hour == 8
        assert first_slot.duration_minutes == 60

    def test_generate_slots_excludes_lunch(self, slot_service, sample_lab_config):
        """Test that lunch time is excluded from slots."""
        target_date = date(2024, 1, 20)
        duration_minutes = 60
        
        slots = slot_service._generate_possible_slots(
            target_date, sample_lab_config, duration_minutes
        )
        
        lunch_start = datetime.combine(target_date, time(12, 0))
        lunch_end = datetime.combine(target_date, time(13, 0))
        
        for slot in slots:
            assert not (slot.start_time < lunch_end and slot.end_time > lunch_start)


class TestConflictDetection:
    """Test appointment conflict detection."""

    def test_is_slot_available_no_conflicts(self, slot_service):
        """Test slot availability with no conflicts."""
        slot = TimeSlot(
            start_time=datetime(2024, 1, 20, 9, 0),
            end_time=datetime(2024, 1, 20, 10, 0),
            duration_minutes=60
        )
        
        available = slot_service._is_slot_available(slot, [], 5)
        assert available is True

    def test_is_slot_available_with_conflicts(self, slot_service):
        """Test slot availability with conflicts."""
        slot = TimeSlot(
            start_time=datetime(2024, 1, 20, 9, 0),
            end_time=datetime(2024, 1, 20, 10, 0),
            duration_minutes=60
        )
        
        booked_slots = [
            BookedSlot(
                start_time=datetime(2024, 1, 20, 9, 30),
                end_time=datetime(2024, 1, 20, 10, 30),
                appointment_id=uuid4(),
                test_name="MRI Scan"
            )
        ]
        
        available = slot_service._is_slot_available(slot, booked_slots, 1)
        assert available is False


@pytest.mark.asyncio
class TestSlotReservation:
    """Test slot reservation functionality."""

    async def test_reserve_exact_slot_success(self, slot_service):
        """Test successful slot reservation."""
        db_mock = AsyncMock()
        
        test_duration = TestDuration(
            duration_minutes=45,
            setup_time_minutes=10,
            cleanup_time_minutes=5,
            total_time_minutes=60
        )
        
        slot_service._get_test_duration = AsyncMock(return_value=test_duration)
        slot_service._get_overlapping_appointments = AsyncMock(return_value=[])  # No overlapping appointments
        slot_service._get_lab_configuration = AsyncMock(return_value=None)  # Will use default capacity
        
        success, message = await slot_service.reserve_exact_slot(
            db_mock, uuid4(), uuid4(), datetime(2024, 1, 20, 9, 0), uuid4(), uuid4()
        )
        
        assert success is True
        assert "successfully" in message.lower()

    async def test_reserve_exact_slot_conflict(self, slot_service):
        """Test slot reservation with conflicts."""
        db_mock = AsyncMock()
        
        test_duration = TestDuration(total_time_minutes=60)
        slot_service._get_test_duration = AsyncMock(return_value=test_duration)
        
        # Mock overlapping appointments to simulate capacity exceeded
        mock_appointments = [
            Appointment(id=uuid4(), appointment_time=datetime(2024, 1, 20, 9, 0)),
            Appointment(id=uuid4(), appointment_time=datetime(2024, 1, 20, 9, 30)),
            Appointment(id=uuid4(), appointment_time=datetime(2024, 1, 20, 10, 0)),
            Appointment(id=uuid4(), appointment_time=datetime(2024, 1, 20, 10, 30)),
            Appointment(id=uuid4(), appointment_time=datetime(2024, 1, 20, 11, 0))
        ]
        slot_service._get_overlapping_appointments = AsyncMock(return_value=mock_appointments)
        slot_service._get_lab_configuration = AsyncMock(return_value=None)  # Will use default capacity of 5
        
        success, message = await slot_service.reserve_exact_slot(
            db_mock, uuid4(), uuid4(), datetime(2024, 1, 20, 9, 0), uuid4(), uuid4()
        )
        
        assert success is False
        assert "capacity" in message.lower()