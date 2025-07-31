# import pytest
# from httpx import AsyncClient
# from sqlalchemy.ext.asyncio import AsyncSession
# import uuid

# from app.models.lab_service import LabService
# from app.models.test_definition import TestDefinition
# from app.models.test_order import TestOrder, TestOrderStatusEnum


# @pytest.mark.asyncio
# async def test_health_check(client: AsyncClient):
#     """Test the health check endpoint."""
#     response = await client.get("/")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == "ok"


# @pytest.mark.asyncio
# async def test_create_lab_service_endpoint(client: AsyncClient, db_session: AsyncSession):
#     """Test creating a lab service via API."""
#     service_data = {
#         "name": "Complete Blood Count",
#         "description": "A comprehensive blood test",
#         "price": 75.50,
#         "is_active": True,
#         "test_definitions": [
#             {
#                 "name": "White Blood Cell Count",
#                 "description": "Count of white blood cells",
#                 "normal_range": "4,000-11,000 cells/mcL",
#                 "unit": "cells/mcL"
#             },
#             {
#                 "name": "Red Blood Cell Count",
#                 "description": "Count of red blood cells",
#                 "normal_range": "4.5-5.5 million cells/mcL",
#                 "unit": "million cells/mcL"
#             }
#         ]
#     }
    
#     response = await client.post("/api/v1/lab-services/", json=service_data)
#     assert response.status_code == 201
    
#     data = response.json()
#     assert data["name"] == "Complete Blood Count"
#     assert float(data["price"]) == 75.50
#     assert len(data["test_definitions"]) == 2


# @pytest.mark.asyncio
# async def test_get_lab_services_endpoint(client: AsyncClient, db_session: AsyncSession):
#     """Test retrieving lab services via API."""
#     # First create a lab service directly in the database
#     lab_id = uuid.UUID("87654321-4321-4321-8321-210987654321")
    
#     lab_service = LabService(
#         name="Basic Metabolic Panel",
#         description="Basic metabolic tests",
#         price=45.00,
#         lab_id=lab_id,
#         is_active=True
#     )
    
#     db_session.add(lab_service)
#     await db_session.flush()
#     await db_session.refresh(lab_service)
    
#     # Now test the API endpoint
#     response = await client.get(f"/api/v1/lab-services/by-lab/{lab_id}")
#     assert response.status_code == 200
    
#     data = response.json()
#     assert len(data) >= 1
#     assert any(service["name"] == "Basic Metabolic Panel" for service in data)


# @pytest.mark.asyncio
# async def test_create_test_order_endpoint(client: AsyncClient, db_session: AsyncSession):
#     """Test creating a test order via API."""
#     # First create a lab service
#     lab_id = uuid.UUID("87654321-4321-4321-8321-210987654321")
    
#     lab_service = LabService(
#         name="Lipid Panel",
#         description="Cholesterol and lipid tests",
#         price=65.00,
#         lab_id=lab_id,
#         is_active=True
#     )
    
#     db_session.add(lab_service)
#     await db_session.flush()
#     await db_session.refresh(lab_service)
    
#     # Create test order
#     patient_id = uuid.UUID("22345678-1234-4234-8234-123456789012")
#     order_data = {
#         "lab_service_id": str(lab_service.id),
#         "clinical_notes": "Patient has family history of heart disease"
#     }
    
#     response = await client.post(
#         f"/api/v1/test-orders/for-patient/{patient_id}",
#         json=order_data
#     )
#     assert response.status_code == 201
    
#     data = response.json()
#     assert data["lab_service_id"] == str(lab_service.id)
#     assert data["patient_user_id"] == str(patient_id)
#     assert data["status"] == TestOrderStatusEnum.PENDING_CONSENT.value


# @pytest.mark.asyncio
# async def test_get_my_test_orders_endpoint(client: AsyncClient, db_session: AsyncSession):
#     """Test retrieving user's test orders via API."""
#     # Create a test order directly in the database
#     user_id = uuid.UUID("12345678-1234-4234-8234-123456789012")
#     lab_id = uuid.UUID("87654321-4321-4321-8321-210987654321")
    
#     # First create a lab service
#     lab_service = LabService(
#         name="Thyroid Panel",
#         description="Thyroid function tests",
#         price=85.00,
#         lab_id=lab_id,
#         is_active=True
#     )
    
#     db_session.add(lab_service)
#     await db_session.flush()
#     await db_session.refresh(lab_service)
    
#     # Create test order
#     test_order = TestOrder(
#         patient_user_id=user_id,
#         requesting_entity_id=uuid.UUID("32345678-1234-4234-8234-123456789012"),
#         organization_id=lab_id,
#         lab_service_id=lab_service.id,
#         status=TestOrderStatusEnum.PENDING_CONSENT,
#         clinical_notes="Routine thyroid check"
#     )
    
#     db_session.add(test_order)
#     await db_session.flush()
#     await db_session.refresh(test_order)
    
#     # Test the API endpoint
#     response = await client.get("/api/v1/test-orders/for-patient/my-orders")
#     assert response.status_code == 200
    
#     data = response.json()
#     assert len(data) >= 1
#     assert any(order["clinical_notes"] == "Routine thyroid check" for order in data)


# @pytest.mark.asyncio
# async def test_database_transaction_rollback(db_session: AsyncSession):
#     """Test that database transactions properly rollback on error."""
#     lab_service = LabService(
#         name="Test Service",
#         description="Test description",
#         price=50.00,
#         lab_id=uuid.UUID("00000000-0000-0000-0000-000000000123"),
#         is_active=True
#     )
    
#     db_session.add(lab_service)
#     await db_session.flush()
    
#     # Simulate an error and rollback
#     await db_session.rollback()
    
#     # Verify the service was not committed
#     result = await db_session.get(LabService, lab_service.id)
#     assert result is None