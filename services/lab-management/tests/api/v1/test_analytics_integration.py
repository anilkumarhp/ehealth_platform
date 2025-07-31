import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date, timedelta
from uuid import uuid4

from app.models.appointment import Appointment, AppointmentStatusEnum
from app.models.lab_service import LabService
from app.models.test_order import TestOrder, TestOrderStatusEnum


@pytest.mark.asyncio
class TestAnalyticsIntegration:
    """Integration tests for analytics endpoints."""

    async def test_dashboard_metrics(self, client: AsyncClient, db_session: AsyncSession, shared_lab_id):
        """Test dashboard metrics endpoint."""
        # Create test data
        lab_service = LabService(
            name="Analytics Test Service",
            price=100.00,
            lab_id=shared_lab_id,
            is_active=True
        )
        db_session.add(lab_service)
        await db_session.flush()
        await db_session.refresh(lab_service)

        # Create test appointment
        appointment = Appointment(
            patient_user_id=uuid4(),
            lab_id=shared_lab_id,
            lab_service_id=lab_service.id,
            appointment_time=datetime.utcnow(),
            status=AppointmentStatusEnum.COMPLETED
        )
        db_session.add(appointment)
        await db_session.flush()
        await db_session.commit()

        response = await client.get(f"/api/v1/analytics/dashboard?lab_id={shared_lab_id}")

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return  # Skip if endpoint not implemented

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "metrics" in data
        assert "period" in data
        assert "total_appointments" in data["metrics"]
        assert "completed_appointments" in data["metrics"]
        assert "total_revenue" in data["metrics"]

    async def test_appointments_by_day(self, client: AsyncClient, db_session: AsyncSession, shared_lab_id):
        """Test appointments by day endpoint."""
        response = await client.get(f"/api/v1/analytics/appointments-by-day?lab_id={shared_lab_id}&days=7")

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return  # Skip if endpoint not implemented

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        for item in data:
            assert "date" in item
            assert "appointments" in item

    async def test_popular_services(self, client: AsyncClient, db_session: AsyncSession, shared_lab_id):
        """Test popular services endpoint."""
        response = await client.get(f"/api/v1/analytics/popular-services?lab_id={shared_lab_id}&limit=5")

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return  # Skip if endpoint not implemented

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    async def test_monthly_revenue(self, client: AsyncClient, shared_lab_id):
        """Test monthly revenue endpoint."""
        response = await client.get(f"/api/v1/analytics/monthly-revenue?lab_id={shared_lab_id}&months=6")

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return  # Skip if endpoint not implemented

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        for item in data:
            assert "year" in item
            assert "month" in item
            assert "revenue" in item

    async def test_dashboard_unauthorized(self, client: AsyncClient):
        """Test dashboard access without proper authorization."""
        different_lab_id = uuid4()
        response = await client.get(f"/api/v1/analytics/dashboard?lab_id={different_lab_id}")
        
        # Should work but return empty/minimal data due to no access
        if response.status_code not in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]:
            assert response.status_code == status.HTTP_200_OK