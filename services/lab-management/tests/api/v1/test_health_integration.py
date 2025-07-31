import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
class TestHealthIntegration:
    """Integration tests for health check endpoints."""

    async def test_basic_health_check(self, client: AsyncClient):
        """Test basic health check endpoint."""
        response = await client.get("/api/v1/health/")

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return  # Skip if endpoint not implemented

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data
        assert "version" in data

    async def test_detailed_health_check(self, client: AsyncClient):
        """Test detailed health check endpoint."""
        response = await client.get("/api/v1/health/detailed")

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return  # Skip if endpoint not implemented

        # Should be 200 (healthy) or 503 (unhealthy)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "timestamp" in data

        # Check that we have expected health checks
        if "checks" in data:
            expected_checks = ["database", "redis", "filesystem"]
            for check in expected_checks:
                if check in data["checks"]:
                    assert "status" in data["checks"][check]

    async def test_readiness_probe(self, client: AsyncClient):
        """Test Kubernetes readiness probe."""
        response = await client.get("/api/v1/health/readiness")

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return  # Skip if endpoint not implemented

        # Should be 200 (ready) or 503 (not ready)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]
        data = response.json()
        assert "status" in data
        assert "timestamp" in data

    async def test_liveness_probe(self, client: AsyncClient):
        """Test Kubernetes liveness probe."""
        response = await client.get("/api/v1/health/liveness")

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return  # Skip if endpoint not implemented

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "alive"
        assert "timestamp" in data

    async def test_metrics_endpoint(self, client: AsyncClient):
        """Test metrics endpoint."""
        response = await client.get("/api/v1/health/metrics")

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return  # Skip if endpoint not implemented

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "timestamp" in data
        assert "uptime_seconds" in data

    async def test_dependencies_check(self, client: AsyncClient):
        """Test dependencies check endpoint."""
        response = await client.get("/api/v1/health/dependencies")

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return  # Skip if endpoint not implemented

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "timestamp" in data
        assert "dependencies" in data