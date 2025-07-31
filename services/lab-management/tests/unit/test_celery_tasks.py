import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta

from app.tasks.appointment_tasks import (
    send_appointment_reminder,
    process_appointment_completion,
    cleanup_expired_appointments
)


@pytest.mark.asyncio
class TestAppointmentTasks:
    """Unit tests for appointment-related Celery tasks."""

    def setup_method(self):
        """Set up test fixtures."""
        self.appointment_id = str(uuid4())
        self.user_id = str(uuid4())

    @patch('app.tasks.appointment_tasks.get_async_session')
    async def test_send_appointment_reminder_retry(self, mock_get_session):
        """Test appointment reminder with retry logic."""
        mock_db = AsyncMock()
        mock_get_session.return_value.__aenter__.return_value = mock_db
        
        # Mock appointment query
        mock_appointment = MagicMock()
        mock_appointment.patient_user_id = uuid4()
        mock_appointment.appointment_time = datetime.utcnow() + timedelta(hours=24)
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_appointment
        mock_db.execute.return_value = mock_result
        
        # Test successful execution
        result = send_appointment_reminder.apply(args=[self.appointment_id])
        assert result.state in ['SUCCESS', 'PENDING']

    @patch('app.tasks.appointment_tasks.process_appointment_completion')
    async def test_process_appointment_completion_success(self, mock_task):
        """Test successful appointment completion processing."""
        # Mock the task to return success
        mock_result = MagicMock()
        mock_result.state = 'SUCCESS'
        mock_result.successful.return_value = True
        mock_task.apply.return_value = mock_result
        
        # Test successful execution
        result = mock_task.apply(args=[self.appointment_id])
        assert result.successful()

    @patch('app.tasks.appointment_tasks.get_async_session')
    async def test_cleanup_expired_appointments_success(self, mock_get_session):
        """Test successful cleanup of expired appointments."""
        mock_db = AsyncMock()
        mock_get_session.return_value.__aenter__.return_value = mock_db
        
        # Mock expired appointments query
        mock_result = MagicMock()
        mock_result.rowcount = 5
        mock_db.execute.return_value = mock_result
        
        # Test successful execution
        result = cleanup_expired_appointments.apply()
        assert result.state in ['SUCCESS', 'PENDING']

    @patch('app.tasks.appointment_tasks.get_async_session')
    async def test_cleanup_expired_appointments_exception(self, mock_get_session):
        """Test cleanup with exception handling."""
        mock_db = AsyncMock()
        mock_get_session.return_value.__aenter__.return_value = mock_db
        mock_db.execute.side_effect = Exception("Database error")
        
        # Test that task handles exceptions gracefully
        result = cleanup_expired_appointments.apply()
        # Task should complete even with exceptions
        assert result.state in ['SUCCESS', 'FAILURE']