from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict
from uuid import UUID

from app.models.audit_log import AuditLog, AuditActionEnum
from app.db.base import Base

class AuditLogRepository:
    """
    Repository for AuditLog database operations.
    This is a write-only repository.
    """
    def create(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        action: AuditActionEnum,
        table_name: str,
        record_id: UUID,
        old_values: Dict[str, Any] = None,
        new_values: Dict[str, Any] = None
    ) -> None:
        """
        Creates a new audit log entry.
        This is a 'fire-and-forget' operation from the perspective of the calling service.
        """
        db_obj = AuditLog(
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
        )
        db.add(db_obj)
        # Note: We do not commit here. The commit is handled by the calling service
        # to ensure the audit log is part of the same transaction as the main action.

# Instantiate the repository
audit_repo = AuditLogRepository()