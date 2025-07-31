"""
Billing service for invoice generation and payment processing
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID
import logging
from datetime import datetime, date
from decimal import Decimal
import uuid

from app.models.billing import Invoice, InvoiceItem, Payment
from app.models.order import Order, OrderItem
from app.models.pharmacy import Pharmacy
from app.repositories.base_repository import BaseRepository
from app.schemas.billing import InvoiceCreate, InvoiceResponse, InvoiceNotification, InvoiceItemResponse
from app.core.exceptions import OrderNotFoundException, PharmacyNotFoundException
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class BillingService:
    """Service for billing and invoice operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.invoice_repo = BaseRepository(db, Invoice)
        self.invoice_item_repo = BaseRepository(db, InvoiceItem)
        self.payment_repo = BaseRepository(db, Payment)
        self.audit_service = AuditService(db)
    
    async def generate_invoice(self, invoice_data: InvoiceCreate) -> InvoiceResponse:
        """Generate GST-compliant invoice for order."""
        try:
            # Verify order exists
            order_result = await self.db.execute(
                select(Order).where(Order.id == invoice_data.order_id)
            )
            order = order_result.scalar_one_or_none()
            if not order:
                raise OrderNotFoundException(str(invoice_data.order_id))
            
            # Verify pharmacy exists
            pharmacy_result = await self.db.execute(
                select(Pharmacy).where(Pharmacy.id == invoice_data.pharmacy_id)
            )
            pharmacy = pharmacy_result.scalar_one_or_none()
            if not pharmacy:
                raise PharmacyNotFoundException(str(invoice_data.pharmacy_id))
            
            # Generate invoice number
            invoice_number = await self._generate_invoice_number(invoice_data.pharmacy_id)
            
            # Calculate totals
            subtotal = Decimal('0.00')
            total_cgst = Decimal('0.00')
            total_sgst = Decimal('0.00')
            total_igst = Decimal('0.00')
            
            for item in invoice_data.items:
                item_total = item.unit_price * item.quantity
                discount_amount = (item_total * item.discount_percentage) / 100
                taxable_amount = item_total - discount_amount
                
                # Calculate GST (simplified - assuming intra-state)
                gst_amount = (taxable_amount * item.gst_rate) / 100
                cgst_amount = gst_amount / 2
                sgst_amount = gst_amount / 2
                
                subtotal += taxable_amount
                total_cgst += cgst_amount
                total_sgst += sgst_amount
            
            # Calculate final total
            total_amount = (
                subtotal + 
                total_cgst + 
                total_sgst + 
                total_igst +
                invoice_data.delivery_charges +
                invoice_data.packaging_charges +
                invoice_data.other_charges -
                invoice_data.discount_amount
            )
            
            # Create invoice
            invoice_dict = {
                "invoice_number": invoice_number,
                "order_id": invoice_data.order_id,
                "pharmacy_id": invoice_data.pharmacy_id,
                "patient_id": invoice_data.patient_id,
                "patient_name": invoice_data.patient_name,
                "patient_phone": invoice_data.patient_phone,
                "patient_email": invoice_data.patient_email,
                "billing_address": invoice_data.billing_address,
                "invoice_date": date.today(),
                "subtotal": subtotal,
                "discount_amount": invoice_data.discount_amount,
                "cgst_amount": total_cgst,
                "sgst_amount": total_sgst,
                "igst_amount": total_igst,
                "delivery_charges": invoice_data.delivery_charges,
                "packaging_charges": invoice_data.packaging_charges,
                "other_charges": invoice_data.other_charges,
                "total_amount": total_amount,
                "amount_due": total_amount,
                "gstin": pharmacy.tax_id,  # Assuming tax_id is GSTIN
                "place_of_supply": f"{pharmacy.state}, {pharmacy.country}",
                "notes": invoice_data.notes,
                "status": "generated"
            }
            
            invoice = await self.invoice_repo.create(invoice_dict)
            
            # Create invoice items
            invoice_items = []
            for item_data in invoice_data.items:
                # Get order item details
                order_item_result = await self.db.execute(
                    select(OrderItem).where(OrderItem.id == item_data.order_item_id)
                )
                order_item = order_item_result.scalar_one_or_none()
                
                if order_item:
                    item_total = item_data.unit_price * item_data.quantity
                    discount_amount = (item_total * item_data.discount_percentage) / 100
                    taxable_amount = item_total - discount_amount
                    
                    # Calculate GST
                    gst_amount = (taxable_amount * item_data.gst_rate) / 100
                    cgst_amount = gst_amount / 2
                    sgst_amount = gst_amount / 2
                    final_amount = taxable_amount + gst_amount
                    
                    invoice_item_dict = {
                        "invoice_id": invoice.id,
                        "order_item_id": item_data.order_item_id,
                        "medicine_id": item_data.medicine_id,
                        "medicine_name": order_item.medicine_name,
                        "strength": order_item.strength,
                        "manufacturer": order_item.manufacturer,
                        "batch_number": order_item.batch_number,
                        "quantity": item_data.quantity,
                        "unit_price": item_data.unit_price,
                        "total_price": item_total,
                        "discount_percentage": item_data.discount_percentage,
                        "discount_amount": discount_amount,
                        "gst_rate": item_data.gst_rate,
                        "cgst_amount": cgst_amount,
                        "sgst_amount": sgst_amount,
                        "igst_amount": Decimal('0.00'),
                        "taxable_amount": taxable_amount,
                        "final_amount": final_amount
                    }
                    
                    invoice_item = await self.invoice_item_repo.create(invoice_item_dict)
                    invoice_items.append(invoice_item)
            
            # Log audit trail
            await self.audit_service.log_action(
                action="invoice_generated",
                resource_type="invoice",
                resource_id=invoice.id,
                pharmacy_id=invoice_data.pharmacy_id,
                description=f"Generated invoice {invoice_number} for order {invoice_data.order_id}",
                metadata={
                    "invoice_number": invoice_number,
                    "total_amount": float(total_amount),
                    "items_count": len(invoice_items)
                }
            )
            
            # Convert to response format
            response = InvoiceResponse.from_orm(invoice)
            response.items = [InvoiceItemResponse.from_orm(item) for item in invoice_items]
            
            logger.info(f"Generated invoice {invoice_number} for order {invoice_data.order_id}")
            return response
        except Exception as e:
            logger.error(f"Error generating invoice: {e}")
            raise
    
    async def get_invoice(self, invoice_id: UUID) -> InvoiceResponse:
        """Get invoice details."""
        try:
            invoice = await self.invoice_repo.get_by_id(invoice_id)
            if not invoice:
                raise ValueError("Invoice not found")
            
            # Get invoice items
            invoice_items = await self.invoice_item_repo.get_multi(
                filters={"invoice_id": invoice_id}
            )
            
            # Convert to response format
            response = InvoiceResponse.from_orm(invoice)
            response.items = [InvoiceItemResponse.from_orm(item) for item in invoice_items]
            
            return response
        except Exception as e:
            logger.error(f"Error getting invoice {invoice_id}: {e}")
            raise
    
    async def send_invoice_notification(
        self, 
        invoice_id: UUID, 
        notification_method: str
    ) -> InvoiceNotification:
        """Send invoice notification to patient."""
        try:
            invoice = await self.invoice_repo.get_by_id(invoice_id)
            if not invoice:
                raise ValueError("Invoice not found")
            
            # Simulate notification sending
            # In production, this would integrate with actual notification services
            success = True
            message = f"Invoice {invoice.invoice_number} sent via {notification_method}"
            
            # Update invoice notification status
            await self.invoice_repo.update(invoice_id, {
                "notification_sent": True,
                "notification_sent_at": datetime.utcnow(),
                "notification_method": notification_method
            })
            
            # Log audit trail
            await self.audit_service.log_action(
                action="invoice_notification_sent",
                resource_type="invoice",
                resource_id=invoice_id,
                description=f"Sent invoice notification via {notification_method}",
                metadata={
                    "invoice_number": invoice.invoice_number,
                    "method": notification_method,
                    "recipient": invoice.patient_email or invoice.patient_phone
                }
            )
            
            response = InvoiceNotification(
                invoice_id=invoice_id,
                notification_method=notification_method,
                success=success,
                message=message,
                sent_at=datetime.utcnow().isoformat(),
                delivery_status="sent"
            )
            
            logger.info(f"Sent invoice notification for {invoice.invoice_number}")
            return response
        except Exception as e:
            logger.error(f"Error sending invoice notification: {e}")
            raise
    
    async def _generate_invoice_number(self, pharmacy_id: UUID) -> str:
        """Generate unique invoice number."""
        try:
            # Get pharmacy code (first 3 letters of name)
            pharmacy_result = await self.db.execute(
                select(Pharmacy.name).where(Pharmacy.id == pharmacy_id)
            )
            pharmacy_name = pharmacy_result.scalar_one_or_none()
            pharmacy_code = pharmacy_name[:3].upper() if pharmacy_name else "PHA"
            
            # Generate invoice number with timestamp
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            invoice_number = f"INV-{pharmacy_code}-{timestamp}"
            
            return invoice_number
        except Exception as e:
            logger.error(f"Error generating invoice number: {e}")
            # Fallback to UUID-based number
            return f"INV-{str(uuid.uuid4())[:8].upper()}"