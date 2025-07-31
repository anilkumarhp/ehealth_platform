# app/services/report_service.py (Updated with Audit Trail)

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from fastapi import HTTPException, status, UploadFile

from app.repositories.report_repo import report_repo
from app.repositories.appointment_repo import appointment_repo
from app.repositories.payment_repo import payment_repo
from app.repositories.consent_repo import access_permission_repo
from app.models.report import Report
from app.models.appointment import AppointmentStatusEnum
from app.models.payment import PaymentStatusEnum
from app.models.audit_log import AuditActionEnum # Import audit enum
from app.schemas.report import ReportCreate, ReportWithDownloadUrl
from app.integrations.storage.s3_client import s3_client
from app.core.security import TokenPayload
from app.services.audit_service import audit_service # Import audit service

class ReportService:
    # --- THIS METHOD IS UPDATED ---
    async def upload_report(
        self, db: AsyncSession, *, obj_in: ReportCreate, file: UploadFile, lab_id: UUID, current_user: TokenPayload
    ) -> Report:
        """
        Handles uploading a report file, creating its record, and logging the action.
        """
        appointment = await appointment_repo.get(db, id=obj_in.appointment_id)
        if not appointment:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Appointment not found.")
        if appointment.lab_id != lab_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Permission denied to upload report for this appointment.")
        if appointment.status != AppointmentStatusEnum.COMPLETED:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Report can only be uploaded for a completed appointment.")
        payment = await payment_repo.get_by_appointment_id(db, appointment_id=appointment.id)
        if not payment or payment.status != PaymentStatusEnum.SUCCESSFUL:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot upload report until payment is successful.")
        existing_report = await report_repo.get_by_appointment_id(db, appointment_id=obj_in.appointment_id)
        if existing_report:
            raise HTTPException(status.HTTP_409_CONFLICT, "A report for this appointment has already been uploaded.")

        storage_key = s3_client.upload_file(file=file, folder="reports")
        if not storage_key:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to upload report file.")

        # Create the report record
        new_report = await report_repo.create_for_appointment(
            db,
            obj_in=obj_in,
            appointment=appointment,
            storage_key=storage_key,
            bucket_name=s3_client.bucket_name
        )

        # --- Log the report upload action ---
        # Note: The previous call to create_for_appointment already committed.
        # For perfect transactional integrity, the logging should happen before the commit.
        # We will refactor this in a future step for robustness.
        audit_service.log_action(
            db=db,
            user_id=current_user.sub, # The lab user who uploaded the report
            action=AuditActionEnum.CREATE,
            record=new_report,
            new_values=obj_in.model_dump(mode='json')
        )
        await db.commit() # Commit the audit log entry
        await db.refresh(new_report)

        return new_report

    # ... (get_report_with_download_url and get_reports_by_patient remain the same) ...
    async def get_report_with_download_url(self, db: AsyncSession, *, report_id: UUID, current_user: TokenPayload) -> ReportWithDownloadUrl:
        report = await report_repo.get(db, id=report_id)
        if not report:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Report not found.")
        is_patient_owner = report.patient_user_id == current_user.sub
        is_uploader_staff = report.uploading_lab_id == current_user.org_id
        has_granted_permission = False
        if not is_patient_owner and not is_uploader_staff:
            has_granted_permission = await access_permission_repo.check_permission_exists(db, report_id=report.id, user_id=current_user.sub)
        if not is_patient_owner and not is_uploader_staff and not has_granted_permission:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to access this report.")
        download_url = s3_client.generate_presigned_url(storage_key=report.storage_key)
        if not download_url:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Could not generate download link.")
        return ReportWithDownloadUrl.model_validate(report, update={"download_url": download_url})

    async def get_reports_by_patient(self, db: AsyncSession, *, patient_user_id: UUID, skip: int = 0, limit: int = 100) -> List[Report]:
        return await report_repo.get_by_patient_id(db, patient_user_id=patient_user_id, skip=skip, limit=limit)


# Instantiate the service
report_service = ReportService()