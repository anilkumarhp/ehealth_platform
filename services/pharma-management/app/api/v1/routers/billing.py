"""
Billing and invoice management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import logging

from app.db.session import get_async_session
from app.schemas.billing import InvoiceCreate, InvoiceResponse, InvoiceNotification
from app.services.billing_service import BillingService
from app.core.exceptions import PharmacyNotFoundException, OrderNotFoundException

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/invoices", response_model=InvoiceResponse)
async def generate_invoice(
    invoice_data: InvoiceCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """Generate GST-compliant invoice for order."""
    try:
        billing_service = BillingService(db)
        invoice = await billing_service.generate_invoice(invoice_data)
        logger.info(f"Successfully generated invoice for order {invoice_data.order_id}")
        return invoice
    except OrderNotFoundException as e:
        logger.error(f"Order not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except PharmacyNotFoundException as e:
        logger.error(f"Pharmacy not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error generating invoice: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """Get invoice details."""
    try:
        billing_service = BillingService(db)
        invoice = await billing_service.get_invoice(invoice_id)
        logger.info(f"Retrieved invoice {invoice_id}")
        return invoice
    except ValueError as e:
        logger.error(f"Invoice not found: {e}")
        raise HTTPException(status_code=404, detail="Invoice not found")
    except Exception as e:
        logger.error(f"Unexpected error getting invoice {invoice_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/invoices/{invoice_id}/notify", response_model=InvoiceNotification)
async def notify_invoice(
    invoice_id: UUID,
    notification_method: str = "email",  # email, whatsapp, sms
    db: AsyncSession = Depends(get_async_session)
):
    """Send invoice to patient via Email/WhatsApp."""
    try:
        billing_service = BillingService(db)
        notification_result = await billing_service.send_invoice_notification(
            invoice_id, notification_method
        )
        logger.info(f"Successfully sent invoice notification for {invoice_id}")
        return notification_result
    except ValueError as e:
        logger.error(f"Invoice not found for notification: {e}")
        raise HTTPException(status_code=404, detail="Invoice not found")
    except Exception as e:
        logger.error(f"Unexpected error sending notification for {invoice_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")