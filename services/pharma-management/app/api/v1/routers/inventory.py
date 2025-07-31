"""
Inventory management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
import logging

from app.db.session import get_async_session
from app.schemas.inventory import (
    InventoryItemResponse, InventoryUpdate, InventoryAvailability,
    PurchaseOrderCreate, PurchaseOrderResponse, GRNCreate, GRNResponse
)
from app.services.inventory_service import InventoryService
from app.services.purchase_service import PurchaseService
from app.core.exceptions import MedicineNotFoundException, InsufficientStockException

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{pharmacy_id}/inventory", response_model=InventoryItemResponse)
async def add_inventory_item(
    pharmacy_id: UUID,
    inventory_data: InventoryUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    """Add a new inventory item to pharmacy."""
    return await add_medicine_batch(pharmacy_id, inventory_data, db)


@router.post("/{pharmacy_id}/medicines", response_model=InventoryItemResponse)
async def add_medicine_batch(
    pharmacy_id: UUID,
    inventory_data: InventoryUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    """Add a new batch of medicine to pharmacy inventory."""
    try:
        inventory_service = InventoryService(db)
        inventory_item = await inventory_service.add_medicine_batch(pharmacy_id, inventory_data)
        logger.info(f"Successfully added medicine batch to pharmacy {pharmacy_id}")
        return inventory_item
    except MedicineNotFoundException as e:
        logger.error(f"Medicine not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error adding medicine batch: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{pharmacy_id}/medicines/{inventory_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    pharmacy_id: UUID,
    inventory_id: UUID,
    inventory_data: InventoryUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    """Update inventory item quantity or price."""
    try:
        inventory_service = InventoryService(db)
        inventory_item = await inventory_service.update_inventory_item(
            pharmacy_id, inventory_id, inventory_data
        )
        return inventory_item
    except Exception as e:
        logger.error(f"Error updating inventory item: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/availability", response_model=List[InventoryAvailability])
async def check_medicine_availability(
    medicine_ids: str = Query(..., description="Comma-separated medicine IDs"),
    pharmacy_id: Optional[UUID] = Query(None),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    radius_km: float = Query(10.0, ge=1, le=50),
    db: AsyncSession = Depends(get_async_session)
):
    """Check real-time availability of medicines."""
    try:
        medicine_id_list = [UUID(id.strip()) for id in medicine_ids.split(",")]
        inventory_service = InventoryService(db)
        availability = await inventory_service.check_availability(
            medicine_id_list, pharmacy_id, latitude, longitude, radius_km
        )
        return availability
    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/purchases", response_model=PurchaseOrderResponse)
async def create_purchase_order(
    purchase_data: PurchaseOrderCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """Create a purchase order to supplier."""
    try:
        purchase_service = PurchaseService(db)
        purchase_order = await purchase_service.create_purchase_order(purchase_data)
        return purchase_order
    except Exception as e:
        logger.error(f"Error creating purchase order: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/grn", response_model=GRNResponse)
async def create_goods_receipt_note(
    grn_data: GRNCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """Create Goods Receipt Note for incoming stock."""
    try:
        purchase_service = PurchaseService(db)
        grn = await purchase_service.create_grn(grn_data)
        return grn
    except Exception as e:
        logger.error(f"Error creating GRN: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{pharmacy_id}/inventory", response_model=List[InventoryItemResponse])
async def get_pharmacy_inventory(
    pharmacy_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """Get all inventory items for a pharmacy."""
    try:
        inventory_service = InventoryService(db)
        inventory_items = await inventory_service.get_pharmacy_inventory(pharmacy_id)
        return inventory_items
    except Exception as e:
        logger.error(f"Error getting pharmacy inventory: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve inventory")


@router.get("/{pharmacy_id}/inventory/low-stock", response_model=List[InventoryItemResponse])
async def get_low_stock_items(
    pharmacy_id: UUID,
    threshold: Optional[int] = Query(None, description="Custom threshold for low stock"),
    db: AsyncSession = Depends(get_async_session)
):
    """Get low stock items for a pharmacy."""
    try:
        inventory_service = InventoryService(db)
        low_stock_items = await inventory_service.get_low_stock_items(pharmacy_id, threshold)
        return low_stock_items
    except Exception as e:
        logger.error(f"Error getting low stock items: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve low stock items")