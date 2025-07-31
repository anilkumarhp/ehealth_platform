from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status

from app.models.appointment import Appointment, AppointmentStatusEnum
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.core.security import TokenPayload


class AppointmentService:
    """Service for managing appointments."""

    async def create_appointment(
        self,
        db: AsyncSession,
        test_order_id: UUID,
        patient_user_id: UUID,
        lab_service_id: UUID,
        appointment_datetime: str,
        lab_id: UUID
    ) -> Appointment:
        """Create a new appointment."""
        
        appointment_data = AppointmentCreate(
            test_order_id=test_order_id,
            patient_user_id=patient_user_id,
            lab_service_id=lab_service_id,
            appointment_datetime=appointment_datetime,
            lab_id=lab_id,
            status=AppointmentStatusEnum.SCHEDULED
        )
        
        appointment = Appointment(**appointment_data.dict())
        db.add(appointment)
        await db.flush()
        await db.refresh(appointment)
        
        return appointment

    async def get_appointment(
        self,
        db: AsyncSession,
        appointment_id: UUID
    ) -> Optional[Appointment]:
        """Get appointment by ID."""
        
        result = await db.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        return result.scalar_one_or_none()

    async def get_appointments_by_patient(
        self,
        db: AsyncSession,
        patient_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Appointment]:
        """Get appointments for a patient."""
        
        result = await db.execute(
            select(Appointment)
            .where(Appointment.patient_user_id == patient_id)
            .offset(skip)
            .limit(limit)
            .order_by(Appointment.appointment_datetime.desc())
        )
        return result.scalars().all()

    async def get_appointments_by_lab(
        self,
        db: AsyncSession,
        lab_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Appointment]:
        """Get appointments for a lab."""
        
        result = await db.execute(
            select(Appointment)
            .where(Appointment.lab_id == lab_id)
            .offset(skip)
            .limit(limit)
            .order_by(Appointment.appointment_datetime.desc())
        )
        return result.scalars().all()

    async def get_appointments_in_timerange(
        self,
        db: AsyncSession,
        lab_id: UUID,
        start_time: datetime,
        end_time: datetime
    ) -> List[Appointment]:
        """Get appointments in a specific time range."""
        
        result = await db.execute(
            select(Appointment)
            .where(
                and_(
                    Appointment.lab_id == lab_id,
                    Appointment.appointment_datetime >= start_time,
                    Appointment.appointment_datetime < end_time
                )
            )
        )
        return result.scalars().all()

    async def update_appointment_status(
        self,
        db: AsyncSession,
        appointment_id: UUID,
        new_status: AppointmentStatusEnum,
        completion_notes: Optional[str] = None
    ) -> Appointment:
        """Update appointment status."""
        
        appointment = await self.get_appointment(db, appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        appointment.status = new_status
        if completion_notes:
            appointment.completion_notes = completion_notes
        
        await db.flush()
        await db.refresh(appointment)
        
        return appointment

    async def cancel_appointment(
        self,
        db: AsyncSession,
        appointment_id: UUID,
        current_user: TokenPayload
    ) -> Appointment:
        """Cancel an appointment."""
        
        appointment = await self.get_appointment(db, appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        # Check permissions
        if (appointment.patient_user_id != current_user.sub and 
            current_user.org_id != appointment.lab_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        
        appointment.status = AppointmentStatusEnum.CANCELLED
        await db.flush()
        await db.refresh(appointment)
        
        return appointment

    async def get_appointment_by_details(
        self,
        db: AsyncSession,
        lab_id: UUID,
        patient_id: UUID,
        appointment_datetime: datetime
    ) -> Optional[Appointment]:
        """Get appointment by specific details."""
        
        result = await db.execute(
            select(Appointment)
            .where(
                and_(
                    Appointment.lab_id == lab_id,
                    Appointment.patient_user_id == patient_id,
                    Appointment.appointment_datetime == appointment_datetime
                )
            )
        )
        return result.scalar_one_or_none()


# Singleton instance
appointment_service = AppointmentService()