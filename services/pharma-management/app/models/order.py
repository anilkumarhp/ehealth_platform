"""
Order models for managing prescription orders
"""

from sqlalchemy import Column, String, Text, Integer, Numeric, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class OrderStatusEnum(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    READY = "ready"
    DISPATCHED = "dispatched"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class DeliveryTypeEnum(enum.Enum):
    PICKUP = "pickup"
    HOME_DELIVERY = "home_delivery"
    HOSPITAL_DELIVERY = "hospital_delivery"


class Order(BaseModel):
    """Order entity for prescription fulfillment."""
    
    __tablename__ = "orders"
    
    # Basic Information
    order_number = Column(String(100), unique=True, nullable=False, index=True)
    prescription_id = Column(UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=False, index=True)
    pharmacy_id = Column(UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=False, index=True)
    
    # Customer Information
    patient_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    patient_name = Column(String(255), nullable=False)
    patient_phone = Column(String(20), nullable=False)
    patient_email = Column(String(255), nullable=True)
    
    # Order Details
    status = Column(String(50), default=OrderStatusEnum.PENDING.value, index=True)
    order_date = Column(DateTime, nullable=False)
    expected_ready_time = Column(DateTime, nullable=True)
    actual_ready_time = Column(DateTime, nullable=True)
    
    # Delivery Information
    delivery_type = Column(String(50), default=DeliveryTypeEnum.PICKUP.value)
    delivery_address = Column(JSON, nullable=True)  # Address object
    delivery_instructions = Column(Text, nullable=True)
    delivery_fee = Column(Numeric(10, 2), default=0.00)
    
    # Pricing
    subtotal = Column(Numeric(10, 2), nullable=False, default=0.00)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    
    # Insurance
    insurance_provider = Column(String(255), nullable=True)
    insurance_copay = Column(Numeric(10, 2), nullable=True)
    insurance_claim_number = Column(String(100), nullable=True)
    
    # Payment
    payment_status = Column(String(50), default="pending")  # pending, paid, failed
    payment_method = Column(String(50), nullable=True)  # cash, card, insurance
    payment_reference = Column(String(255), nullable=True)
    
    # Fulfillment
    pharmacist_id = Column(UUID(as_uuid=True), nullable=True)
    pharmacist_notes = Column(Text, nullable=True)
    quality_check_passed = Column(Boolean, default=False)
    
    # Tracking
    tracking_number = Column(String(100), nullable=True)
    delivery_partner = Column(String(100), nullable=True)
    estimated_delivery_time = Column(DateTime, nullable=True)
    actual_delivery_time = Column(DateTime, nullable=True)
    
    # Special Flags
    urgent = Column(Boolean, default=False)
    controlled_substance = Column(Boolean, default=False)
    requires_id_verification = Column(Boolean, default=False)
    
    # Relationships
    prescription = relationship("Prescription", back_populates="orders")
    pharmacy = relationship("Pharmacy", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")
    invoice = relationship("Invoice", back_populates="order", uselist=False)
    
    def __repr__(self):
        return f"<Order(number='{self.order_number}', status='{self.status}')>"


class OrderItem(BaseModel):
    """Individual items in an order."""
    
    __tablename__ = "order_items"
    
    # References
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True)
    medicine_id = Column(UUID(as_uuid=True), ForeignKey("medicines.id"), nullable=False, index=True)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("medicine_batches.id"), nullable=True, index=True)
    
    # Item Details
    medicine_name = Column(String(255), nullable=False)
    strength = Column(String(100), nullable=False)
    dosage_form = Column(String(100), nullable=False)
    manufacturer = Column(String(255), nullable=False)
    
    # Quantity
    quantity_ordered = Column(Integer, nullable=False)
    quantity_dispensed = Column(Integer, default=0)
    unit = Column(String(50), nullable=False)
    
    # Pricing
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    discount_applied = Column(Numeric(10, 2), default=0.00)
    
    # Batch Information
    batch_number = Column(String(100), nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    
    # Substitution
    is_substituted = Column(Boolean, default=False)
    original_medicine_id = Column(UUID(as_uuid=True), nullable=True)
    substitution_reason = Column(String(255), nullable=True)
    
    # Status
    status = Column(String(50), default="pending")  # pending, dispensed, cancelled
    dispensed_by = Column(UUID(as_uuid=True), nullable=True)
    dispensed_at = Column(DateTime, nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    medicine = relationship("Medicine")
    batch = relationship("MedicineBatch")
    
    def __repr__(self):
        return f"<OrderItem(medicine='{self.medicine_name}', qty={self.quantity_ordered})>"