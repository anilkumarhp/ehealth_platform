import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

from app.services.audit_service import AuditService, audit_action
from app.models.audit_log import AuditActionEnum


@pytest.mark.asyncio
class TestAuditService:
    """Unit tests for AuditService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = AsyncMock()
        self.user_id = uuid4()
        self.resource_id = uuid4()

    async def test_log_action_basic(self):
        """Test basic action logging."""
        result = await AuditService.log_action(
            db=self.mock_db,
            user_id=self.user_id,
            action=AuditActionEnum.CREATE,
            resource_type="test_resource",
            resource_id=self.resource_id,
            details={"test": "data"}
        )

        # Verify database operations
        self.mock_db.add.assert_called_once()
        self.mock_db.flush.assert_called_once()

    async def test_log_appointment_created(self):
        """Test appointment creation logging."""
        appointment_data = {
            "appointment_datetime": "2024-01-15T10:00:00",
            "lab_service_id": str(uuid4()),
            "patient_user_id": str(uuid4())
        }

        await AuditService.log_appointment_created(
            db=self.mock_db,
            user_id=self.user_id,
            appointment_id=self.resource_id,
            appointment_data=appointment_data
        )

        # Verify database operations were called
        self.mock_db.add.assert_called_once()
        self.mock_db.flush.assert_called_once()

    async def test_log_test_order_status_change(self):
        """Test test order status change logging."""
        await AuditService.log_test_order_status_change(
            db=self.mock_db,
            user_id=self.user_id,
            test_order_id=self.resource_id,
            old_status="PENDING_CONSENT",
            new_status="AWAITING_APPOINTMENT"
        )

        # Verify database operations were called
        self.mock_db.add.assert_called_once()
        self.mock_db.flush.assert_called_once()

    async def test_log_file_upload(self):
        """Test file upload logging."""
        await AuditService.log_file_upload(
            db=self.mock_db,
            user_id=self.user_id,
            file_id=self.resource_id,
            filename="test_file.pdf",
            file_category="lab_result"
        )

        # Verify database operations were called
        self.mock_db.add.assert_called_once()
        self.mock_db.flush.assert_called_once()

    async def test_log_lab_service_access(self):
        """Test lab service access logging."""
        await AuditService.log_lab_service_access(
            db=self.mock_db,
            user_id=self.user_id,
            lab_service_id=self.resource_id,
            action=AuditActionEnum.CREATE
        )

        # Verify database operations were called
        self.mock_db.add.assert_called_once()
        self.mock_db.flush.assert_called_once()

    async def test_log_action_without_optional_params(self):
        """Test logging action without optional parameters."""
        await AuditService.log_action(
            db=self.mock_db,
            user_id=self.user_id,
            action=AuditActionEnum.UPDATE,
            resource_type="test_resource"
        )

        # Should still work with minimal parameters
        self.mock_db.add.assert_called_once()
        self.mock_db.flush.assert_called_once()


@pytest.mark.asyncio
class TestAuditDecorator:
    """Unit tests for audit_action decorator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = AsyncMock()
        self.mock_user = MagicMock()
        self.mock_user.sub = uuid4()

    async def test_audit_decorator_success(self):
        """Test audit decorator on successful function execution."""
        mock_result = MagicMock()
        mock_result.id = uuid4()

        @audit_action(resource_type="test_resource", action=AuditActionEnum.CREATE)
        async def test_function(self, db, current_user):
            return mock_result

        with patch.object(AuditService, 'log_action') as mock_log:
            result = await test_function(self, db=self.mock_db, current_user=self.mock_user)

            assert result == mock_result
            mock_log.assert_called_once()

    async def test_audit_decorator_no_result_id(self):
        """Test audit decorator when result has no id attribute."""
        mock_result = "string_result"

        @audit_action(resource_type="test_resource", action=AuditActionEnum.CREATE)
        async def test_function(self, db, current_user):
            return mock_result

        with patch.object(AuditService, 'log_action') as mock_log:
            result = await test_function(self, db=self.mock_db, current_user=self.mock_user)

            assert result == mock_result
            mock_log.assert_not_called()

    async def test_audit_decorator_missing_params(self):
        """Test audit decorator with missing required parameters."""
        mock_result = MagicMock()
        mock_result.id = uuid4()

        @audit_action(resource_type="test_resource", action=AuditActionEnum.CREATE)
        async def test_function(self):
            return mock_result

        with patch.object(AuditService, 'log_action') as mock_log:
            result = await test_function(self)

            assert result == mock_result
            mock_log.assert_not_called()

    async def test_audit_decorator_exception_handling(self):
        """Test audit decorator handles audit logging exceptions gracefully."""
        mock_result = MagicMock()
        mock_result.id = uuid4()

        @audit_action(resource_type="test_resource", action=AuditActionEnum.CREATE)
        async def test_function(self, db, current_user):
            return mock_result

        with patch.object(AuditService, 'log_action') as mock_log:
            mock_log.side_effect = Exception("Audit logging failed")
            
            result = await test_function(self, db=self.mock_db, current_user=self.mock_user)
            
            assert result == mock_result
            mock_log.assert_called_once()

    async def test_audit_decorator_with_args(self):
        """Test audit decorator with positional arguments."""
        mock_result = MagicMock()
        mock_result.id = uuid4()

        @audit_action(resource_type="test_resource", action=AuditActionEnum.CREATE)
        async def test_function(self, arg1, db, current_user):
            return mock_result

        with patch.object(AuditService, 'log_action') as mock_log:
            result = await test_function(self, "test_arg", db=self.mock_db, current_user=self.mock_user)

            assert result == mock_result
            mock_log.assert_called_once()

    async def test_audit_decorator_different_action_types(self):
        """Test audit decorator with different action types."""
        mock_result = MagicMock()
        mock_result.id = uuid4()

        actions_to_test = [AuditActionEnum.CREATE, AuditActionEnum.UPDATE, AuditActionEnum.DELETE]

        for action in actions_to_test:
            @audit_action(resource_type="test_resource", action=action)
            async def test_function(self, db, current_user):
                return mock_result

            with patch.object(AuditService, 'log_action') as mock_log:
                result = await test_function(self, db=self.mock_db, current_user=self.mock_user)

                assert result == mock_result
                mock_log.assert_called_once()
                call_args = mock_log.call_args[1]
                assert call_args['action'] == action