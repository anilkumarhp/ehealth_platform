"""
Purchase and supplier management models
"""

from sqlalchemy import Column, String, Text, Numeric, Integer, Date, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class PurchaseOrderStatusEnum(enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    SENT = "sent"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class GRNStatusEnum(enum.Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    COMPLETE = "complete"
    DISCREPANCY = "discrepancy"


class Supplier(BaseModel):
    """Supplier/Vendor information."""
    
    __tablename__ = "suppliers"
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    website = Column(String(255), nullable=True)
    
    # Address
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False, default="India")
    
    # Business Information
    gst_number = Column(String(50), nullable=True, index=True)
    pan_number = Column(String(20), nullable=True)
    drug_license = Column(String(100), nullable=True)
    
    # Contact Person
    contact_person_name = Column(String(255), nullable=True)
    contact_person_phone = Column(String(20), nullable=True)
    contact_person_email = Column(String(255), nullable=True)
    
    # Terms
    payment_terms = Column(String(100), nullable=True)  # "30 days", "COD", etc.
    credit_limit = Column(Numeric(15, 2), nullable=True)
    discount_percentage = Column(Numeric(5, 2), nullable=True)
    
    # Status
    status = Column(String(50), default="active")  # active, inactive, blacklisted
    rating = Column(Numeric(3, 2), nullable=True)  # 1.00 to 5.00
    
    # Relationships
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    
    def __repr__(self):
        return f"<Supplier(name='{self.name}', code='{self.code}')>"


class PurchaseOrder(BaseModel):
    """Purchase orders to suppliers."""
    
    __tablename__ = "purchase_orders"
    
    # Basic Information
    po_number = Column(String(100), unique=True, nullable=False, index=True)
    pharmacy_id = Column(UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=False, index=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False, index=True)
    
    # Order Details
    order_date = Column(Date, nullable=False)
    expected_delivery_date = Column(Date, nullable=True)
    status = Column(String(50), default=PurchaseOrderStatusEnum.DRAFT.value, index=True)
    
    # Financial
    subtotal = Column(Numeric(15, 2), nullable=False, default=0.00)
    tax_amount = Column(Numeric(15, 2), nullable=False, default=0.00)
    discount_amount = Column(Numeric(15, 2), nullable=False, default=0.00)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0.00)
    
    # Terms
    payment_terms = Column(String(100), nullable=True)
    delivery_terms = Column(String(100), nullable=True)
    
    # Approval
    requested_by = Column(UUID(as_uuid=True), nullable=False)
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    terms_conditions = Column(Text, nullable=True)
    
    # Relationships
    pharmacy = relationship("Pharmacy")
    supplier = relationship("Supplier", back_populates="purchase_orders")
    po_items = relationship("PurchaseOrderItem", back_populates="purchase_order")
    grns = relationship("GoodsReceiptNote", back_populates="purchase_order")
    
    def __repr__(self):
        return f"<PurchaseOrder(po_number='{self.po_number}', status='{self.status}')>"


class PurchaseOrderItem(BaseModel):
    """Items in a purchase order."""
    
    __tablename__ = "purchase_order_items"
    
    # References
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False, index=True)
    medicine_id = Column(UUID(as_uuid=True), ForeignKey("medicines.id"), nullable=False, index=True)
    
    # Item Details
    medicine_name = Column(String(255), nullable=False)
    strength = Column(String(100), nullable=False)
    manufacturer = Column(String(255), nullable=False)
    
    # Quantity & Pricing
    quantity_ordered = Column(Integer, nullable=False)
    unit = Column(String(50), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(15, 2), nullable=False)
    
    # Discount
    discount_percentage = Column(Numeric(5, 2), default=0.00)
    discount_amount = Column(Numeric(10, 2), default=0.00)
    
    # Tax
    tax_percentage = Column(Numeric(5, 2), default=0.00)
    tax_amount = Column(Numeric(10, 2), default=0.00)
    
    # Delivery
    quantity_received = Column(Integer, default=0)
    quantity_pending = Column(Integer, nullable=False)
    
    # Specifications
    specifications = Column(Text, nullable=True)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="po_items")
    medicine = relationship("Medicine")
    
    def __repr__(self):
        return f"<PurchaseOrderItem(medicine='{self.medicine_name}', qty={self.quantity_ordered})>"


class GoodsReceiptNote(BaseModel):
    """Goods Receipt Note for tracking deliveries."""
    
    __tablename__ = "goods_receipt_notes"
    
    # Basic Information
    grn_number = Column(String(100), unique=True, nullable=False, index=True)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False, index=True)
    pharmacy_id = Column(UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=False, index=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False, index=True)
    
    # Receipt Details
    receipt_date = Column(Date, nullable=False)
    invoice_number = Column(String(100), nullable=True)
    invoice_date = Column(Date, nullable=True)
    invoice_amount = Column(Numeric(15, 2), nullable=True)
    
    # Delivery Information
    delivery_challan_number = Column(String(100), nullable=True)
    vehicle_number = Column(String(50), nullable=True)
    driver_name = Column(String(255), nullable=True)
    driver_phone = Column(String(20), nullable=True)
    
    # Status
    status = Column(String(50), default=GRNStatusEnum.PENDING.value, index=True)
    
    # Quality Check
    quality_check_done = Column(Boolean, default=False)
    quality_check_by = Column(UUID(as_uuid=True), nullable=True)
    quality_check_date = Column(Date, nullable=True)
    quality_issues = Column(Text, nullable=True)
    
    # Received By
    received_by = Column(UUID(as_uuid=True), nullable=False)
    verified_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    discrepancy_notes = Column(Text, nullable=True)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="grns")
    pharmacy = relationship("Pharmacy")
    supplier = relationship("Supplier")
    grn_items = relationship("GoodsReceiptNoteItem", back_populates="grn")
    
    def __repr__(self):
        return f"<GoodsReceiptNote(grn_number='{self.grn_number}', status='{self.status}')>"


class GoodsReceiptNoteItem(BaseModel):
    """Items received in a GRN."""
    
    __tablename__ = "goods_receipt_note_items"
    
    # References
    grn_id = Column(UUID(as_uuid=True), ForeignKey("goods_receipt_notes.id"), nullable=False, index=True)
    po_item_id = Column(UUID(as_uuid=True), ForeignKey("purchase_order_items.id"), nullable=False, index=True)
    medicine_id = Column(UUID(as_uuid=True), ForeignKey("medicines.id"), nullable=False, index=True)
    
    # Item Details
    medicine_name = Column(String(255), nullable=False)
    batch_number = Column(String(100), nullable=False)
    manufacturing_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    
    # Quantities
    quantity_ordered = Column(Integer, nullable=False)
    quantity_received = Column(Integer, nullable=False)
    quantity_accepted = Column(Integer, nullable=False)
    quantity_rejected = Column(Integer, default=0)
    
    # Pricing
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_value = Column(Numeric(15, 2), nullable=False)
    
    # Quality
    quality_status = Column(String(50), default="pending")  # pending, passed, failed
    rejection_reason = Column(Text, nullable=True)
    
    # Storage
    storage_location = Column(String(100), nullable=True)
    
    # Relationships
    grn = relationship("GoodsReceiptNote", back_populates="grn_items")
    po_item = relationship("PurchaseOrderItem")
    medicine = relationship("Medicine")
    
    def __repr__(self):
        return f"<GoodsReceiptNoteItem(medicine='{self.medicine_name}', batch='{self.batch_number}')>"