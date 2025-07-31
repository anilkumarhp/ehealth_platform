# app/repositories/report_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from uuid import UUID

from app.repositories.base_repo import BaseRepository
from app.models.report import Report
from app.models.appointment import Appointment
from app.schemas.report import ReportCreate, ReportUpdate # ReportUpdate is not defined yet, but we can plan for it

class ReportRepository(BaseRepository[Report, ReportCreate, ReportUpdate]):
    """
    Repository for Report database operations.
    """
    async def create_for_appointment(
        self,
        db: AsyncSession,
        *,
        obj_in: ReportCreate,
        appointment: Appointment,
        storage_key: str,
        bucket_name: str
    ) -> Report:
        """
        Creates a new Report record and links it to an appointment.
        """
        db_obj = self.model(
            **obj_in.model_dump(exclude={"appointment_id"}), # appointment_id is already in the appointment object
            appointment_id=appointment.id,
            patient_user_id=appointment.patient_user_id,
            uploading_lab_id=appointment.lab_id,
            storage_key=storage_key,
            storage_bucket=bucket_name
        )
        db.add(db_obj)
        await db.flush() 
        await db.refresh(db_obj)
        return db_obj

    async def get_by_patient_id(
        self, db: AsyncSession, *, patient_user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """
        Retrieves all reports for a specific patient.
        """
        statement = (
            select(self.model)
            .where(self.model.patient_user_id == patient_user_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_by_appointment_id(self, db: AsyncSession, *, appointment_id: UUID) -> Optional[Report]:
        """
        Retrieves a report by its associated appointment_id.
        """
        statement = select(self.model).where(self.model.appointment_id == appointment_id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()


# Instantiate the repository
report_repo = ReportRepository(Report)