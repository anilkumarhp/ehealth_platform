"""
Staff management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import logging

from app.db.session import get_async_session
from app.schemas.staff import StaffCreate, StaffResponse, StaffList
from app.services.staff_service import StaffService
from app.core.exceptions import PharmacyNotFoundException

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{pharmacy_id}/staff", response_model=StaffResponse)
async def add_staff_member(
    pharmacy_id: UUID,
    staff_data: StaffCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """Add new staff member to pharmacy."""
    try:
        staff_service = StaffService(db)
        staff_member = await staff_service.add_staff_member(pharmacy_id, staff_data)
        logger.info(f"Successfully added staff member to pharmacy {pharmacy_id}")
        return staff_member
    except PharmacyNotFoundException as e:
        logger.error(f"Pharmacy not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Validation error adding staff member: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error adding staff member: {e}")
        raise HTTPException(status_code=500, detail="Failed to add staff member")


@router.get("/{pharmacy_id}/staff", response_model=List[StaffList])
async def get_pharmacy_staff(
    pharmacy_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """Get all staff members for a pharmacy."""
    try:
        staff_service = StaffService(db)
        staff_members = await staff_service.get_pharmacy_staff(pharmacy_id)
        logger.info(f"Retrieved {len(staff_members)} staff members for pharmacy {pharmacy_id}")
        return staff_members
    except Exception as e:
        logger.error(f"Unexpected error getting pharmacy staff: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")