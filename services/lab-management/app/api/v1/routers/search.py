from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func, String as sa_String
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db_session
from app.api.deps import get_current_user
from app.core.security import TokenPayload
from app.models.lab_service import LabService
from app.models.test_order import TestOrder
from app.models.appointment import Appointment
from app.models.test_definition import TestDefinition

router = APIRouter()

@router.get("/lab-services")
async def search_lab_services(
    *,
    db: AsyncSession = Depends(get_db_session),
    q: str = Query(..., min_length=2, description="Search query"),
    lab_id: Optional[UUID] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    is_active: Optional[bool] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: TokenPayload = Depends(get_current_user)
):
    """Search lab services with full-text search capabilities."""
    
    # Base query with text search
    query = select(LabService).where(
        or_(
            LabService.name.ilike(f"%{q}%"),
            LabService.description.ilike(f"%{q}%")
        )
    )
    
    # Apply filters
    if lab_id:
        query = query.where(LabService.lab_id == lab_id)
    if min_price is not None:
        query = query.where(LabService.price >= min_price)
    if max_price is not None:
        query = query.where(LabService.price <= max_price)
    if is_active is not None:
        query = query.where(LabService.is_active == is_active)
    
    # Add pagination
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    services = result.scalars().all()
    
    return [
        {
            "id": str(service.id),
            "name": service.name,
            "description": service.description,
            "price": float(service.price),
            "is_active": service.is_active,
            "lab_id": str(service.lab_id)
        }
        for service in services
    ]

@router.get("/test-parameters")
async def search_test_parameters(
    *,
    db: AsyncSession = Depends(get_db_session),
    q: str = Query(..., min_length=2, description="Search query"),
    lab_id: Optional[UUID] = None,
    limit: int = Query(20, ge=1, le=100),
    current_user: TokenPayload = Depends(get_current_user)
):
    """Search test parameters/definitions."""
    
    query = select(TestDefinition).options(
        selectinload(TestDefinition.service)
    ).join(LabService).where(
        or_(
            TestDefinition.name.ilike(f"%{q}%"),
            TestDefinition.unit.ilike(f"%{q}%"),
            TestDefinition.reference_range.ilike(f"%{q}%")
        )
    )
    
    if lab_id:
        query = query.where(LabService.lab_id == lab_id)
    
    query = query.limit(limit)
    
    result = await db.execute(query)
    definitions = result.scalars().all()
    
    return [
        {
            "id": str(definition.id),
            "name": definition.name,
            "unit": definition.unit,
            "reference_range": definition.reference_range,
            "service_name": definition.service.name if definition.service else None
        }
        for definition in definitions
    ]

@router.get("/appointments")
async def search_appointments(
    *,
    db: AsyncSession = Depends(get_db_session),
    q: Optional[str] = Query(None, min_length=2),
    lab_id: Optional[UUID] = None,
    status: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: TokenPayload = Depends(get_current_user)
):
    """Search appointments with various filters."""
    
    query = select(Appointment)
    
    # Text search (if provided)
    if q:
        query = query.join(LabService).where(
            or_(
                LabService.name.ilike(f"%{q}%"),
                func.cast(Appointment.patient_user_id, sa_String).ilike(f"%{q}%")
            )
        )
    
    # Apply filters
    if lab_id:
        query = query.where(Appointment.lab_id == lab_id)
    elif current_user.org_id:
        query = query.where(Appointment.lab_id == current_user.org_id)
    
    if status:
        query = query.where(Appointment.status == status)
    
    # Add pagination
    query = query.offset(offset).limit(limit).order_by(Appointment.appointment_time.desc())
    
    result = await db.execute(query)
    appointments = result.scalars().all()
    
    return [
        {
            "id": str(appointment.id),
            "appointment_time": appointment.appointment_time.isoformat(),
            "status": appointment.status.value,
            "patient_user_id": str(appointment.patient_user_id),
            "lab_service_id": str(appointment.lab_service_id),
            "lab_id": str(appointment.lab_id)
        }
        for appointment in appointments
    ]

@router.get("/global")
async def global_search(
    *,
    db: AsyncSession = Depends(get_db_session),
    q: str = Query(..., min_length=2, description="Global search query"),
    limit: int = Query(10, ge=1, le=50),
    current_user: TokenPayload = Depends(get_current_user)
):
    """Global search across multiple entities."""
    
    results = {
        "lab_services": [],
        "test_parameters": [],
        "appointments": []
    }
    
    # Search lab services
    services_query = select(LabService).where(
        or_(
            LabService.name.ilike(f"%{q}%"),
            LabService.description.ilike(f"%{q}%")
        )
    ).limit(limit // 3)
    
    services_result = await db.execute(services_query)
    services = services_result.scalars().all()
    
    results["lab_services"] = [
        {
            "id": str(s.id),
            "name": s.name,
            "type": "lab_service"
        }
        for s in services
    ]
    
    # Search test parameters
    params_query = select(TestDefinition).where(
        TestDefinition.name.ilike(f"%{q}%")
    ).limit(limit // 3)
    
    params_result = await db.execute(params_query)
    params = params_result.scalars().all()
    
    results["test_parameters"] = [
        {
            "id": str(p.id),
            "name": p.name,
            "type": "test_parameter"
        }
        for p in params
    ]
    
    return results