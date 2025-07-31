"""
Order management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
import logging

from app.db.session import get_async_session
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate, OrderList
from app.services.order_service import OrderService
from app.core.exceptions import OrderNotFoundException, PrescriptionNotFoundException

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new order from prescription."""
    try:
        order_service = OrderService(db)
        order = await order_service.create_order(order_data)
        return order
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """Get complete order details."""
    try:
        order_service = OrderService(db)
        order = await order_service.get_order(order_id)
        return order
    except Exception as e:
        logger.error(f"Error getting order: {e}")
        raise HTTPException(status_code=404, detail="Order not found")


@router.get("/patients/{patient_id}/orders", response_model=List[OrderList])
async def get_patient_orders(
    patient_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_session)
):
    """Get order history for a patient."""
    try:
        order_service = OrderService(db)
        orders = await order_service.get_patient_orders(patient_id, skip, limit, status)
        return orders
    except Exception as e:
        logger.error(f"Error getting patient orders: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: UUID,
    status_update: OrderStatusUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    """Update order status."""
    try:
        order_service = OrderService(db)
        order = await order_service.update_order_status(order_id, status_update)
        return order
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/validate", response_model=OrderResponse)
async def validate_order(
    order_id: UUID,
    pharmacist_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """Validate order by pharmacist before processing."""
    try:
        order_service = OrderService(db)
        order = await order_service.validate_order(order_id, pharmacist_id)
        return order
    except Exception as e:
        logger.error(f"Error validating order: {e}")
        raise HTTPException(status_code=400, detail=str(e))