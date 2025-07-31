import pytest
from datetime import datetime, date, time, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock

from app.services.business_rules import BusinessRulesService
from app.models.lab_service import LabService


@pytest.fixture
def business_rules():
    return BusinessRulesService()


class TestBusinessRules:
    """Test business rules validation."""

    def test_check_consent_requirements_fasting(self, business_rules):
        """Test consent requirements for fasting tests."""
        assert business_rules.check_consent_requirements("fasting_glucose") is False
        assert business_rules.check_consent_requirements("genetic_testing") is True
        assert business_rules.check_consent_requirements("hiv_test") is True

    @pytest.mark.asyncio
    async def test_validate_appointment_scheduling_past_date(self, business_rules):
        """Test appointment scheduling validation for past dates."""
        past_datetime = datetime.now() - timedelta(hours=1)
        
        result = await business_rules.validate_appointment_scheduling(
            AsyncMock(), uuid4(), past_datetime
        )
        
        assert result is False

    @pytest.mark.asyncio
    async def test_validate_appointment_scheduling_business_hours(self, business_rules):
        """Test appointment scheduling within business hours."""
        # 7 AM - too early
        early_time = datetime.now().replace(hour=7, minute=0)
        result = await business_rules.validate_appointment_scheduling(
            AsyncMock(), uuid4(), early_time
        )
        assert result is False
        
        # 6 PM - too late
        late_time = datetime.now().replace(hour=18, minute=0)
        result = await business_rules.validate_appointment_scheduling(
            AsyncMock(), uuid4(), late_time
        )
        assert result is False
        
        # 10 AM next Monday - valid
        from datetime import timedelta
        next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
        valid_time = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        result = await business_rules.validate_appointment_scheduling(
            AsyncMock(), uuid4(), valid_time
        )
        assert result is True

    def test_calculate_estimated_completion_time(self, business_rules):
        """Test completion time calculation."""
        estimated_time = business_rules.calculate_estimated_completion_time(3)
        
        # Should be current time + (3 * 30 minutes) + 20% buffer
        expected_minutes = 3 * 30 * 1.2  # 108 minutes
        time_diff = (estimated_time - datetime.utcnow()).total_seconds() / 60
        
        assert abs(time_diff - expected_minutes) < 5  # Allow 5-minute tolerance

    @pytest.mark.asyncio
    async def test_validate_test_order_eligibility_inactive_service(self, business_rules):
        """Test test order eligibility with inactive service."""
        db_mock = AsyncMock()
        
        # Mock inactive service
        inactive_service = LabService(is_active=False)
        
        # Mock the lab service service
        from app.services import lab_service_service
        lab_service_service.lab_service_service.get_service = AsyncMock(
            return_value=inactive_service
        )
        
        result = await business_rules.validate_test_order_eligibility(
            db_mock, uuid4(), uuid4()
        )
        
        assert result is False

    @pytest.mark.asyncio
    async def test_validate_test_order_eligibility_valid_service(self, business_rules):
        """Test test order eligibility with valid service."""
        db_mock = AsyncMock()
        
        # Mock active service
        active_service = LabService(is_active=True)
        
        from app.services import lab_service_service
        lab_service_service.lab_service_service.get_service = AsyncMock(
            return_value=active_service
        )
        
        result = await business_rules.validate_test_order_eligibility(
            db_mock, uuid4(), uuid4()
        )
        
        assert result is True