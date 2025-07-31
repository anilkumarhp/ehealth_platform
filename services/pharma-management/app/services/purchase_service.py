"""
Purchase management service
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import logging
from datetime import datetime, date
import uuid

from app.models.purchase import PurchaseOrder, PurchaseOrderItem, GoodsReceiptNote, GoodsReceiptNoteItem
from app.repositories.base_repository import BaseRepository
from app.schemas.inventory import PurchaseOrderCreate, PurchaseOrderResponse, GRNCreate, GRNResponse
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class PurchaseService:
    """Service for purchase management operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.po_repo = BaseRepository(db, PurchaseOrder)
        self.po_item_repo = BaseRepository(db, PurchaseOrderItem)
        self.grn_repo = BaseRepository(db, GoodsReceiptNote)
        self.grn_item_repo = BaseRepository(db, GoodsReceiptNoteItem)
        self.audit_service = AuditService(db)
    
    async def create_purchase_order(self, purchase_data: PurchaseOrderCreate) -> PurchaseOrderResponse:
        """Create a purchase order to supplier."""
        try:
            # Generate PO number
            po_number = await self._generate_po_number()
            
            # Calculate totals
            subtotal = sum(item.get('unit_price', 0) * item.get('quantity', 0) for item in purchase_data.items)
            tax_amount = subtotal * 0.18  # 18% GST
            total_amount = subtotal + tax_amount
            
            # Create purchase order
            po_dict = {
                "po_number": po_number,
                "pharmacy_id": purchase_data.pharmacy_id,
                "supplier_id": purchase_data.supplier_id,
                "order_date": date.today(),
                "expected_delivery_date": purchase_data.expected_delivery_date,
                "status": "pending",
                "subtotal": subtotal,
                "tax_amount": tax_amount,
                "total_amount": total_amount,
                "notes": purchase_data.notes,
                "requested_by": UUID("00000000-0000-0000-0000-000000000000")  # Would get from auth context
            }
            
            purchase_order = await self.po_repo.create(po_dict)
            
            # Create PO items
            for item_data in purchase_data.items:
                po_item_dict = {
                    "purchase_order_id": purchase_order.id,
                    "medicine_id": item_data.get('medicine_id'),
                    "medicine_name": item_data.get('medicine_name', 'Unknown'),
                    "strength": item_data.get('strength', 'Unknown'),
                    "manufacturer": item_data.get('manufacturer', 'Unknown'),
                    "quantity_ordered": item_data.get('quantity', 0),
                    "unit": item_data.get('unit', 'units'),
                    "unit_price": item_data.get('unit_price', 0),
                    "total_price": item_data.get('unit_price', 0) * item_data.get('quantity', 0),
                    "quantity_pending": item_data.get('quantity', 0)
                }
                
                await self.po_item_repo.create(po_item_dict)
            
            # Log audit trail
            await self.audit_service.log_action(
                action="purchase_order_created",
                resource_type="purchase_order",
                resource_id=purchase_order.id,
                pharmacy_id=purchase_data.pharmacy_id,
                description=f"Created purchase order {po_number}",
                metadata={
                    "po_number": po_number,
                    "supplier_id": str(purchase_data.supplier_id),
                    "total_amount": float(total_amount),
                    "items_count": len(purchase_data.items)
                }
            )
            
            response = PurchaseOrderResponse.from_orm(purchase_order)
            
            logger.info(f"Created purchase order {po_number}")
            return response
        except Exception as e:
            logger.error(f"Error creating purchase order: {e}")
            raise
    
    async def create_grn(self, grn_data: GRNCreate) -> GRNResponse:
        """Create Goods Receipt Note for incoming stock."""
        try:
            # Generate GRN number
            grn_number = await self._generate_grn_number()
            
            # Get purchase order
            purchase_order = await self.po_repo.get_by_id(grn_data.purchase_order_id)
            if not purchase_order:
                raise ValueError("Purchase order not found")
            
            # Create GRN
            grn_dict = {
                "grn_number": grn_number,
                "purchase_order_id": grn_data.purchase_order_id,
                "pharmacy_id": purchase_order.pharmacy_id,
                "supplier_id": purchase_order.supplier_id,
                "receipt_date": date.today(),
                "invoice_number": grn_data.invoice_number,
                "invoice_date": grn_data.invoice_date,
                "status": "pending",
                "quality_check_done": False,
                "received_by": UUID("00000000-0000-0000-0000-000000000000"),  # Would get from auth context
                "notes": grn_data.notes
            }
            
            grn = await self.grn_repo.create(grn_dict)
            
            # Create GRN items
            for item_data in grn_data.items:
                grn_item_dict = {
                    "grn_id": grn.id,
                    "po_item_id": item_data.get('po_item_id'),
                    "medicine_id": item_data.get('medicine_id'),
                    "medicine_name": item_data.get('medicine_name', 'Unknown'),
                    "batch_number": item_data.get('batch_number', ''),
                    "manufacturing_date": item_data.get('manufacturing_date', date.today()),
                    "expiry_date": item_data.get('expiry_date', date.today()),
                    "quantity_ordered": item_data.get('quantity_ordered', 0),
                    "quantity_received": item_data.get('quantity_received', 0),
                    "quantity_accepted": item_data.get('quantity_accepted', 0),
                    "unit_price": item_data.get('unit_price', 0),
                    "total_value": item_data.get('unit_price', 0) * item_data.get('quantity_accepted', 0),
                    "quality_status": "pending"
                }
                
                await self.grn_item_repo.create(grn_item_dict)
            
            # Log audit trail
            await self.audit_service.log_action(
                action="grn_created",
                resource_type="goods_receipt_note",
                resource_id=grn.id,
                pharmacy_id=purchase_order.pharmacy_id,
                description=f"Created GRN {grn_number}",
                metadata={
                    "grn_number": grn_number,
                    "po_number": purchase_order.po_number,
                    "items_count": len(grn_data.items)
                }
            )
            
            response = GRNResponse.from_orm(grn)
            
            logger.info(f"Created GRN {grn_number}")
            return response
        except Exception as e:
            logger.error(f"Error creating GRN: {e}")
            raise
    
    async def _generate_po_number(self) -> str:
        """Generate unique purchase order number."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            po_number = f"PO-{timestamp}"
            return po_number
        except Exception as e:
            logger.error(f"Error generating PO number: {e}")
            return f"PO-{str(uuid.uuid4())[:8].upper()}"
    
    async def _generate_grn_number(self) -> str:
        """Generate unique GRN number."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            grn_number = f"GRN-{timestamp}"
            return grn_number
        except Exception as e:
            logger.error(f"Error generating GRN number: {e}")
            return f"GRN-{str(uuid.uuid4())[:8].upper()}"