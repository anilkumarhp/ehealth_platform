from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, date, time, timedelta
from enum import Enum

from app.models.appointment import Appointment, AppointmentStatusEnum
from app.models.lab_service import LabService


class SlotDuration(Enum):
    """Standard appointment slot durations."""
    QUICK_TEST = 15  # Blood draw, urine sample
    STANDARD_TEST = 30  # Most lab tests
    COMPLEX_TEST = 60  # Comprehensive panels
    IMAGING = 45  # X-ray, ultrasound


class LabCapacity(Enum):
    """Lab capacity configurations."""
    SMALL_LAB = 2  # 2 concurrent appointments
    MEDIUM_LAB = 5  # 5 concurrent appointments  
    LARGE_LAB = 10  # 10 concurrent appointments


class SlotManagementService:
    """Advanced slot management for lab appointments."""

    def __init__(self):
        # Lab operating hours
        self.operating_hours = {
            "start": time(8, 0),  # 8:00 AM
            "end": time(18, 0),   # 6:00 PM
            "lunch_start": time(12, 0),  # 12:00 PM
            "lunch_end": time(13, 0)     # 1:00 PM
        }
        
        # Default lab capacities (can be configured per lab)
        self.default_capacity = LabCapacity.MEDIUM_LAB.value

    async def get_available_slots(
        self,
        db: AsyncSession,
        lab_id: UUID,
        target_date: date,
        test_duration_minutes: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all available appointment slots for a specific date."""
        
        # Get lab capacity and existing appointments
        lab_capacity = await self._get_lab_capacity(db, lab_id)
        existing_appointments = await self._get_existing_appointments(db, lab_id, target_date)
        
        # Generate time slots
        time_slots = self._generate_time_slots(
            target_date, 
            test_duration_minutes or SlotDuration.STANDARD_TEST.value
        )
        
        # Check availability for each slot
        available_slots = []
        for slot in time_slots:
            slot_info = await self._check_slot_availability(
                slot, existing_appointments, lab_capacity, test_duration_minutes
            )
            if slot_info["available"]:
                available_slots.append(slot_info)
        
        return available_slots

    async def get_next_available_slot(
        self,
        db: AsyncSession,
        lab_id: UUID,
        preferred_date: Optional[date] = None,
        test_duration_minutes: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Find the next available appointment slot."""
        
        start_date = preferred_date or date.today()
        
        # Search for next 14 days
        for days_ahead in range(14):
            check_date = start_date + timedelta(days=days_ahead)
            
            # Skip weekends
            if check_date.weekday() >= 5:
                continue
            
            available_slots = await self.get_available_slots(
                db, lab_id, check_date, test_duration_minutes
            )
            
            if available_slots:
                return available_slots[0]  # Return first available slot
        
        return None

    async def reserve_slot(
        self,
        db: AsyncSession,
        lab_id: UUID,
        slot_datetime: datetime,
        patient_id: UUID,
        test_order_id: UUID,
        lab_service_id: UUID
    ) -> bool:
        """Reserve a specific time slot."""
        
        # Double-check availability
        is_available = await self._is_slot_still_available(
            db, lab_id, slot_datetime
        )
        
        if not is_available:
            return False
        
        # Create appointment to reserve slot
        appointment = Appointment(
            test_order_id=test_order_id,
            patient_user_id=patient_id,
            lab_service_id=lab_service_id,
            lab_id=lab_id,
            appointment_datetime=slot_datetime,
            status=AppointmentStatusEnum.SCHEDULED
        )
        
        db.add(appointment)
        await db.flush()
        
        return True

    async def get_optimal_slots_for_test(
        self,
        db: AsyncSession,
        lab_id: UUID,
        lab_service_id: UUID,
        preferred_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get optimal slots based on test requirements."""
        
        # Get test service details
        service = await self._get_lab_service(db, lab_service_id)
        if not service:
            return []
        
        # Determine test duration based on complexity
        test_duration = self._calculate_test_duration(service)
        
        # Get available slots
        target_date = preferred_date or date.today()
        available_slots = await self.get_available_slots(
            db, lab_id, target_date, test_duration
        )
        
        # Add test-specific recommendations
        for slot in available_slots:
            slot["recommended_for_test"] = self._is_optimal_time_for_test(
                slot["datetime"], service
            )
            slot["test_duration_minutes"] = test_duration
        
        # Sort by recommendation and time
        available_slots.sort(
            key=lambda x: (not x["recommended_for_test"], x["datetime"])
        )
        
        return available_slots

    def _generate_time_slots(
        self, 
        target_date: date, 
        duration_minutes: int
    ) -> List[datetime]:
        """Generate all possible time slots for a date."""
        
        slots = []
        current_time = datetime.combine(target_date, self.operating_hours["start"])
        end_time = datetime.combine(target_date, self.operating_hours["end"])
        lunch_start = datetime.combine(target_date, self.operating_hours["lunch_start"])
        lunch_end = datetime.combine(target_date, self.operating_hours["lunch_end"])
        
        while current_time + timedelta(minutes=duration_minutes) <= end_time:
            # Skip lunch hour
            if not (lunch_start <= current_time < lunch_end):
                slots.append(current_time)
            
            # Move to next slot (15-minute intervals)
            current_time += timedelta(minutes=15)
        
        return slots

    async def _check_slot_availability(
        self,
        slot_datetime: datetime,
        existing_appointments: List[Appointment],
        lab_capacity: int,
        duration_minutes: Optional[int]
    ) -> Dict[str, Any]:
        """Check if a specific slot is available."""
        
        slot_end = slot_datetime + timedelta(minutes=duration_minutes or 30)
        
        # Count overlapping appointments
        overlapping_count = 0
        for appointment in existing_appointments:
            appt_start = appointment.appointment_datetime
            appt_end = appt_start + timedelta(minutes=30)  # Default duration
            
            # Check for overlap
            if (slot_datetime < appt_end and slot_end > appt_start):
                overlapping_count += 1
        
        available = overlapping_count < lab_capacity
        
        return {
            "datetime": slot_datetime.isoformat(),
            "available": available,
            "capacity_used": overlapping_count,
            "capacity_total": lab_capacity,
            "duration_minutes": duration_minutes or 30
        }

    async def _get_existing_appointments(
        self,
        db: AsyncSession,
        lab_id: UUID,
        target_date: date
    ) -> List[Appointment]:
        """Get all existing appointments for a lab on a specific date."""
        
        start_datetime = datetime.combine(target_date, time.min)
        end_datetime = datetime.combine(target_date, time.max)
        
        result = await db.execute(
            select(Appointment)
            .where(
                and_(
                    Appointment.lab_id == lab_id,
                    Appointment.appointment_datetime >= start_datetime,
                    Appointment.appointment_datetime <= end_datetime,
                    Appointment.status.in_([
                        AppointmentStatusEnum.SCHEDULED,
                        AppointmentStatusEnum.IN_PROGRESS
                    ])
                )
            )
        )
        
        return result.scalars().all()

    async def _get_lab_capacity(self, db: AsyncSession, lab_id: UUID) -> int:
        """Get lab capacity (could be stored in lab configuration table)."""
        # For now, return default capacity
        # In future, this could query a lab_configuration table
        return self.default_capacity

    async def _get_lab_service(self, db: AsyncSession, service_id: UUID) -> Optional[LabService]:
        """Get lab service details."""
        result = await db.execute(
            select(LabService).where(LabService.id == service_id)
        )
        return result.scalar_one_or_none()

    def _calculate_test_duration(self, service: LabService) -> int:
        """Calculate test duration based on service complexity."""
        
        if not service.test_definitions:
            return SlotDuration.STANDARD_TEST.value
        
        test_count = len(service.test_definitions)
        
        if test_count <= 2:
            return SlotDuration.QUICK_TEST.value
        elif test_count <= 5:
            return SlotDuration.STANDARD_TEST.value
        else:
            return SlotDuration.COMPLEX_TEST.value

    def _is_optimal_time_for_test(self, slot_datetime: datetime, service: LabService) -> bool:
        """Determine if time slot is optimal for specific test type."""
        
        slot_time = slot_datetime.time()
        
        # Fasting tests are better in the morning
        if service.name and "fasting" in service.name.lower():
            return slot_time <= time(10, 0)
        
        # Glucose tests better in morning
        if service.name and "glucose" in service.name.lower():
            return slot_time <= time(11, 0)
        
        # Most tests are fine anytime during operating hours
        return True

    async def _is_slot_still_available(
        self,
        db: AsyncSession,
        lab_id: UUID,
        slot_datetime: datetime
    ) -> bool:
        """Final check if slot is still available before reservation."""
        
        # Check for any appointments in the same time slot
        result = await db.execute(
            select(func.count(Appointment.id))
            .where(
                and_(
                    Appointment.lab_id == lab_id,
                    Appointment.appointment_datetime == slot_datetime,
                    Appointment.status.in_([
                        AppointmentStatusEnum.SCHEDULED,
                        AppointmentStatusEnum.IN_PROGRESS
                    ])
                )
            )
        )
        
        count = result.scalar()
        lab_capacity = await self._get_lab_capacity(db, lab_id)
        
        return count < lab_capacity


# Singleton instance
slot_management_service = SlotManagementService()