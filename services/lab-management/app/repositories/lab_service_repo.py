# app/repositories/lab_service_repo.py (Final Corrected Version with Eager Loading)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload # Import selectinload
from typing import List, Optional
from uuid import UUID

from app.repositories.base_repo import BaseRepository
from app.models.lab_service import LabService
from app.models.test_definition import TestDefinition
from app.schemas.lab_service import LabServiceCreate, LabServiceUpdate

class LabServiceRepository(BaseRepository[LabService, LabServiceCreate, LabServiceUpdate]):

    # --- THIS IS A FIX: Override the base 'get' method ---
    async def get(self, db: AsyncSession, id: UUID) -> Optional[LabService]:
        """
        Retrieves a single LabService and eagerly loads its test definitions.
        """
        statement = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(self.model.test_definitions)) # Eager load
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def create_with_lab_id(
        self, db: AsyncSession, *, obj_in: LabServiceCreate, lab_id: UUID
    ) -> LabService:
        """
        Creates a LabService and its associated TestDefinitions.
        """
        service_data = obj_in.model_dump(exclude={"test_definitions"})
        db_service = LabService(**service_data, lab_id=lab_id)

        for test_def_in in obj_in.test_definitions:
            db_test_def = TestDefinition(
                **test_def_in.model_dump(),
                service=db_service
            )
            db.add(db_test_def)

        db.add(db_service)
        await db.flush()
        await db.commit()  # Commit to make data available to other sessions
        
        # --- THIS IS A FIX: Refresh the object to load the eager-loaded relationship ---
        # After flushing, the relationships are not loaded yet. We need to refresh.
        # We can re-fetch it using our new eager-loading get method.
        await db.refresh(db_service)
        # To be absolutely sure the relationship is loaded, we can re-query
        refreshed_service = await self.get(db, id=db_service.id)
        return refreshed_service
        # --- END OF FIX ---

    async def get_by_lab_id(
        self, db: AsyncSession, *, lab_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[LabService]:
        """
        Retrieves all services offered by a specific lab, eagerly loading test definitions.
        """
        statement = (
            select(self.model)
            .where(self.model.lab_id == lab_id)
            .options(selectinload(self.model.test_definitions)) # Eager load
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()

lab_service_repo = LabServiceRepository(LabService)