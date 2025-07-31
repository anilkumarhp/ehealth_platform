import pytest
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.repositories.lab_service_repo import lab_service_repo
from app.repositories.test_order_repo import test_order_repo
from app.models.lab_service import LabService
from app.models.test_order import TestOrder, TestOrderStatusEnum
from app.schemas.lab_service import LabServiceCreate, TestDefinitionCreate
from app.schemas.test_order import TestOrderCreate


@pytest.mark.asyncio
async def test_lab_service_repository_create(db_session: AsyncSession):
    """Test creating a lab service using the async repository."""
    test_definitions = [
        TestDefinitionCreate(
            name="Hemoglobin",
            unit="g/dL",
            reference_range="12.0-15.5"
        ),
        TestDefinitionCreate(
            name="Hematocrit",
            unit="%",
            reference_range="36-46"
        )
    ]
    
    service_create = LabServiceCreate(
        name="Complete Blood Count",
        description="Comprehensive blood analysis",
        price=85.00,
        is_active=True,
        test_definitions=test_definitions
    )
    
    lab_id = uuid.UUID("00000000-0000-0000-0000-000000000123")
    
    # Create the service
    created_service = await lab_service_repo.create_with_lab_id(
        db=db_session,
        obj_in=service_create,
        lab_id=lab_id
    )
    
    assert created_service.id is not None
    assert created_service.name == "Complete Blood Count"
    assert float(created_service.price) == 85.00
    assert created_service.lab_id == lab_id
    assert len(created_service.test_definitions) == 2


@pytest.mark.asyncio
async def test_lab_service_repository_get(db_session: AsyncSession):
    """Test retrieving a lab service using the async repository."""
    # First create a service
    lab_service = LabService(
        name="Lipid Panel",
        description="Cholesterol and triglycerides",
        price=65.00,
        lab_id=uuid.UUID("00000000-0000-0000-0000-000000000123"),
        is_active=True
    )
    
    db_session.add(lab_service)
    await db_session.flush()
    await db_session.refresh(lab_service)
    
    # Retrieve it using the repository
    retrieved_service = await lab_service_repo.get(db=db_session, id=lab_service.id)
    
    assert retrieved_service is not None
    assert retrieved_service.id == lab_service.id
    assert retrieved_service.name == "Lipid Panel"


@pytest.mark.asyncio
async def test_test_order_repository_create(db_session: AsyncSession):
    """Test creating a test order using the async repository."""
    # First create a lab service
    lab_service = LabService(
        name="Basic Metabolic Panel",
        description="Basic metabolic tests",
        price=45.00,
        lab_id=uuid.UUID("00000000-0000-0000-0000-000000000123"),
        is_active=True
    )
    
    db_session.add(lab_service)
    await db_session.flush()
    await db_session.refresh(lab_service)
    
    # Create test order
    order_create = TestOrderCreate(
        lab_service_id=lab_service.id,
        clinical_notes="Routine metabolic screening"
    )
    
    patient_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    requesting_entity_id = uuid.UUID("00000000-0000-0000-0000-000000000002")
    organization_id = uuid.UUID("00000000-0000-0000-0000-000000000123")
    
    created_order = await test_order_repo.create_with_owner(
        db=db_session,
        obj_in=order_create,
        patient_user_id=patient_id,
        requesting_entity_id=requesting_entity_id,
        organization_id=organization_id
    )
    
    assert created_order.id is not None
    assert created_order.patient_user_id == patient_id
    assert created_order.requesting_entity_id == requesting_entity_id
    assert created_order.organization_id == organization_id
    assert created_order.lab_service_id == lab_service.id
    assert created_order.status == TestOrderStatusEnum.PENDING_CONSENT


@pytest.mark.asyncio
async def test_test_order_repository_get_by_patient(db_session: AsyncSession):
    """Test retrieving test orders by patient ID."""
    patient_id = uuid.uuid4()  # Use unique patient ID to avoid test pollution
    
    # Create a lab service first
    lab_service = LabService(
        name="Thyroid Panel",
        description="Thyroid function tests",
        price=95.00,
        lab_id=uuid.UUID("00000000-0000-0000-0000-000000000123"),
        is_active=True
    )
    
    db_session.add(lab_service)
    await db_session.flush()
    await db_session.refresh(lab_service)
    
    # Create multiple test orders for the same patient
    for i in range(3):
        test_order = TestOrder(
            patient_user_id=patient_id,
            requesting_entity_id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
            organization_id=uuid.UUID("00000000-0000-0000-0000-000000000123"),
            lab_service_id=lab_service.id,
            status=TestOrderStatusEnum.PENDING_CONSENT,
            clinical_notes=f"Test order {i+1}"
        )
        db_session.add(test_order)
    
    await db_session.flush()
    
    # Retrieve orders by patient ID
    orders = await test_order_repo.get_by_patient_id(
        db=db_session,
        patient_user_id=patient_id
    )
    
    assert len(orders) == 3
    assert all(order.patient_user_id == patient_id for order in orders)


@pytest.mark.asyncio
async def test_repository_update_operations(db_session: AsyncSession):
    """Test update operations in repositories."""
    # Create a lab service
    lab_service = LabService(
        name="Original Name",
        description="Original description",
        price=50.00,
        lab_id=uuid.UUID("00000000-0000-0000-0000-000000000123"),
        is_active=True
    )
    
    db_session.add(lab_service)
    await db_session.flush()
    await db_session.refresh(lab_service)
    
    # Update the service
    update_data = {
        "name": "Updated Name",
        "price": 75.00,
        "is_active": False
    }
    
    updated_service = await lab_service_repo.update(
        db=db_session,
        db_obj=lab_service,
        obj_in=update_data
    )
    
    assert updated_service.name == "Updated Name"
    assert float(updated_service.price) == 75.00
    assert updated_service.is_active is False
    assert updated_service.description == "Original description"  # Unchanged