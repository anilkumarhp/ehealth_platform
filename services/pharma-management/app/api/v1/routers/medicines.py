"""
Medicine management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from uuid import UUID
import logging

from app.db.session import get_async_session
from app.models.medicine import Medicine
from app.schemas.medicine import MedicineResponse, MedicineAlternatives
from app.services.medicine_service import MedicineService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/search", response_model=List[MedicineResponse])
async def search_medicines(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session)
):
    """Search medicines by name, generic name, or manufacturer."""
    try:
        medicine_service = MedicineService(db)
        medicines = await medicine_service.search_medicines(q.strip(), limit)
        
        if not medicines:
            logger.info(f"No medicines found for query: {q}")
            return []
        
        logger.info(f"Found {len(medicines)} medicines for query: {q}")
        return medicines
    except ValueError as e:
        logger.error(f"Validation error in medicine search: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error searching medicines: {e}")
        raise HTTPException(status_code=500, detail="Medicine search failed")


@router.get("/{medicine_id}", response_model=MedicineResponse)
async def get_medicine(
    medicine_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """Get medicine details by ID."""
    try:
        medicine_service = MedicineService(db)
        medicine = await medicine_service.get_medicine(medicine_id)
        return medicine
    except ValueError as e:
        logger.error(f"Medicine not found: {e}")
        raise HTTPException(status_code=404, detail="Medicine not found")
    except Exception as e:
        logger.error(f"Unexpected error getting medicine {medicine_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve medicine")


@router.post("/", response_model=MedicineResponse)
async def create_medicine(
    medicine_data: dict,
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new medicine."""
    try:
        medicine_service = MedicineService(db)
        medicine = await medicine_service.create_medicine(medicine_data)
        logger.info(f"Created medicine: {medicine.name}")
        return medicine
    except ValueError as e:
        logger.error(f"Validation error creating medicine: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating medicine: {e}")
        raise HTTPException(status_code=500, detail="Failed to create medicine")


@router.get("/{medicine_id}/alternatives", response_model=MedicineAlternatives)
async def get_medicine_alternatives(
    medicine_id: UUID,
    include_generic: bool = Query(True),
    include_brand: bool = Query(True),
    db: AsyncSession = Depends(get_async_session)
):
    """Get alternative medicines (generic/brand substitutes)."""
    try:
        medicine_service = MedicineService(db)
        alternatives = await medicine_service.get_alternatives(
            medicine_id, include_generic, include_brand
        )
        return alternatives
    except ValueError as e:
        logger.error(f"Medicine not found for alternatives: {e}")
        raise HTTPException(status_code=404, detail="Medicine not found")
    except Exception as e:
        logger.error(f"Unexpected error getting alternatives for medicine {medicine_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alternatives")