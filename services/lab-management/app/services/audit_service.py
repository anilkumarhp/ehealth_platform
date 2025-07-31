from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID
from typing import Dict, Any, Optional
import json

from app.models.audit_log import AuditLog, AuditActionEnum
from app.db.session import get_db_session

class AuditService:
    """Service for managing audit logs."""
    
    @staticmethod
    async def log_action(
        db: AsyncSession,
        user_id: UUID,
        action: AuditActionEnum,
        resource_type: str,
        resource_id: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """Log an audit action."""
        
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            table_name=resource_type,
            record_id=resource_id,
            new_values=details or {}
        )
        
        db.add(audit_log)
        await db.flush()
        
        return audit_log
    
    @staticmethod
    async def log_appointment_created(
        db: AsyncSession,
        user_id: UUID,
        appointment_id: UUID,
        appointment_data: Dict[str, Any],
        ip_address: Optional[str] = None
    ):
        """Log appointment creation."""
        return await AuditService.log_action(
            db=db,
            user_id=user_id,
            action=AuditActionEnum.CREATE,
            resource_type="appointment",
            resource_id=appointment_id,
            details={
                "appointment_datetime": appointment_data.get("appointment_datetime"),
                "lab_service_id": str(appointment_data.get("lab_service_id")),
                "patient_user_id": str(appointment_data.get("patient_user_id"))
            },
            ip_address=ip_address
        )
    
    @staticmethod
    async def log_test_order_status_change(
        db: AsyncSession,
        user_id: UUID,
        test_order_id: UUID,
        old_status: str,
        new_status: str,
        ip_address: Optional[str] = None
    ):
        """Log test order status change."""
        return await AuditService.log_action(
            db=db,
            user_id=user_id,
            action=AuditActionEnum.UPDATE,
            resource_type="test_order",
            resource_id=test_order_id,
            details={
                "status_change": {
                    "from": old_status,
                    "to": new_status
                }
            },
            ip_address=ip_address
        )
    
    @staticmethod
    async def log_file_upload(
        db: AsyncSession,
        user_id: UUID,
        file_id: UUID,
        filename: str,
        file_category: str,
        ip_address: Optional[str] = None
    ):
        """Log file upload."""
        return await AuditService.log_action(
            db=db,
            user_id=user_id,
            action=AuditActionEnum.CREATE,
            resource_type="file_attachment",
            resource_id=file_id,
            details={
                "filename": filename,
                "file_category": file_category
            },
            ip_address=ip_address
        )
    
    @staticmethod
    async def log_lab_service_access(
        db: AsyncSession,
        user_id: UUID,
        lab_service_id: UUID,
        action: AuditActionEnum,
        ip_address: Optional[str] = None
    ):
        """Log lab service access."""
        return await AuditService.log_action(
            db=db,
            user_id=user_id,
            action=action,
            resource_type="lab_service",
            resource_id=lab_service_id,
            ip_address=ip_address
        )

# Audit decorator
def audit_action(resource_type: str, action: AuditActionEnum):
    """Decorator to automatically audit actions."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract common parameters
            db = kwargs.get('db') or (args[1] if len(args) > 1 else None)
            current_user = kwargs.get('current_user')
            
            # Execute the function
            result = await func(*args, **kwargs)
            
            # Log the action if we have the required info
            if db and current_user and hasattr(result, 'id'):
                try:
                    await AuditService.log_action(
                        db=db,
                        user_id=current_user.sub,
                        action=action,
                        resource_type=resource_type,
                        resource_id=result.id
                    )
                except Exception as e:
                    # Don't fail the main operation if audit logging fails
                    print(f"Audit logging failed: {e}")
            
            return result
        return wrapper
    return decorator

audit_service = AuditService()