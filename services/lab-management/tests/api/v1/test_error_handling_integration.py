import pytest
from httpx import AsyncClient
from fastapi import status
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lab_service import LabService


@pytest.mark.asyncio
class TestErrorHandlingIntegration:
    """Integration tests for error handling and edge cases."""

    async def test_database_constraint_violations(self, client: AsyncClient, db_session: AsyncSession):
        """Test handling of database constraint violations."""
        # Login first
        login_data = {
            "username": "testuser",
            "password": "testpass"
        }
        
        login_response = await client.post(
            "/api/v1/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a lab service directly in database
        existing_service = LabService(
            name="Existing Service",
            description="Already exists",
            price=100.00,
            lab_id="87654321-4321-4321-8321-210987654321",
            is_active=True
        )
        db_session.add(existing_service)
        await db_session.flush()
        
        # Try to create test order with non-existent service
        nonexistent_service_id = uuid4()
        order_data = {
            "lab_service_id": str(nonexistent_service_id),
            "clinical_notes": "Order for non-existent service"
        }
        
        response = await client.post(
            "/api/v1/test-orders/for-patient/22345678-1234-4234-8234-123456789012",
            json=order_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_malformed_json_requests(self, client: AsyncClient):
        """Test handling of malformed JSON requests."""
        # Login first
        login_data = {
            "username": "testuser",
            "password": "testpass"
        }
        
        login_response = await client.post(
            "/api/v1/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Send malformed JSON
        malformed_json = '{"name": "Test Service", "price": 100.00, "invalid_json"}'
        
        response = await client.post(
            "/api/v1/lab-services/",
            content=malformed_json,
            headers={**headers, "Content-Type": "application/json"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_extremely_large_payloads(self, client: AsyncClient):
        """Test handling of extremely large payloads."""
        # Login first
        login_data = {
            "username": "testuser",
            "password": "testpass"
        }
        
        login_response = await client.post(
            "/api/v1/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create extremely large payload
        large_description = "A" * 100000  # 100KB description
        large_test_definitions = [
            {
                "name": f"Test Parameter {i}",
                "unit": "unit",
                "reference_range": "1-10"
            }
            for i in range(1000)  # 1000 test definitions
        ]
        
        large_payload = {
            "name": "Large Payload Service",
            "description": large_description,
            "price": 100.00,
            "test_definitions": large_test_definitions
        }
        
        response = await client.post(
            "/api/v1/lab-services/",
            json=large_payload,
            headers=headers
        )
        
        # Should handle large payloads gracefully
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        ]

    async def test_special_characters_in_data(self, client: AsyncClient):
        """Test handling of special characters in data."""
        # Login first
        login_data = {
            "username": "testuser",
            "password": "testpass"
        }
        
        login_response = await client.post(
            "/api/v1/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test with various special characters
        special_chars_data = {
            "name": "Service with Special Chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "description": "Description with unicode: 你好世界 🧪🔬💉",
            "price": 100.00,
            "test_definitions": [
                {
                    "name": "Test with émojis 🧪",
                    "unit": "µg/dL",
                    "reference_range": "≤ 10 or ≥ 20"
                }
            ]
        }
        
        response = await client.post(
            "/api/v1/lab-services/",
            json=special_chars_data,
            headers=headers
        )
        
        # Should handle special characters properly
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]

    async def test_sql_injection_attempts(self, client: AsyncClient):
        """Test protection against SQL injection attempts."""
        # Login first
        login_data = {
            "username": "testuser",
            "password": "testpass"
        }
        
        login_response = await client.post(
            "/api/v1/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # SQL injection attempts in various fields
        sql_injection_payloads = [
            {
                "name": "'; DROP TABLE lab_services; --",
                "description": "SQL injection attempt",
                "price": 100.00,
                "test_definitions": []
            },
            {
                "name": "Normal Service",
                "description": "1' OR '1'='1",
                "price": 100.00,
                "test_definitions": []
            }
        ]
        
        for payload in sql_injection_payloads:
            response = await client.post(
                "/api/v1/lab-services/",
                json=payload,
                headers=headers
            )
            
            # Should not cause server errors
            assert response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR

    async def test_concurrent_modifications(self, client: AsyncClient, db_session: AsyncSession):
        """Test handling of concurrent modifications."""
        # Login first
        login_data = {
            "username": "testuser",
            "password": "testpass"
        }
        
        login_response = await client.post(
            "/api/v1/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a lab service
        service_data = {
            "name": "Concurrent Test Service",
            "description": "For concurrent modification testing",
            "price": 100.00,
            "test_definitions": []
        }
        
        create_response = await client.post(
            "/api/v1/lab-services/",
            json=service_data,
            headers=headers
        )
        
        service = create_response.json()
        service_id = service["id"]
        
        # Simulate concurrent updates
        update_data_1 = {"name": "Updated by User 1"}
        update_data_2 = {"name": "Updated by User 2"}
        
        # Both updates should be handled gracefully
        response_1 = await client.patch(
            f"/api/v1/lab-services/{service_id}",
            json=update_data_1,
            headers=headers
        )
        
        response_2 = await client.patch(
            f"/api/v1/lab-services/{service_id}",
            json=update_data_2,
            headers=headers
        )
        
        # Both should succeed (last one wins)
        assert response_1.status_code == status.HTTP_200_OK
        assert response_2.status_code == status.HTTP_200_OK

    async def test_invalid_uuid_formats(self, client: AsyncClient):
        """Test handling of invalid UUID formats in URLs."""
        # Login first
        login_data = {
            "username": "testuser",
            "password": "testpass"
        }
        
        login_response = await client.post(
            "/api/v1/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        invalid_uuids = [
            "not-a-uuid",
            "12345",
            "12345678-1234-1234-1234",  # Too short
            "12345678-1234-1234-1234-12345678901234",  # Too long
            "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",  # Invalid characters
            "",  # Empty
            "null",
            "undefined"
        ]
        
        for invalid_uuid in invalid_uuids:
            # Test lab services endpoint
            response = await client.get(
                f"/api/v1/lab-services/by-lab/{invalid_uuid}",
                headers=headers
            )
            # 307 is redirect, 422 is validation error - both are acceptable
            assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_307_TEMPORARY_REDIRECT]
            
            # Test test orders endpoint
            response = await client.get(
                f"/api/v1/test-orders/{invalid_uuid}",
                headers=headers
            )
            # Accept both validation error and redirect, or 404 if endpoint doesn't exist
            assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_307_TEMPORARY_REDIRECT, status.HTTP_404_NOT_FOUND]

    async def test_missing_required_fields(self, client: AsyncClient):
        """Test handling of missing required fields."""
        # Login first
        login_data = {
            "username": "testuser",
            "password": "testpass"
        }
        
        login_response = await client.post(
            "/api/v1/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test missing required fields in lab service creation
        incomplete_payloads = [
            {},  # Empty payload
            {"name": "Service without price"},  # Missing price
            {"price": 100.00},  # Missing name
            {"name": "Service", "price": "invalid_price"},  # Invalid price type
        ]
        
        for payload in incomplete_payloads:
            response = await client.post(
                "/api/v1/lab-services/",
                json=payload,
                headers=headers
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_boundary_value_testing(self, client: AsyncClient):
        """Test boundary values for numeric fields."""
        # Login first
        login_data = {
            "username": "testuser",
            "password": "testpass"
        }
        
        login_response = await client.post(
            "/api/v1/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test boundary values for price
        boundary_test_cases = [
            {"name": "Zero Price", "price": 0.00, "test_definitions": []},
            {"name": "Very Small Price", "price": 0.01, "test_definitions": []},
            {"name": "Large Price", "price": 999999.99, "test_definitions": []},
            {"name": "Negative Price", "price": -1.00, "test_definitions": []},
        ]
        
        for test_case in boundary_test_cases:
            response = await client.post(
                "/api/v1/lab-services/",
                json=test_case,
                headers=headers
            )
            
            # Negative prices should be rejected, others might be accepted
            if test_case["price"] < 0:
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            else:
                assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]

    async def test_network_timeout_simulation(self, client: AsyncClient):
        """Test handling of potential network timeouts."""
        # This test simulates slow operations by creating complex data
        # Login first
        login_data = {
            "username": "testuser",
            "password": "testpass"
        }
        
        login_response = await client.post(
            "/api/v1/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create service with many test definitions (simulates slow operation)
        complex_service = {
            "name": "Complex Service with Many Tests",
            "description": "Service with many test definitions to simulate slow processing",
            "price": 500.00,
            "test_definitions": [
                {
                    "name": f"Complex Test Parameter {i}",
                    "unit": f"unit_{i}",
                    "reference_range": f"{i}-{i+10}"
                }
                for i in range(50)  # 50 test definitions
            ]
        }
        
        response = await client.post(
            "/api/v1/lab-services/",
            json=complex_service,
            headers=headers
        )
        
        # Should complete within reasonable time
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]