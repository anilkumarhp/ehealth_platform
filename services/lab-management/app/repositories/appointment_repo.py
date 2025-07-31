# app/repositories/appointment_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.repositories.base_repo import BaseRepository
from app.models.appointment import Appointment
from app.models.test_order import TestOrder # We need this to create an appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate

class AppointmentRepository(BaseRepository[Appointment, AppointmentCreate, AppointmentUpdate]):
    """
    Repository for Appointment database operations.
    """
    async def create_from_test_order(
        self, db: AsyncSession, *, obj_in: AppointmentCreate, test_order: TestOrder
    ) -> Appointment:
        """
        Creates a new Appointment record from a validated TestOrder.
        """
        db_obj = self.model(
            appointment_time=obj_in.appointment_time,
            test_order_id=test_order.id,
            patient_user_id=test_order.patient_user_id,
            lab_id=test_order.organization_id, # Assuming the org ID on the order is the lab
            lab_service_id=test_order.lab_service_id
        )
        db.add(db_obj)
        await db.flush() 
        await db.refresh(db_obj)
        return db_obj

    async def get_by_lab_id(
        self, db: AsyncSession, *, lab_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Appointment]:
        """
        Retrieves all appointments for a specific lab, ordered by time.
        """
        statement = (
            select(self.model)
            .where(self.model.lab_id == lab_id)
            .order_by(self.model.appointment_time.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_by_patient_id(
        self, db: AsyncSession, *, patient_user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Appointment]:
        """
        Retrieves all appointments for a specific patient, ordered by time.
        """
        statement = (
            select(self.model)
            .where(self.model.patient_user_id == patient_user_id)
            .order_by(self.model.appointment_time.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()

# Instantiate the repository
appointment_repo = AppointmentRepository(Appointment)