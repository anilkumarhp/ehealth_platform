"""
Order management service
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from uuid import UUID
import logging
from datetime import datetime
import uuid

from app.models.order import Order, OrderItem, OrderStatusEnum
from app.models.prescription import Prescription
from app.repositories.base_repository import BaseRepository
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate, OrderList
from app.core.exceptions import OrderNotFoundException, PrescriptionNotFoundException
from app.services.audit_service import AuditService
from app.services.inventory_service import InventoryService

logger = logging.getLogger(__name__)


class OrderService:
    """Service for order management operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = BaseRepository(db, Order)
        self.order_item_repo = BaseRepository(db, OrderItem)
        self.audit_service = AuditService(db)
        self.inventory_service = InventoryService(db)
    
    async def create_order(self, order_data: OrderCreate) -> OrderResponse:
        """Create a new order from prescription."""
        try:
            # Verify prescription exists
            prescription_result = await self.db.execute(
                select(Prescription).where(Prescription.id == order_data.prescription_id)
            )
            prescription = prescription_result.scalar_one_or_none()
            if not prescription:
                raise PrescriptionNotFoundException(str(order_data.prescription_id))
            
            # Generate order number
            order_number = await self._generate_order_number(order_data.pharmacy_id)
            
            # Calculate totals
            subtotal = sum(item.unit_price * item.quantity for item in order_data.items)
            tax_amount = subtotal * 0.18  # 18% GST
            total_amount = subtotal + tax_amount
            
            # Create order
            order_dict = {
                "order_number": order_number,
                "prescription_id": order_data.prescription_id,
                "pharmacy_id": order_data.pharmacy_id,
                "patient_id": order_data.patient_id,
                "patient_name": order_data.patient_name,
                "patient_phone": order_data.patient_phone,
                "patient_email": order_data.patient_email,
                "status": OrderStatusEnum.PENDING.value,
                "order_date": datetime.utcnow(),
                "delivery_type": order_data.delivery_type,
                "delivery_address": order_data.delivery_address,
                "delivery_instructions": order_data.delivery_instructions,
                "subtotal": subtotal,
                "tax_amount": tax_amount,
                "total_amount": total_amount,
                "payment_status": "pending",
                "urgent": order_data.urgent
            }
            
            order = await self.order_repo.create(order_dict)
            
            # Create order items
            order_items = []
            for item_data in order_data.items:
                order_item_dict = {
                    "order_id": order.id,
                    "medicine_id": item_data.medicine_id,
                    "medicine_name": f"Medicine-{str(item_data.medicine_id)[:8]}",  # Would get from medicine table
                    "strength": "Unknown",  # Would get from medicine table
                    "dosage_form": "Unknown",  # Would get from medicine table
                    "manufacturer": "Unknown",  # Would get from medicine table
                    "quantity_ordered": item_data.quantity,
                    "unit_price": item_data.unit_price,
                    "total_price": item_data.unit_price * item_data.quantity,
                    "status": "pending"
                }
                
                order_item = await self.order_item_repo.create(order_item_dict)
                order_items.append(order_item)
            
            # Reserve inventory
            medicine_quantities = [
                {"medicine_id": item.medicine_id, "quantity": item.quantity}
                for item in order_data.items
            ]
            await self.inventory_service.reserve_medicines(order_data.pharmacy_id, medicine_quantities)
            
            # Log audit trail
            await self.audit_service.log_order_action(
                action="order_created",
                order_id=order.id,
                pharmacy_id=order_data.pharmacy_id,
                description=f"Created order {order_number}",
                metadata={
                    "order_number": order_number,
                    "total_amount": float(total_amount),
                    "items_count": len(order_items),
                    "urgent": order_data.urgent
                }
            )
            
            # Convert to response format
            response = OrderResponse.from_orm(order)
            response.items = [item for item in order_items]  # Would convert to OrderItemResponse
            
            logger.info(f"Created order {order_number}")
            return response
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise
    
    async def get_order(self, order_id: UUID) -> OrderResponse:
        """Get order details."""
        try:
            order = await self.order_repo.get_by_id(order_id)
            if not order:
                raise OrderNotFoundException(str(order_id))
            
            # Get order items
            order_items = await self.order_item_repo.get_multi(
                filters={"order_id": order_id}
            )
            
            # Convert to response format
            response = OrderResponse.from_orm(order)
            response.items = [item for item in order_items]  # Would convert to OrderItemResponse
            
            return response
        except Exception as e:
            logger.error(f"Error getting order {order_id}: {e}")
            raise
    
    async def get_patient_orders(
        self, 
        patient_id: UUID, 
        skip: int = 0, 
        limit: int = 50,
        status: Optional[str] = None
    ) -> List[OrderList]:
        """Get order history for a patient."""
        try:
            filters = {"patient_id": patient_id}
            if status:
                filters["status"] = status
            
            orders = await self.order_repo.get_multi(
                skip=skip,
                limit=limit,
                filters=filters,
                order_by="order_date"
            )
            
            logger.info(f"Retrieved {len(orders)} orders for patient {patient_id}")
            return [OrderList.from_orm(order) for order in orders]
        except Exception as e:
            logger.error(f"Error getting patient orders: {e}")
            raise
    
    async def update_order_status(
        self, 
        order_id: UUID, 
        status_update: OrderStatusUpdate
    ) -> OrderResponse:
        """Update order status."""
        try:
            order = await self.order_repo.get_by_id(order_id)
            if not order:
                raise OrderNotFoundException(str(order_id))
            
            old_status = order.status
            
            # Update order status
            update_data = {
                "status": status_update.status,
                "updated_at": datetime.utcnow()
            }
            
            if status_update.status == "ready":
                update_data["actual_ready_time"] = datetime.utcnow()
            
            updated_order = await self.order_repo.update(order_id, update_data)
            
            # Log audit trail
            await self.audit_service.log_order_action(
                action="order_status_updated",
                order_id=order_id,
                user_id=status_update.updated_by,
                description=f"Updated order status from {old_status} to {status_update.status}",
                metadata={
                    "old_status": old_status,
                    "new_status": status_update.status,
                    "notes": status_update.notes
                }
            )
            
            # Get updated order with items
            response = await self.get_order(order_id)
            
            logger.info(f"Updated order {order_id} status to {status_update.status}")
            return response
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            raise
    
    async def validate_order(self, order_id: UUID, pharmacist_id: UUID) -> OrderResponse:
        """Validate order by pharmacist."""
        try:
            order = await self.order_repo.get_by_id(order_id)
            if not order:
                raise OrderNotFoundException(str(order_id))
            
            # Update order with pharmacist validation
            update_data = {
                "pharmacist_id": pharmacist_id,
                "quality_check_passed": True,
                "status": OrderStatusEnum.CONFIRMED.value,
                "updated_at": datetime.utcnow()
            }
            
            updated_order = await self.order_repo.update(order_id, update_data)
            
            # Log audit trail
            await self.audit_service.log_order_action(
                action="order_validated",
                order_id=order_id,
                user_id=pharmacist_id,
                description=f"Order validated by pharmacist",
                metadata={"pharmacist_id": str(pharmacist_id)}
            )
            
            # Get updated order with items
            response = await self.get_order(order_id)
            
            logger.info(f"Validated order {order_id} by pharmacist {pharmacist_id}")
            return response
        except Exception as e:
            logger.error(f"Error validating order: {e}")
            raise
    
    async def _generate_order_number(self, pharmacy_id: UUID) -> str:
        """Generate unique order number."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            order_number = f"ORD-{str(pharmacy_id)[:8].upper()}-{timestamp}"
            return order_number
        except Exception as e:
            logger.error(f"Error generating order number: {e}")
            return f"ORD-{str(uuid.uuid4())[:8].upper()}"