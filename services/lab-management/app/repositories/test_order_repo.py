# app/repositories/test_order_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.repositories.base_repo import BaseRepository
from app.models.test_order import TestOrder
from app.schemas.test_order import TestOrderCreate, TestOrderUpdate

class TestOrderRepository(BaseRepository[TestOrder, TestOrderCreate, TestOrderUpdate]):
    """
    Repository for TestOrder database operations.
    It inherits generic CRUD methods from BaseRepository.
    We can add custom query methods here if needed.
    """
    async def get_by_patient_id(
        self, db: AsyncSession, *, patient_user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[TestOrder]:
        """
        Retrieves all test orders for a specific patient.
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

    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: TestOrderCreate, patient_user_id: UUID, requesting_entity_id: UUID, organization_id: UUID
    ) -> TestOrder:
        """
        Creates a new test order with all necessary owner IDs.
        """
        db_obj = self.model(
            **obj_in.model_dump(),
            patient_user_id=patient_user_id,
            requesting_entity_id=requesting_entity_id,
            organization_id=organization_id
        )
        db.add(db_obj)
        await db.flush()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

# Instantiate the repository to be used in the application
test_order_repo = TestOrderRepository(TestOrder)