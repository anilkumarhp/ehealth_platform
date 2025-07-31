"""
Billing and invoice models
"""

from sqlalchemy import Column, String, Text, Numeric, Integer, Date, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class InvoiceStatusEnum(enum.Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    SENT = "sent"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentStatusEnum(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentMethodEnum(enum.Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    NET_BANKING = "net_banking"
    WALLET = "wallet"
    INSURANCE = "insurance"
    CREDIT = "credit"


class Invoice(BaseModel):
    """GST-compliant invoices for orders."""
    
    __tablename__ = "invoices"
    
    # Basic Information
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True)
    pharmacy_id = Column(UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=False, index=True)
    
    # Customer Information
    patient_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    patient_name = Column(String(255), nullable=False)
    patient_phone = Column(String(20), nullable=False)
    patient_email = Column(String(255), nullable=True)
    
    # Billing Address
    billing_address = Column(JSON, nullable=False)  # Complete address object
    
    # Invoice Details
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(String(50), default=InvoiceStatusEnum.DRAFT.value, index=True)
    
    # Financial Details
    subtotal = Column(Numeric(15, 2), nullable=False, default=0.00)
    discount_amount = Column(Numeric(15, 2), nullable=False, default=0.00)
    
    # GST Details
    cgst_rate = Column(Numeric(5, 2), nullable=False, default=0.00)
    cgst_amount = Column(Numeric(15, 2), nullable=False, default=0.00)
    sgst_rate = Column(Numeric(5, 2), nullable=False, default=0.00)
    sgst_amount = Column(Numeric(15, 2), nullable=False, default=0.00)
    igst_rate = Column(Numeric(5, 2), nullable=False, default=0.00)
    igst_amount = Column(Numeric(15, 2), nullable=False, default=0.00)
    
    # Other Charges
    delivery_charges = Column(Numeric(10, 2), nullable=False, default=0.00)
    packaging_charges = Column(Numeric(10, 2), nullable=False, default=0.00)
    other_charges = Column(Numeric(10, 2), nullable=False, default=0.00)
    
    # Total
    total_amount = Column(Numeric(15, 2), nullable=False, default=0.00)
    amount_paid = Column(Numeric(15, 2), nullable=False, default=0.00)
    amount_due = Column(Numeric(15, 2), nullable=False, default=0.00)
    
    # Insurance
    insurance_provider = Column(String(255), nullable=True)
    insurance_claim_number = Column(String(100), nullable=True)
    insurance_amount = Column(Numeric(15, 2), nullable=True)
    copay_amount = Column(Numeric(15, 2), nullable=True)
    
    # Compliance
    gstin = Column(String(50), nullable=True)  # Pharmacy GSTIN
    place_of_supply = Column(String(100), nullable=False)
    reverse_charge = Column(Boolean, default=False)
    
    # Digital Signature
    digital_signature = Column(Text, nullable=True)
    qr_code_data = Column(Text, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    terms_conditions = Column(Text, nullable=True)
    
    # Notification
    notification_sent = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime, nullable=True)
    notification_method = Column(String(50), nullable=True)  # email, whatsapp, sms
    
    # Relationships
    order = relationship("Order", back_populates="invoice")
    pharmacy = relationship("Pharmacy")
    invoice_items = relationship("InvoiceItem", back_populates="invoice")
    payments = relationship("Payment", back_populates="invoice")
    
    def __repr__(self):
        return f"<Invoice(number='{self.invoice_number}', status='{self.status}')>"


class InvoiceItem(BaseModel):
    """Individual items in an invoice."""
    
    __tablename__ = "invoice_items"
    
    # References
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, index=True)
    order_item_id = Column(UUID(as_uuid=True), ForeignKey("order_items.id"), nullable=False, index=True)
    medicine_id = Column(UUID(as_uuid=True), ForeignKey("medicines.id"), nullable=False, index=True)
    
    # Item Details
    medicine_name = Column(String(255), nullable=False)
    strength = Column(String(100), nullable=False)
    manufacturer = Column(String(255), nullable=False)
    batch_number = Column(String(100), nullable=True)
    expiry_date = Column(Date, nullable=True)
    
    # HSN/SAC Code for GST
    hsn_code = Column(String(20), nullable=True)
    
    # Quantity & Pricing
    quantity = Column(Integer, nullable=False)
    unit = Column(String(50), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(15, 2), nullable=False)
    
    # Discount
    discount_percentage = Column(Numeric(5, 2), default=0.00)
    discount_amount = Column(Numeric(10, 2), default=0.00)
    
    # GST
    gst_rate = Column(Numeric(5, 2), nullable=False, default=0.00)
    cgst_amount = Column(Numeric(10, 2), default=0.00)
    sgst_amount = Column(Numeric(10, 2), default=0.00)
    igst_amount = Column(Numeric(10, 2), default=0.00)
    
    # Final Amount
    taxable_amount = Column(Numeric(15, 2), nullable=False)
    final_amount = Column(Numeric(15, 2), nullable=False)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="invoice_items")
    order_item = relationship("OrderItem")
    medicine = relationship("Medicine")
    
    def __repr__(self):
        return f"<InvoiceItem(medicine='{self.medicine_name}', qty={self.quantity})>"


class Payment(BaseModel):
    """Payment records for invoices."""
    
    __tablename__ = "payments"
    
    # Basic Information
    payment_id = Column(String(100), unique=True, nullable=False, index=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True)
    
    # Payment Details
    payment_date = Column(DateTime, nullable=False)
    payment_method = Column(String(50), nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    status = Column(String(50), default=PaymentStatusEnum.PENDING.value, index=True)
    
    # Transaction Details
    transaction_id = Column(String(255), nullable=True, index=True)
    reference_number = Column(String(255), nullable=True)
    gateway_response = Column(JSON, nullable=True)
    
    # Card/UPI Details (if applicable)
    card_last_four = Column(String(4), nullable=True)
    card_type = Column(String(50), nullable=True)  # visa, mastercard, rupay
    upi_id = Column(String(255), nullable=True)
    
    # Bank Details (if applicable)
    bank_name = Column(String(255), nullable=True)
    bank_reference = Column(String(255), nullable=True)
    
    # Insurance Details (if applicable)
    insurance_provider = Column(String(255), nullable=True)
    insurance_policy_number = Column(String(100), nullable=True)
    insurance_claim_id = Column(String(100), nullable=True)
    copay_amount = Column(Numeric(10, 2), nullable=True)
    
    # Failure Details
    failure_reason = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Refund Details
    refund_amount = Column(Numeric(15, 2), default=0.00)
    refund_date = Column(DateTime, nullable=True)
    refund_reference = Column(String(255), nullable=True)
    refund_reason = Column(Text, nullable=True)
    
    # Reconciliation
    reconciled = Column(Boolean, default=False)
    reconciled_at = Column(DateTime, nullable=True)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
    order = relationship("Order")
    
    def __repr__(self):
        return f"<Payment(id='{self.payment_id}', amount={self.amount}, status='{self.status}')>"