"""
Billing and invoice schemas
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date
from decimal import Decimal


class InvoiceItemCreate(BaseModel):
    """Schema for creating invoice items."""
    order_item_id: UUID
    medicine_id: UUID
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)
    discount_percentage: Decimal = Field(default=0, ge=0, le=100)
    gst_rate: Decimal = Field(..., ge=0, le=100)


class InvoiceCreate(BaseModel):
    """Schema for creating invoices."""
    order_id: UUID
    pharmacy_id: UUID
    patient_id: UUID
    patient_name: str = Field(..., min_length=2, max_length=255)
    patient_phone: str = Field(..., min_length=10, max_length=20)
    patient_email: Optional[str] = None
    billing_address: Dict[str, Any]
    items: List[InvoiceItemCreate] = Field(..., min_items=1)
    delivery_charges: Decimal = Field(default=0, ge=0)
    packaging_charges: Decimal = Field(default=0, ge=0)
    other_charges: Decimal = Field(default=0, ge=0)
    discount_amount: Decimal = Field(default=0, ge=0)
    notes: Optional[str] = None


class InvoiceItemResponse(BaseModel):
    """Invoice item response schema."""
    id: UUID
    medicine_name: str
    strength: str
    manufacturer: str
    batch_number: Optional[str] = None
    hsn_code: Optional[str] = None
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    discount_amount: Decimal
    gst_rate: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    taxable_amount: Decimal
    final_amount: Decimal
    
    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    """Invoice response schema."""
    id: UUID
    invoice_number: str
    order_id: UUID
    pharmacy_id: UUID
    patient_name: str
    patient_phone: str
    patient_email: Optional[str] = None
    billing_address: Dict[str, Any]
    invoice_date: date
    due_date: Optional[date] = None
    status: str
    subtotal: Decimal
    discount_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    delivery_charges: Decimal
    packaging_charges: Decimal
    other_charges: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    amount_due: Decimal
    gstin: Optional[str] = None
    place_of_supply: str
    qr_code_data: Optional[str] = None
    items: List[InvoiceItemResponse] = []
    
    class Config:
        from_attributes = True


class InvoiceNotification(BaseModel):
    """Invoice notification response."""
    invoice_id: UUID
    notification_method: str
    success: bool
    message: str
    sent_at: Optional[str] = None
    delivery_status: Optional[str] = None


class PaymentCreate(BaseModel):
    """Schema for creating payments."""
    invoice_id: UUID
    order_id: UUID
    payment_method: str = Field(..., pattern=r'^(cash|card|upi|net_banking|wallet|insurance)$')
    amount: Decimal = Field(..., gt=0)
    transaction_id: Optional[str] = None
    reference_number: Optional[str] = None
    card_last_four: Optional[str] = Field(None, min_length=4, max_length=4)
    upi_id: Optional[str] = None
    bank_name: Optional[str] = None
    insurance_details: Optional[Dict[str, Any]] = None


class PaymentResponse(BaseModel):
    """Payment response schema."""
    id: UUID
    payment_id: str
    invoice_id: UUID
    order_id: UUID
    payment_method: str
    amount: Decimal
    status: str
    payment_date: str
    transaction_id: Optional[str] = None
    reference_number: Optional[str] = None
    failure_reason: Optional[str] = None
    
    class Config:
        from_attributes = True