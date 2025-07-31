from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from datetime import time
from pydantic import BaseModel

from app.db.session import get_db_session
from app.api.deps import get_current_user
from app.core.security import TokenPayload, RoleBasedAuth
from app.models.lab_configuration import LabConfiguration
from app.models.test_duration import TestDuration


router = APIRouter()


class LabConfigurationCreate(BaseModel):
    """Schema for creating lab configuration."""
    lab_name: str
    opening_time: str = "08:00:00"
    closing_time: str = "18:00:00"
    lunch_start: Optional[str] = "12:00:00"
    lunch_end: Optional[str] = "13:00:00"
    max_concurrent_appointments: int = 5
    slot_interval_minutes: int = 15
    operating_days: List[int] = [0, 1, 2, 3, 4]  # Mon-Fri
    allow_same_day_booking: bool = True
    advance_booking_days: int = 30


class TestDurationCreate(BaseModel):
    """Schema for creating test duration configuration."""
    duration_minutes: int
    setup_time_minutes: int = 5
    cleanup_time_minutes: int = 5
    requires_fasting: bool = False
    equipment_required: Optional[str] = None
    room_type_required: Optional[str] = None
    scheduling_notes: Optional[str] = None


@router.post("/lab-configuration/{lab_id}")
async def create_lab_configuration(
    *,
    db: AsyncSession = Depends(get_db_session),
    lab_id: UUID,
    config: LabConfigurationCreate,
    current_user: TokenPayload = Depends(get_current_user)
):
    """Create or update lab configuration (lab admin only)."""
    
    # Check if user is lab admin for this lab
    if current_user.org_id != lab_id or "lab-admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lab administrators can configure lab settings"
        )
    
    # Check if configuration already exists
    existing = await db.execute(
        select(LabConfiguration).where(LabConfiguration.lab_id == lab_id)
    )
    existing_config = existing.scalar_one_or_none()
    
    if existing_config:
        # Update existing configuration
        for field, value in config.model_dump().items():
            if field == "opening_time" or field == "closing_time" or field.endswith("_start") or field.endswith("_end"):
                if isinstance(value, str):
                    value = time.fromisoformat(value)
            setattr(existing_config, field, value)
        
        await db.flush()
        await db.commit()
        return {"message": "Lab configuration updated successfully"}
    else:
        # Create new configuration
        config_dict = config.model_dump()
        
        # Convert time strings to time objects
        time_fields = ['opening_time', 'closing_time', 'lunch_start', 'lunch_end']
        for field in time_fields:
            if field in config_dict and isinstance(config_dict[field], str):
                config_dict[field] = time.fromisoformat(config_dict[field])
        
        lab_config = LabConfiguration(
            lab_id=lab_id,
            **config_dict
        )
        db.add(lab_config)
        await db.flush()
        await db.commit()
        return {"message": "Lab configuration created successfully"}


@router.post("/test-duration/{lab_service_id}")
async def create_test_duration(
    *,
    db: AsyncSession = Depends(get_db_session),
    lab_service_id: UUID,
    duration_config: TestDurationCreate,
    current_user: TokenPayload = Depends(get_current_user)
):
    """Configure test duration for a lab service (lab admin only)."""
    
    # Verify lab service belongs to user's lab
    from sqlalchemy import select
    from app.models.lab_service import LabService
    result = await db.execute(
        select(LabService).where(LabService.id == lab_service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service or service.lab_id != current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lab service not found or access denied"
        )
    
    if "lab-admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lab administrators can configure test durations"
        )
    
    # Calculate total time
    total_time = duration_config.duration_minutes + duration_config.setup_time_minutes + duration_config.cleanup_time_minutes
    
    # Check if duration config already exists
    from sqlalchemy import select
    existing = await db.execute(
        select(TestDuration).where(TestDuration.lab_service_id == lab_service_id)
    )
    existing_duration = existing.scalar_one_or_none()
    
    if existing_duration:
        # Update existing
        for field, value in duration_config.dict().items():
            setattr(existing_duration, field, value)
        existing_duration.total_time_minutes = total_time
        await db.flush()
        await db.commit()
        return {"message": "Test duration updated successfully"}
    else:
        # Create new
        test_duration = TestDuration(
            lab_service_id=lab_service_id,
            total_time_minutes=total_time,
            **duration_config.dict()
        )
        db.add(test_duration)
        await db.flush()
        await db.commit()
        return {"message": "Test duration configured successfully"}


@router.get("/lab-configuration/{lab_id}")
async def get_lab_configuration(
    *,
    db: AsyncSession = Depends(get_db_session),
    lab_id: UUID,
    current_user: TokenPayload = Depends(get_current_user)
):
    """Get lab configuration."""
    
    from sqlalchemy import select
    result = await db.execute(
        select(LabConfiguration).where(LabConfiguration.lab_id == lab_id)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lab configuration not found"
        )
    
    return {
        "lab_id": str(config.lab_id),
        "lab_name": config.lab_name,
        "opening_time": config.opening_time.strftime("%H:%M:%S"),
        "closing_time": config.closing_time.strftime("%H:%M:%S"),
        "lunch_start": config.lunch_start.strftime("%H:%M:%S") if config.lunch_start else None,
        "lunch_end": config.lunch_end.strftime("%H:%M:%S") if config.lunch_end else None,
        "max_concurrent_appointments": config.max_concurrent_appointments,
        "slot_interval_minutes": config.slot_interval_minutes,
        "operating_days": config.operating_days,
        "allow_same_day_booking": config.allow_same_day_booking,
        "advance_booking_days": config.advance_booking_days
    }


@router.get("/test-duration/{lab_service_id}")
async def get_test_duration(
    *,
    db: AsyncSession = Depends(get_db_session),
    lab_service_id: UUID,
    current_user: TokenPayload = Depends(get_current_user)
):
    """Get test duration configuration."""
    
    from sqlalchemy import select
    result = await db.execute(
        select(TestDuration).where(TestDuration.lab_service_id == lab_service_id)
    )
    duration = result.scalar_one_or_none()
    
    if not duration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test duration configuration not found"
        )
    
    return {
        "lab_service_id": str(duration.lab_service_id),
        "duration_minutes": duration.duration_minutes,
        "setup_time_minutes": duration.setup_time_minutes,
        "cleanup_time_minutes": duration.cleanup_time_minutes,
        "total_time_minutes": duration.total_time_minutes,
        "requires_fasting": duration.requires_fasting,
        "equipment_required": duration.equipment_required,
        "room_type_required": duration.room_type_required,
        "scheduling_notes": duration.scheduling_notes
    }