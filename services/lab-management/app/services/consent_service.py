# app/services/consent_service.py (Updated with Audit Trail)

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from fastapi import HTTPException, status

from app.repositories.consent_repo import access_request_repo, access_permission_repo
from app.repositories.report_repo import report_repo
from app.models.access_request import AccessRequest, AccessRequestStatusEnum
from app.models.access_permission import PermissionLevelEnum
from app.models.audit_log import AuditActionEnum # Import the audit action enum
from app.schemas.consent import AccessRequestCreate
from app.services.audit_service import audit_service # Import our new audit service

class ConsentService:
    # ... (create_access_request and get_requests_for_patient remain the same) ...
    async def create_access_request(self, db: AsyncSession, *, obj_in: AccessRequestCreate, requesting_entity_id: UUID) -> AccessRequest:
        report = await report_repo.get(db, id=obj_in.report_id)
        if not report:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Report not found.")
        if report.patient_user_id != obj_in.patient_user_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Report does not belong to the specified patient.")
        if report.patient_user_id == requesting_entity_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "You already have access to this report.")
        
        new_request = await access_request_repo.create_with_requester(db, obj_in=obj_in, requesting_entity_id=requesting_entity_id)
        
        # --- Log the creation of the request ---
        audit_service.log_action(
            db=db,
            user_id=requesting_entity_id,
            action=AuditActionEnum.CREATE,
            record=new_request,
            new_values=obj_in.model_dump(mode='json')
        )
        await db.commit()
        await db.refresh(new_request)
        return new_request

    async def get_requests_for_patient(self, db: AsyncSession, *, patient_user_id: UUID, skip: int = 0, limit: int = 100) -> List[AccessRequest]:
        return await access_request_repo.get_by_patient_id(db, patient_user_id=patient_user_id, skip=skip, limit=limit)

    # --- THIS METHOD IS UPDATED ---
    async def approve_request(
        self, db: AsyncSession, *, request_id: UUID, approving_user_id: UUID
    ) -> AccessRequest:
        """
        Approves an access request and creates the corresponding permission and audit log.
        """
        access_request = await access_request_repo.get(db, id=request_id)
        if not access_request:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Access request not found.")
        if access_request.status != AccessRequestStatusEnum.PENDING:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "This request is no longer pending.")
        if access_request.patient_user_id != approving_user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to approve this request.")

        # Store old state for audit log
        old_status = access_request.status.value

        # Update request status and create permission
        access_request.status = AccessRequestStatusEnum.APPROVED
        db.add(access_request)
        await access_permission_repo.create_from_request(
            db, access_request=access_request, permission_level=PermissionLevelEnum.VIEW_AND_DOWNLOAD
        )

        # --- Log the approval action ---
        audit_service.log_action(
            db=db,
            user_id=approving_user_id,
            action=AuditActionEnum.UPDATE,
            record=access_request,
            old_values={"status": old_status},
            new_values={"status": access_request.status.value}
        )

        # await db.commit()
        await db.refresh(access_request)
        return access_request

    # --- THIS METHOD IS UPDATED ---
    async def deny_request(
        self, db: AsyncSession, *, request_id: UUID, denying_user_id: UUID
    ) -> AccessRequest:
        """
        Denies an access request and creates an audit log.
        """
        access_request = await access_request_repo.get(db, id=request_id)
        if not access_request:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Access request not found.")
        if access_request.status != AccessRequestStatusEnum.PENDING:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "This request is no longer pending.")
        if access_request.patient_user_id != denying_user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to deny this request.")

        old_status = access_request.status.value
        
        access_request.status = AccessRequestStatusEnum.DENIED
        db.add(access_request)

        # --- Log the denial action ---
        audit_service.log_action(
            db=db,
            user_id=denying_user_id,
            action=AuditActionEnum.UPDATE,
            record=access_request,
            old_values={"status": old_status},
            new_values={"status": access_request.status.value}
        )

        # await db.commit()
        await db.refresh(access_request)
        return access_request

# Instantiate the service
consent_service = ConsentService()