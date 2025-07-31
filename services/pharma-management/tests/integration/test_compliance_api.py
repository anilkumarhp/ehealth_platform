"""
Integration tests for compliance API endpoints
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4

class TestComplianceAPI:
    """Test compliance API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_audit_logs(self, client: AsyncClient, test_pharmacy):
        """Test retrieving audit logs via API."""
        response = await client.get(f"/api/v1/compliance/audit-logs?resource_id={test_pharmacy.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_audit_logs_by_action(self, client: AsyncClient):
        """Test retrieving audit logs filtered by action."""
        response = await client.get("/api/v1/compliance/audit-logs?action=pharmacy_create")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert data[0]["action"] == "pharmacy_create"
    
    @pytest.mark.asyncio
    async def test_get_controlled_substances_report(self, client: AsyncClient):
        """Test retrieving controlled substances report."""
        response = await client.get("/api/v1/compliance/reports/controlled-substances")
        
        assert response.status_code == 200
        data = response.json()
        assert "report_date" in data
        assert "substances" in data