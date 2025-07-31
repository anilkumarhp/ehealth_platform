"""
Order management schemas
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal


class OrderItemCreate(BaseModel):
    """Schema for creating order items."""
    medicine_id: UUID
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)
    notes: Optional[str] = None


class OrderCreate(BaseModel):
    """Schema for creating orders."""
    prescription_id: UUID
    pharmacy_id: UUID
    patient_id: UUID
    patient_name: str = Field(..., min_length=2, max_length=255)
    patient_phone: str = Field(..., min_length=10, max_length=20)
    patient_email: Optional[str] = None
    delivery_type: str = Field(default="pickup", pattern=r'^(pickup|home_delivery|hospital_delivery)$')
    delivery_address: Optional[Dict[str, Any]] = None
    delivery_instructions: Optional[str] = None
    items: List[OrderItemCreate] = Field(..., min_items=1)
    urgent: bool = False
    notes: Optional[str] = None


class OrderItemResponse(BaseModel):
    """Order item response schema."""
    id: UUID
    medicine_id: UUID
    medicine_name: str
    strength: str
    manufacturer: str
    quantity_ordered: int
    quantity_dispensed: int
    unit_price: Decimal
    total_price: Decimal
    batch_number: Optional[str] = None
    expiry_date: Optional[datetime] = None
    status: str
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Order response schema."""
    id: UUID
    order_number: str
    prescription_id: UUID
    pharmacy_id: UUID
    patient_id: UUID
    patient_name: str
    patient_phone: str
    patient_email: Optional[str] = None
    status: str
    order_date: datetime
    expected_ready_time: Optional[datetime] = None
    actual_ready_time: Optional[datetime] = None
    delivery_type: str
    delivery_address: Optional[Dict[str, Any]] = None
    delivery_instructions: Optional[str] = None
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    delivery_fee: Decimal
    total_amount: Decimal
    payment_status: str
    urgent: bool
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True


class OrderList(BaseModel):
    """Simplified order list schema."""
    id: UUID
    order_number: str
    patient_name: str
    status: str
    order_date: datetime
    total_amount: Decimal
    delivery_type: str
    urgent: bool
    
    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    status: str = Field(..., pattern=r'^(pending|confirmed|processing|ready|dispatched|delivered|cancelled)$')
    notes: Optional[str] = None
    updated_by: UUID
    
    @validator('status')
    def validate_status_transition(cls, v):
        # Add business logic for valid status transitions
        valid_statuses = [
            "pending", "confirmed", "processing", "ready", 
            "dispatched", "delivered", "cancelled"
        ]
        if v not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        return v