from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel

from app.db.session import get_db_session
from app.api.deps import get_current_user
from app.core.security import TokenPayload
from app.services.appointment_service import appointment_service
from app.services.advanced_slot_service import advanced_slot_service
from app.schemas.appointment import Appointment, AppointmentCreate


router = APIRouter()


class SlotReservationRequest(BaseModel):
    """Request to reserve an appointment slot."""
    test_order_id: UUID
    lab_service_id: UUID
    appointment_time: str  # ISO format


class SlotAvailabilityResponse(BaseModel):
    """Response for slot availability."""
    datetime: str
    available: bool
    capacity_used: int
    capacity_total: int
    duration_minutes: int
    recommended_for_test: Optional[bool] = None


@router.get("/available-slots/{lab_id}/{lab_service_id}")
async def get_available_slots_for_test(
    *,
    db: AsyncSession = Depends(get_db_session),
    lab_id: UUID,
    lab_service_id: UUID,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    current_user: TokenPayload = Depends(get_current_user)
):
    """Get available appointment slots for a specific test."""
    
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    if target_date < datetime.now().date():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot schedule appointments in the past"
        )
    
    slots = await advanced_slot_service.get_available_slots_for_test(
        db=db,
        lab_id=lab_id,
        lab_service_id=lab_service_id,
        target_date=target_date
    )
    
    return {"available_slots": slots}


@router.get("/optimal-slots/{lab_id}/{lab_service_id}")
async def get_optimal_slots_for_test(
    *,
    db: AsyncSession = Depends(get_db_session),
    lab_id: UUID,
    lab_service_id: UUID,
    preferred_date: Optional[str] = Query(None, description="Preferred date in YYYY-MM-DD format"),
    current_user: TokenPayload = Depends(get_current_user)
) -> List[SlotAvailabilityResponse]:
    """Get optimal appointment slots for a specific test."""
    
    target_date = None
    if preferred_date:
        try:
            target_date = datetime.strptime(preferred_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    
    slots = await slot_management_service.get_optimal_slots_for_test(
        db=db,
        lab_id=lab_id,
        lab_service_id=lab_service_id,
        preferred_date=target_date
    )
    
    return [SlotAvailabilityResponse(**slot) for slot in slots]


@router.get("/next-available/{lab_id}")
async def get_next_available_slot(
    *,
    db: AsyncSession = Depends(get_db_session),
    lab_id: UUID,
    preferred_date: Optional[str] = Query(None, description="Preferred date in YYYY-MM-DD format"),
    test_duration: Optional[int] = Query(None, description="Test duration in minutes"),
    current_user: TokenPayload = Depends(get_current_user)
) -> Optional[SlotAvailabilityResponse]:
    """Find the next available appointment slot."""
    
    target_date = None
    if preferred_date:
        try:
            target_date = datetime.strptime(preferred_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    
    slot = await slot_management_service.get_next_available_slot(
        db=db,
        lab_id=lab_id,
        preferred_date=target_date,
        test_duration_minutes=test_duration
    )
    
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No available slots found in the next 14 days"
        )
    
    return SlotAvailabilityResponse(**slot)


@router.post("/reserve-exact-slot/{lab_id}")
async def reserve_exact_appointment_slot(
    *,
    db: AsyncSession = Depends(get_db_session),
    lab_id: UUID,
    reservation: SlotReservationRequest,
    current_user: TokenPayload = Depends(get_current_user)
):
    """Reserve an exact appointment slot with conflict checking."""
    
    try:
        start_time = datetime.fromisoformat(reservation.appointment_time.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format. Use ISO format"
        )
    
    # Reserve the exact slot
    success, message = await advanced_slot_service.reserve_exact_slot(
        db=db,
        lab_id=lab_id,
        lab_service_id=reservation.lab_service_id,
        start_time=start_time,
        patient_id=current_user.sub,
        test_order_id=reservation.test_order_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message
        )
    
    return {"success": True, "message": message, "appointment_time": start_time.isoformat()}


@router.get("/my-appointments")
async def get_my_appointments(
    *,
    db: AsyncSession = Depends(get_db_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: TokenPayload = Depends(get_current_user)
) -> List[Appointment]:
    """Get current user's appointments."""
    
    appointments = await appointment_service.get_appointments_by_patient(
        db=db,
        patient_id=current_user.sub,
        skip=skip,
        limit=limit
    )
    
    return appointments


@router.get("/lab-appointments/{lab_id}")
async def get_lab_appointments(
    *,
    db: AsyncSession = Depends(get_db_session),
    lab_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: TokenPayload = Depends(get_current_user)
) -> List[Appointment]:
    """Get appointments for a specific lab (lab staff only)."""
    
    # Check if user belongs to the lab
    if current_user.org_id != lab_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to lab appointments"
        )
    
    appointments = await appointment_service.get_appointments_by_lab(
        db=db,
        lab_id=lab_id,
        skip=skip,
        limit=limit
    )
    
    return appointments


@router.patch("/{appointment_id}/cancel")
async def cancel_appointment(
    *,
    db: AsyncSession = Depends(get_db_session),
    appointment_id: UUID,
    current_user: TokenPayload = Depends(get_current_user)
) -> Appointment:
    """Cancel an appointment."""
    
    appointment = await appointment_service.cancel_appointment(
        db=db,
        appointment_id=appointment_id,
        current_user=current_user
    )
    
    return appointment


@router.patch("/{appointment_id}/complete")
async def complete_appointment(
    *,
    db: AsyncSession = Depends(get_db_session),
    appointment_id: UUID,
    completion_notes: Optional[str] = None,
    current_user: TokenPayload = Depends(get_current_user)
) -> Appointment:
    """Mark appointment as completed (lab staff only)."""
    
    from app.models.appointment import AppointmentStatusEnum
    
    appointment = await appointment_service.update_appointment_status(
        db=db,
        appointment_id=appointment_id,
        new_status=AppointmentStatusEnum.COMPLETED,
        completion_notes=completion_notes
    )
    
    return appointment