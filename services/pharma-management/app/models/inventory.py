"""
Inventory management models
"""

from sqlalchemy import Column, String, Integer, Numeric, DateTime, Boolean, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class TransactionTypeEnum(enum.Enum):
    PURCHASE = "purchase"
    SALE = "sale"
    RETURN = "return"
    ADJUSTMENT = "adjustment"
    TRANSFER = "transfer"
    EXPIRED = "expired"
    DAMAGED = "damaged"


class InventoryItem(BaseModel):
    """Inventory tracking for medicines at pharmacy level."""
    
    __tablename__ = "inventory_items"
    
    # References
    pharmacy_id = Column(UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=False, index=True)
    medicine_id = Column(UUID(as_uuid=True), ForeignKey("medicines.id"), nullable=False, index=True)
    
    # Stock Information
    current_stock = Column(Integer, nullable=False, default=0)
    reserved_stock = Column(Integer, nullable=False, default=0)  # Reserved for orders
    minimum_stock = Column(Integer, nullable=False, default=10)
    maximum_stock = Column(Integer, nullable=False, default=1000)
    reorder_point = Column(Integer, nullable=False, default=20)
    
    # Pricing
    cost_price = Column(Numeric(10, 2), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)
    mrp = Column(Numeric(10, 2), nullable=False)  # Maximum Retail Price
    
    # Storage Information
    storage_location = Column(String(100), nullable=True)  # Shelf/Rack location
    storage_temperature = Column(Numeric(5, 2), nullable=True)  # Current temperature
    requires_refrigeration = Column(Boolean, default=False)
    
    # Supplier Information
    primary_supplier = Column(String(255), nullable=True)
    supplier_contact = Column(String(255), nullable=True)
    last_purchase_date = Column(DateTime, nullable=True)
    last_purchase_price = Column(Numeric(10, 2), nullable=True)
    
    # Auto-reorder Settings
    auto_reorder_enabled = Column(Boolean, default=True)
    preferred_order_quantity = Column(Integer, nullable=True)
    
    # Status
    status = Column(String(50), default="active")  # active, discontinued, recalled
    
    # Relationships
    pharmacy = relationship("Pharmacy", back_populates="inventory_items")
    medicine = relationship("Medicine", back_populates="inventory_items")
    transactions = relationship("InventoryTransaction", back_populates="inventory_item")
    
    @property
    def available_stock(self) -> int:
        """Calculate available stock (current - reserved)."""
        return max(0, self.current_stock - self.reserved_stock)
    
    @property
    def needs_reorder(self) -> bool:
        """Check if item needs reordering."""
        return self.current_stock <= self.reorder_point
    
    @property
    def is_overstocked(self) -> bool:
        """Check if item is overstocked."""
        return self.current_stock > self.maximum_stock
    
    def __repr__(self):
        return f"<InventoryItem(medicine='{self.medicine_id}', stock={self.current_stock})>"


class InventoryTransaction(BaseModel):
    """Track all inventory movements."""
    
    __tablename__ = "inventory_transactions"
    
    # References
    inventory_item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False, index=True)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("medicine_batches.id"), nullable=True, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True, index=True)
    
    # Transaction Details
    transaction_type = Column(String(50), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)  # Positive for inbound, negative for outbound
    unit_cost = Column(Numeric(10, 2), nullable=True)
    total_cost = Column(Numeric(10, 2), nullable=True)
    
    # Before/After Stock Levels
    stock_before = Column(Integer, nullable=False)
    stock_after = Column(Integer, nullable=False)
    
    # Transaction Context
    reference_number = Column(String(100), nullable=True)  # PO number, invoice number, etc.
    supplier = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Approval
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Relationships
    inventory_item = relationship("InventoryItem", back_populates="transactions")
    batch = relationship("MedicineBatch", back_populates="inventory_transactions")
    order = relationship("Order")
    
    def __repr__(self):
        return f"<InventoryTransaction(type='{self.transaction_type}', qty={self.quantity})>"