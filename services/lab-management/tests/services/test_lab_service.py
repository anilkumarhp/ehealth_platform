import pytest
from uuid import UUID
from app.services.lab_service_service import lab_service_service
from app.schemas.lab_service import LabServiceCreate, TestDefinitionCreate
from app.core.security import TokenPayload

@pytest.mark.asyncio
async def test_create_service_logic(db_session):
    obj = LabServiceCreate(
        name="Urine Test",
        description="Detects abnormalities",
        price=100.0,
        test_definitions=[
            TestDefinitionCreate(name="Protein", unit="mg/dL", reference_range="0-8")
        ]
    )
    service = await lab_service_service.create_service(db=db_session, obj_in=obj, lab_id=UUID("00000000-0000-0000-0000-000000000123"))
    assert service.name == "Urine Test"
    assert service.test_definitions[0].name == "Protein"
