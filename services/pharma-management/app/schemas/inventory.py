"""
Inventory management schemas
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from uuid import UUID
from datetime import date
from decimal import Decimal

class InventoryItemCreate(BaseModel):
    """Schema for creating inventory item."""
    medicine_id: UUID
    current_stock: int = Field(0, ge=0)
    minimum_stock: int = Field(10, ge=0)
    maximum_stock: int = Field(1000, ge=0)
    reorder_point: int = Field(20, ge=0)
    cost_price: Decimal = Field(..., gt=0)
    selling_price: Decimal = Field(..., gt=0)
    mrp: Decimal = Field(..., gt=0)
    storage_location: Optional[str] = None


class InventoryTransactionCreate(BaseModel):
    """Schema for creating inventory transaction."""
    inventory_item_id: UUID
    transaction_type: str
    quantity: int
    unit_cost: Optional[Decimal] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class InventoryUpdate(BaseModel):
    """Schema for updating inventory."""
    medicine_id: UUID
    quantity: int = Field(..., gt=0)
    cost_price: Decimal = Field(..., gt=0)
    selling_price: Decimal = Field(..., gt=0)
    mrp: Decimal = Field(..., gt=0)
    batch_number: str = Field(..., min_length=1)
    manufacturing_date: date
    expiry_date: date
    supplier: Optional[str] = None
    
    @validator('expiry_date')
    def validate_expiry_date(cls, v, values):
        if 'manufacturing_date' in values and v <= values['manufacturing_date']:
            raise ValueError('Expiry date must be after manufacturing date')
        return v


class InventoryItemResponse(BaseModel):
    """Inventory item response schema."""
    id: UUID
    pharmacy_id: UUID
    medicine_id: UUID
    medicine_name: str
    current_stock: int
    available_stock: int
    reserved_stock: int
    minimum_stock: int
    reorder_point: int
    cost_price: Decimal
    selling_price: Decimal
    mrp: Decimal
    needs_reorder: bool
    is_overstocked: bool
    storage_location: Optional[str] = None
    
    class Config:
        from_attributes = True


class InventoryAvailability(BaseModel):
    """Medicine availability response."""
    medicine_id: UUID
    medicine_name: str
    total_available: int
    pharmacies: List[dict] = []
    nearest_pharmacy: Optional[dict] = None


class PurchaseOrderCreate(BaseModel):
    """Create purchase order schema."""
    pharmacy_id: UUID
    supplier_id: UUID
    expected_delivery_date: Optional[date] = None
    items: List[dict] = Field(..., min_items=1)
    notes: Optional[str] = None


class PurchaseOrderResponse(BaseModel):
    """Purchase order response schema."""
    id: UUID
    po_number: str
    pharmacy_id: UUID
    supplier_id: UUID
    order_date: date
    status: str
    total_amount: Decimal
    
    class Config:
        from_attributes = True


class GRNCreate(BaseModel):
    """Create GRN schema."""
    purchase_order_id: UUID
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    items: List[dict] = Field(..., min_items=1)
    notes: Optional[str] = None


class GRNResponse(BaseModel):
    """GRN response schema."""
    id: UUID
    grn_number: str
    purchase_order_id: UUID
    receipt_date: date
    status: str
    quality_check_done: bool
    
    class Config:
        from_attributes = True