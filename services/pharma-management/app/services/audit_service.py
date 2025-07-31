"""
Audit service for compliance logging
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any, List, List
from uuid import UUID
import logging
from datetime import datetime, timedelta

from app.models.compliance import AuditLog
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit logging and compliance."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        pharmacy_id: Optional[UUID] = None,
        description: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        severity: str = "info"
    ) -> AuditLog:
        """Log an audit event."""
        try:
            # Calculate retention date (7 years for pharma compliance)
            retention_date = datetime.utcnow() + timedelta(days=settings.AUDIT_LOG_RETENTION_DAYS)
            
            audit_log = AuditLog(
                user_id=user_id,
                pharmacy_id=pharmacy_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                description=description,
                old_values=old_values,
                new_values=new_values,
                extra_data=extra_data,
                ip_address=ip_address,
                user_agent=user_agent,
                severity=severity,
                retention_date=retention_date,
                hipaa_logged=True
            )
            
            self.db.add(audit_log)
            await self.db.commit()
            await self.db.refresh(audit_log)
            
            logger.info(f"Audit log created: {action} on {resource_type}")
            return audit_log
            
        except Exception as e:
            logger.error(f"Error creating audit log: {e}")
            await self.db.rollback()
            raise
    
    async def log_prescription_action(
        self,
        action: str,
        prescription_id: UUID,
        user_id: Optional[UUID] = None,
        pharmacy_id: Optional[UUID] = None,
        description: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log prescription-related actions."""
        return await self.log_action(
            action=action,
            resource_type="prescription",
            resource_id=prescription_id,
            user_id=user_id,
            pharmacy_id=pharmacy_id,
            description=description,
            extra_data=extra_data,
            severity="info"
        )
    
    async def log_order_action(
        self,
        action: str,
        order_id: UUID,
        user_id: Optional[UUID] = None,
        pharmacy_id: Optional[UUID] = None,
        description: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log order-related actions."""
        return await self.log_action(
            action=action,
            resource_type="order",
            resource_id=order_id,
            user_id=user_id,
            pharmacy_id=pharmacy_id,
            description=description,
            extra_data=extra_data,
            severity="info"
        )
    
    async def log_inventory_action(
        self,
        action: str,
        inventory_id: UUID,
        user_id: Optional[UUID] = None,
        pharmacy_id: Optional[UUID] = None,
        description: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log inventory-related actions."""
        return await self.log_action(
            action=action,
            resource_type="inventory",
            resource_id=inventory_id,
            user_id=user_id,
            pharmacy_id=pharmacy_id,
            description=description,
            old_values=old_values,
            new_values=new_values,
            severity="info"
        )
        
    async def get_audit_logs(
        self,
        resource_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        action: Optional[str] = None,
        user_id: Optional[UUID] = None,
        pharmacy_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Get audit logs with optional filtering."""
        from sqlalchemy import select, and_
        
        try:
            # Build query with filters
            query = select(AuditLog)
            filters = []
            
            if resource_id:
                filters.append(AuditLog.resource_id == resource_id)
            if resource_type:
                filters.append(AuditLog.resource_type == resource_type)
            if action:
                filters.append(AuditLog.action == action)
            if user_id:
                filters.append(AuditLog.user_id == user_id)
            if pharmacy_id:
                filters.append(AuditLog.pharmacy_id == pharmacy_id)
            if start_date:
                filters.append(AuditLog.created_at >= start_date)
            if end_date:
                filters.append(AuditLog.created_at <= end_date)
            
            if filters:
                query = query.where(and_(*filters))
            
            # Add ordering and pagination
            query = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
            
            # Execute query
            result = await self.db.execute(query)
            logs = result.scalars().all()
            
            return list(logs)
            
        except Exception as e:
            logger.error(f"Error retrieving audit logs: {e}")
            return []
    
    async def get_audit_logs(
        self,
        resource_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        action: Optional[str] = None,
        user_id: Optional[UUID] = None,
        pharmacy_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Get audit logs with optional filtering."""
        from sqlalchemy import select, and_
        
        try:
            # Build query with filters
            query = select(AuditLog)
            filters = []
            
            if resource_id:
                filters.append(AuditLog.resource_id == resource_id)
            if resource_type:
                filters.append(AuditLog.resource_type == resource_type)
            if action:
                filters.append(AuditLog.action == action)
            if user_id:
                filters.append(AuditLog.user_id == user_id)
            if pharmacy_id:
                filters.append(AuditLog.pharmacy_id == pharmacy_id)
            if start_date:
                filters.append(AuditLog.created_at >= start_date)
            if end_date:
                filters.append(AuditLog.created_at <= end_date)
            
            if filters:
                query = query.where(and_(*filters))
            
            # Add ordering and pagination
            query = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
            
            # Execute query
            result = await self.db.execute(query)
            logs = result.scalars().all()
            
            return list(logs)
            
        except Exception as e:
            logger.error(f"Error retrieving audit logs: {e}")
            return []