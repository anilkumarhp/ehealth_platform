import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4, UUID

from app.repositories.lab_service_repo import lab_service_repo
from app.repositories.test_order_repo import test_order_repo
from app.schemas.lab_service import LabServiceCreate, TestDefinitionCreate
from app.schemas.test_order import TestOrderCreate
from app.models.lab_service import LabService
from app.models.test_order import TestOrder, TestOrderStatusEnum


@pytest.mark.asyncio
class TestRepositoriesSimple:
    """Simple unit tests for repositories using mocks."""

    async def test_lab_service_repo_create_with_lab_id(self):
        """Test lab service creation with mocked repository."""
        
        # Create test data
        test_definitions = [
            TestDefinitionCreate(
                name="Hemoglobin",
                unit="g/dL", 
                reference_range="12.0-15.5"
            )
        ]
        
        service_create = LabServiceCreate(
            name="Complete Blood Count",
            description="Comprehensive blood analysis",
            price=85.00,
            test_definitions=test_definitions
        )
        
        lab_id = UUID("00000000-0000-0000-0000-000000000123")
        
        # Mock the repository method
        expected_service = LabService(
            id=uuid4(),
            name="Complete Blood Count",
            description="Comprehensive blood analysis", 
            price=85.00,
            lab_id=lab_id,
            is_active=True
        )
        
        with patch.object(lab_service_repo, 'create_with_lab_id', return_value=expected_service) as mock_create:
            result = await lab_service_repo.create_with_lab_id(
                db=AsyncMock(),
                obj_in=service_create,
                lab_id=lab_id
            )
            
            assert result.name == "Complete Blood Count"
            assert result.lab_id == lab_id
            mock_create.assert_called_once()

    async def test_test_order_repo_create_with_owner(self):
        """Test test order creation with mocked repository."""
        
        order_create = TestOrderCreate(
            lab_service_id=uuid4(),
            clinical_notes="Test order"
        )
        
        patient_id = uuid4()
        requesting_entity_id = uuid4()
        organization_id = uuid4()
        
        # Mock the repository method
        expected_order = TestOrder(
            id=uuid4(),
            patient_user_id=patient_id,
            requesting_entity_id=requesting_entity_id,
            organization_id=organization_id,
            lab_service_id=order_create.lab_service_id,
            status=TestOrderStatusEnum.PENDING_CONSENT,
            clinical_notes="Test order"
        )
        
        with patch.object(test_order_repo, 'create_with_owner', return_value=expected_order) as mock_create:
            result = await test_order_repo.create_with_owner(
                db=AsyncMock(),
                obj_in=order_create,
                patient_user_id=patient_id,
                requesting_entity_id=requesting_entity_id,
                organization_id=organization_id
            )
            
            assert result.patient_user_id == patient_id
            assert result.status == TestOrderStatusEnum.PENDING_CONSENT
            assert result.clinical_notes == "Test order"
            mock_create.assert_called_once()

    async def test_test_order_repo_get_by_patient_id(self):
        """Test getting test orders by patient ID with mocked repository."""
        
        patient_id = uuid4()
        
        # Mock test orders
        expected_orders = [
            TestOrder(
                id=uuid4(),
                patient_user_id=patient_id,
                requesting_entity_id=uuid4(),
                organization_id=uuid4(),
                lab_service_id=uuid4(),
                status=TestOrderStatusEnum.PENDING_CONSENT,
                clinical_notes=f"Test order {i+1}"
            )
            for i in range(3)
        ]
        
        with patch.object(test_order_repo, 'get_by_patient_id', return_value=expected_orders) as mock_get:
            result = await test_order_repo.get_by_patient_id(
                db=AsyncMock(),
                patient_user_id=patient_id
            )
            
            assert len(result) == 3
            assert all(order.patient_user_id == patient_id for order in result)
            mock_get.assert_called_once()

    async def test_lab_service_repo_get(self):
        """Test getting lab service by ID with mocked repository."""
        
        service_id = uuid4()
        
        # Mock lab service
        expected_service = LabService(
            id=service_id,
            name="Blood Panel",
            description="Comprehensive blood test",
            price=99.99,
            lab_id=uuid4(),
            is_active=True
        )
        
        with patch.object(lab_service_repo, 'get', return_value=expected_service) as mock_get:
            result = await lab_service_repo.get(
                db=AsyncMock(),
                id=service_id
            )
            
            assert result.id == service_id
            assert result.name == "Blood Panel"
            mock_get.assert_called_once()

    async def test_lab_service_repo_get_by_lab_id(self):
        """Test getting lab services by lab ID with mocked repository."""
        
        lab_id = uuid4()
        
        # Mock lab services
        expected_services = [
            LabService(
                id=uuid4(),
                name=f"Service {i+1}",
                description=f"Description {i+1}",
                price=100.0 + i,
                lab_id=lab_id,
                is_active=True
            )
            for i in range(2)
        ]
        
        with patch.object(lab_service_repo, 'get_by_lab_id', return_value=expected_services) as mock_get:
            result = await lab_service_repo.get_by_lab_id(
                db=AsyncMock(),
                lab_id=lab_id
            )
            
            assert len(result) == 2
            assert all(service.lab_id == lab_id for service in result)
            mock_get.assert_called_once()