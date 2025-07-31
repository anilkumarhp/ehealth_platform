# app/repositories/consent_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from uuid import UUID

from app.repositories.base_repo import BaseRepository
from app.models.access_request import AccessRequest
from app.models.access_permission import AccessPermission, PermissionLevelEnum
from app.schemas.consent import AccessRequestCreate

# Schemas for type hinting in BaseRepository. We don't have update schemas yet.
class AccessRequestUpdate: pass
class AccessPermissionCreate: pass
class AccessPermissionUpdate: pass


class AccessRequestRepository(BaseRepository[AccessRequest, AccessRequestCreate, AccessRequestUpdate]):
    """
    Repository for AccessRequest database operations.
    """
    async def create_with_requester(
        self, db: AsyncSession, *, obj_in: AccessRequestCreate, requesting_entity_id: UUID
    ) -> AccessRequest:
        """
        Creates a new access request with the requester's ID.
        """
        db_obj = self.model(
            **obj_in.model_dump(),
            requesting_entity_id=requesting_entity_id,
        )
        db.add(db_obj)
        await db.flush() 
        await db.refresh(db_obj)
        return db_obj

    async def get_by_patient_id(
        self, db: AsyncSession, *, patient_user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[AccessRequest]:
        """
        Retrieves all access requests directed at a specific patient.
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


class AccessPermissionRepository(BaseRepository[AccessPermission, AccessPermissionCreate, AccessPermissionUpdate]):
    """
    Repository for AccessPermission database operations.
    """
    async def create_from_request(
        self, db: AsyncSession, *, access_request: AccessRequest, permission_level: PermissionLevelEnum
    ) -> AccessPermission:
        """
        Creates a new AccessPermission record from an approved AccessRequest.
        """
        db_obj = self.model(
            report_id=access_request.report_id,
            grantee_id=access_request.requesting_entity_id,
            granted_by_user_id=access_request.patient_user_id,
            permission_level=permission_level,
        )
        db.add(db_obj)
        # The commit will be handled by the service layer after all operations are done.
        return db_obj

    async def check_permission_exists(
        self, db: AsyncSession, *, report_id: UUID, user_id: UUID
    ) -> bool:
        """
        Checks if a user has any level of permission for a specific report.
        This is crucial for authorization checks.
        """
        statement = select(self.model).where(
            self.model.report_id == report_id,
            self.model.grantee_id == user_id
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none() is not None


# Instantiate the repositories
access_request_repo = AccessRequestRepository(AccessRequest)
access_permission_repo = AccessPermissionRepository(AccessPermission)