"""
Pharmacy management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from uuid import UUID
import logging

from app.db.session import get_async_session
from app.models.pharmacy import Pharmacy
from app.schemas.pharmacy import PharmacyCreate, PharmacyUpdate, PharmacyResponse, PharmacyList
from app.schemas.prescription import PrescriptionCreate, PrescriptionResponse
from app.schemas.inventory import InventoryItemResponse
from app.services.pharmacy_service import PharmacyService
from app.services.prescription_service import PrescriptionService
from app.core.exceptions import PharmacyNotFoundException

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=PharmacyResponse)
async def create_pharmacy(
    pharmacy_data: PharmacyCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new pharmacy."""
    try:
        pharmacy_service = PharmacyService(db)
        pharmacy = await pharmacy_service.create_pharmacy(pharmacy_data)
        logger.info(f"Created pharmacy: {pharmacy.id}")
        return pharmacy
    except ValueError as e:
        logger.error(f"Validation error creating pharmacy: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating pharmacy: {e}")
        raise HTTPException(status_code=500, detail="Failed to create pharmacy")


@router.get("/search", response_model=List[PharmacyList])
async def search_pharmacies(
    name: str = Query(..., min_length=1, description="Pharmacy name to search"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    radius_km: Optional[float] = Query(10, ge=1, le=100, description="Search radius in km"),
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_async_session)
):
    """Search pharmacies by name with dynamic suggestions."""
    try:
        query = select(Pharmacy).where(
            and_(
                Pharmacy.is_active == True,
                Pharmacy.operational_status == "active",
                Pharmacy.name.ilike(f"%{name.strip()}%")
            )
        )
        
        # Apply additional filters
        if city:
            query = query.where(Pharmacy.city.ilike(f"%{city.strip()}%"))
        if state:
            query = query.where(Pharmacy.state.ilike(f"%{state.strip()}%"))
        
        query = query.limit(limit)
        result = await db.execute(query)
        pharmacies = result.scalars().all()
        
        if not pharmacies:
            logger.info(f"No pharmacies found for '{name}' - suggest widening search area")
            return []
        
        logger.info(f"Found {len(pharmacies)} pharmacies matching '{name}'")
        return pharmacies
    except ValueError as e:
        logger.error(f"Validation error searching pharmacies: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error searching pharmacies: {e}")
        raise HTTPException(status_code=500, detail="Pharmacy search failed")


@router.get("/suggestions")
async def get_pharmacy_suggestions(
    name: str = Query(..., min_length=1, description="Partial pharmacy name"),
    city: Optional[str] = Query(None, description="Filter by city"),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_async_session)
):
    """Get dynamic pharmacy name suggestions as user types."""
    try:
        query = select(Pharmacy.name, Pharmacy.city, Pharmacy.state).where(
            and_(
                Pharmacy.is_active == True,
                Pharmacy.operational_status == "active",
                Pharmacy.name.ilike(f"%{name.strip()}%")
            )
        )
        
        if city:
            query = query.where(Pharmacy.city.ilike(f"%{city.strip()}%"))
        
        query = query.limit(limit)
        result = await db.execute(query)
        suggestions = result.all()
        
        suggestion_list = [
            {
                "name": row.name,
                "location": f"{row.city}, {row.state}"
            }
            for row in suggestions
        ]
        
        return {
            "suggestions": suggestion_list,
            "count": len(suggestion_list),
            "message": "No pharmacies found. Try widening the search area or check spelling." if not suggestion_list else None
        }
    except ValueError as e:
        logger.error(f"Validation error getting suggestions: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail="Suggestions failed")


@router.get("/", response_model=List[PharmacyList])
async def list_pharmacies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_async_session)
):
    """List all pharmacies with optional filtering."""
    try:
        query = select(Pharmacy)
        
        # Apply filters
        filters = []
        if active_only:
            filters.append(Pharmacy.is_active == True)
        if city:
            filters.append(Pharmacy.city.ilike(f"%{city.strip()}%"))
        if state:
            filters.append(Pharmacy.state.ilike(f"%{state.strip()}%"))
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        pharmacies = result.scalars().all()
        
        return pharmacies
    except ValueError as e:
        logger.error(f"Validation error listing pharmacies: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error listing pharmacies: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve pharmacies")


@router.get("/{pharmacy_id}", response_model=PharmacyResponse)
async def get_pharmacy(
    pharmacy_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """Get pharmacy by ID."""
    try:
        pharmacy_service = PharmacyService(db)
        pharmacy = await pharmacy_service.get_pharmacy(pharmacy_id)
        return pharmacy
    except PharmacyNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Pharmacy not found: {e}")
        raise HTTPException(status_code=404, detail="Pharmacy not found")
    except Exception as e:
        logger.error(f"Unexpected error getting pharmacy {pharmacy_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve pharmacy")


@router.put("/{pharmacy_id}", response_model=PharmacyResponse)
async def update_pharmacy(
    pharmacy_id: UUID,
    pharmacy_data: PharmacyUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    """Update pharmacy information."""
    try:
        pharmacy_service = PharmacyService(db)
        pharmacy = await pharmacy_service.update_pharmacy(pharmacy_id, pharmacy_data)
        logger.info(f"Updated pharmacy: {pharmacy_id}")
        return pharmacy
    except PharmacyNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Validation error updating pharmacy: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error updating pharmacy {pharmacy_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update pharmacy")


@router.delete("/{pharmacy_id}")
async def delete_pharmacy(
    pharmacy_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """Soft delete pharmacy."""
    try:
        pharmacy_service = PharmacyService(db)
        await pharmacy_service.delete_pharmacy(pharmacy_id)
        logger.info(f"Deleted pharmacy: {pharmacy_id}")
        return {"message": "Pharmacy deleted successfully"}
    except PharmacyNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Pharmacy not found for deletion: {e}")
        raise HTTPException(status_code=404, detail="Pharmacy not found")
    except Exception as e:
        logger.error(f"Unexpected error deleting pharmacy {pharmacy_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete pharmacy")


@router.get("/{pharmacy_id}/nearby")
async def get_nearby_pharmacies(
    pharmacy_id: UUID,
    radius_km: float = Query(10.0, ge=1.0, le=100.0),
    db: AsyncSession = Depends(get_async_session)
):
    """Get nearby pharmacies within specified radius."""
    try:
        pharmacy_service = PharmacyService(db)
        nearby_pharmacies = await pharmacy_service.get_nearby_pharmacies(pharmacy_id, radius_km)
        return nearby_pharmacies
    except PharmacyNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error finding nearby pharmacies for {pharmacy_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{pharmacy_id}/verify")
async def verify_pharmacy(
    pharmacy_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """Verify pharmacy credentials and licenses."""
    try:
        pharmacy_service = PharmacyService(db)
        verification_result = await pharmacy_service.verify_pharmacy(pharmacy_id)
        logger.info(f"Verified pharmacy: {pharmacy_id}")
        return verification_result
    except PharmacyNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error verifying pharmacy {pharmacy_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{pharmacy_id}/inventory", response_model=InventoryItemResponse)
async def add_pharmacy_inventory_item(
    pharmacy_id: UUID,
    inventory_data: dict,
    db: AsyncSession = Depends(get_async_session)
):
    """Add inventory item to pharmacy."""
    try:
        # First check if pharmacy exists
        pharmacy_service = PharmacyService(db)
        await pharmacy_service.get_pharmacy(pharmacy_id)
        
        # Create inventory update object
        from app.schemas.inventory import InventoryUpdate
        from datetime import date
        from decimal import Decimal
        
        # Convert the inventory data to match what the service expects
        update_data = InventoryUpdate(
            medicine_id=UUID(inventory_data["medicine_id"]) if isinstance(inventory_data["medicine_id"], str) else inventory_data["medicine_id"],
            quantity=inventory_data.get("current_stock", 0),
            cost_price=Decimal(str(inventory_data.get("cost_price", 0))),
            selling_price=Decimal(str(inventory_data.get("selling_price", 0))),
            mrp=Decimal(str(inventory_data.get("mrp", 0))),
            batch_number="BATCH-" + str(UUID(inventory_data["medicine_id"]))[:8] if isinstance(inventory_data["medicine_id"], str) else "BATCH-" + str(inventory_data["medicine_id"])[:8],
            manufacturing_date=date.today(),
            expiry_date=date.today().replace(year=date.today().year + 2)  # 2 years from now
        )
        
        # Add inventory item
        from app.services.inventory_service import InventoryService
        inventory_service = InventoryService(db)
        inventory_item = await inventory_service.add_medicine_batch(pharmacy_id, update_data)
        
        logger.info(f"Added inventory item for pharmacy {pharmacy_id}")
        return inventory_item
    except PharmacyNotFoundException as e:
        logger.error(f"Pharmacy not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error adding inventory item: {e}")
        raise HTTPException(status_code=500, detail="Failed to add inventory item")


@router.get("/{pharmacy_id}/inventory", response_model=List[InventoryItemResponse])
async def get_pharmacy_inventory(
    pharmacy_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """Get all inventory items for a pharmacy."""
    try:
        # First check if pharmacy exists
        pharmacy_service = PharmacyService(db)
        await pharmacy_service.get_pharmacy(pharmacy_id)
        
        # Get inventory
        from app.services.inventory_service import InventoryService
        inventory_service = InventoryService(db)
        inventory_items = await inventory_service.get_pharmacy_inventory(pharmacy_id)
        
        logger.info(f"Retrieved inventory for pharmacy {pharmacy_id}")
        return inventory_items
    except PharmacyNotFoundException as e:
        logger.error(f"Pharmacy not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting inventory: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve inventory")


@router.get("/{pharmacy_id}/inventory/low-stock", response_model=List[InventoryItemResponse])
async def get_low_stock_items(
    pharmacy_id: UUID,
    threshold: Optional[int] = Query(None, description="Custom threshold for low stock"),
    db: AsyncSession = Depends(get_async_session)
):
    """Get low stock items for a pharmacy."""
    try:
        # First check if pharmacy exists
        pharmacy_service = PharmacyService(db)
        await pharmacy_service.get_pharmacy(pharmacy_id)
        
        # Get low stock items
        from app.services.inventory_service import InventoryService
        inventory_service = InventoryService(db)
        low_stock_items = await inventory_service.get_low_stock_items(pharmacy_id, threshold)
        
        logger.info(f"Retrieved low stock items for pharmacy {pharmacy_id}")
        return low_stock_items
    except PharmacyNotFoundException as e:
        logger.error(f"Pharmacy not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting low stock items: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve low stock items")


@router.post("/{pharmacy_id}/prescriptions", response_model=PrescriptionResponse)
async def create_pharmacy_prescription(
    pharmacy_id: UUID,
    prescription_data: PrescriptionCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new prescription for a pharmacy."""
    try:
        # First check if pharmacy exists
        pharmacy_service = PharmacyService(db)
        await pharmacy_service.get_pharmacy(pharmacy_id)
        
        # Create prescription
        prescription_service = PrescriptionService(db)
        prescription = await prescription_service.create_prescription(pharmacy_id, prescription_data)
        
        logger.info(f"Created prescription for pharmacy {pharmacy_id}")
        return prescription
    except PharmacyNotFoundException as e:
        logger.error(f"Pharmacy not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Validation error creating prescription: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating prescription: {e}")
        raise HTTPException(status_code=500, detail="Failed to create prescription")


@router.get("/{pharmacy_id}/prescriptions", response_model=list[PrescriptionResponse])
async def get_pharmacy_prescriptions(
    pharmacy_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """Get all prescriptions for a pharmacy."""
    try:
        # First check if pharmacy exists
        pharmacy_service = PharmacyService(db)
        await pharmacy_service.get_pharmacy(pharmacy_id)
        
        # Get prescriptions
        from sqlalchemy import select
        from app.models.prescription import Prescription
        
        query = select(Prescription).where(Prescription.pharmacy_id == pharmacy_id)
        result = await db.execute(query)
        prescriptions = result.scalars().all()
        
        logger.info(f"Retrieved {len(prescriptions)} prescriptions for pharmacy {pharmacy_id}")
        return prescriptions
    except PharmacyNotFoundException as e:
        logger.error(f"Pharmacy not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting prescriptions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve prescriptions")