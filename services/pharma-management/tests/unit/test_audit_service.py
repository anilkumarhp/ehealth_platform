"""
Unit tests for audit service
"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select

from app.services.audit_service import AuditService
from app.models.compliance import AuditLog

class TestAuditService:
    """Test audit service operations."""
    
    @pytest.mark.asyncio
    async def test_log_action_success(self, db_session: AsyncSession):
        """Test successful audit logging."""
        service = AuditService(db_session)
        
        # Log an action
        resource_id = uuid4()
        audit_log = await service.log_action(
            action="test_action",
            resource_type="test_resource",
            resource_id=resource_id,
            description="Test audit log",
            extra_data={"test_key": "test_value"}
        )
        
        # Verify log was created by checking the returned object
        assert audit_log is not None
        assert audit_log.action == "test_action"
        assert audit_log.resource_type == "test_resource"
        assert audit_log.description == "Test audit log"
    
    @pytest.mark.asyncio
    async def test_get_audit_logs(self, db_session: AsyncSession):
        """Test retrieving audit logs."""
        service = AuditService(db_session)
        resource_id = uuid4()
        
        # Create multiple logs
        for i in range(3):
            await service.log_action(
                action=f"test_action_{i}",
                resource_type="test_resource",
                resource_id=resource_id,
                description=f"Test audit log {i}"
            )
        
        # Get logs for resource
        logs = await service.get_audit_logs(resource_id=resource_id)
        
        assert len(logs) == 3
        assert str(logs[0].resource_id) == str(resource_id)
        assert logs[0].action.startswith("test_action_")