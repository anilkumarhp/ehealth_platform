# app/repositories/payment_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from uuid import UUID

from app.repositories.base_repo import BaseRepository
from app.models.payment import Payment
from app.models.appointment import Appointment # Needed to get user and service info
from app.schemas.payment import PaymentCreate, PaymentUpdate

class PaymentRepository(BaseRepository[Payment, PaymentCreate, PaymentUpdate]):
    """
    Repository for Payment database operations.
    """
    async def create_for_appointment(self, db: AsyncSession, *, appointment: Appointment) -> Payment:
        """
        Creates a new Payment record in a PENDING state for a given appointment.
        It pulls the price and currency from the appointment's related service.
        """
        # The appointment object already has the lab_service loaded via relationship
        if not appointment.service:
            # This should ideally not happen if the data is consistent
            raise Exception("Appointment is not linked to a valid service.")

        db_obj = self.model(
            appointment_id=appointment.id,
            user_id=appointment.patient_user_id,
            amount=appointment.service.price,
            currency="INR" # Assuming INR for now, could be made dynamic later
        )
        db.add(db_obj)
        await db.flush() 
        await db.refresh(db_obj)
        return db_obj

    async def get_by_appointment_id(self, db: AsyncSession, *, appointment_id: UUID) -> Optional[Payment]:
        """
        Retrieves a payment record by its associated appointment_id.
        """
        statement = select(self.model).where(self.model.appointment_id == appointment_id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()


# Instantiate the repository
payment_repo = PaymentRepository(Payment)