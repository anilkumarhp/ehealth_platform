# app/services/lab_service_service.py (Updated with Authorization)

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status

from app.repositories.lab_service_repo import lab_service_repo
from app.models.lab_service import LabService
from app.schemas.lab_service import LabServiceCreate, LabServiceUpdate
from app.core.security import TokenPayload # Import TokenPayload for type hinting

class LabServiceService:
    # ... (create_service and get methods remain the same) ...
    async def create_service(
        self, db: AsyncSession, *, obj_in: LabServiceCreate, lab_id: UUID
    ) -> LabService:
        return await lab_service_repo.create_with_lab_id(db, obj_in=obj_in, lab_id=lab_id)

    async def get_service_by_id(self, db: AsyncSession, *, service_id: UUID) -> Optional[LabService]:
        service = await lab_service_repo.get(db, id=service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lab service not found.",
            )
        return service

    async def get_services_by_lab(
        self, db: AsyncSession, *, lab_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[LabService]:
        return await lab_service_repo.get_by_lab_id(db, lab_id=lab_id, skip=skip, limit=limit)


    # --- THIS METHOD IS UPDATED ---
    async def update_service(
        self, db: AsyncSession, *, service_id: UUID, obj_in: LabServiceUpdate, current_user: TokenPayload
    ) -> LabService:
        """
        Updates an existing lab service after checking for ownership permission.
        """
        db_service = await self.get_service_by_id(db, service_id=service_id)

        # --- Authorization Check ---
        # The user's organization ID from the token must match the lab_id of the service.
        if db_service.lab_id != current_user.org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this service.",
            )
        # --- End of Authorization Check ---

        return await lab_service_repo.update(db, db_obj=db_service, obj_in=obj_in)

    async def delete_service(
        self, db: AsyncSession, *, service_id: UUID, current_user: TokenPayload
    ) -> LabService:
        """
        Deletes a lab service after checking for ownership permission.
        """
        db_service = await self.get_service_by_id(db, service_id=service_id)

        # --- Authorization Check ---
        if db_service.lab_id != current_user.org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this service.",
            )
        # --- End of Authorization Check ---
        
        return await lab_service_repo.remove(db, id=service_id)


# Instantiate the service
lab_service_service = LabServiceService()