"""
Medicine schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date
from decimal import Decimal


class MedicineBase(BaseModel):
    """Base medicine schema."""
    name: str = Field(..., min_length=2, max_length=255)
    generic_name: str = Field(..., min_length=2, max_length=255)
    brand_name: Optional[str] = Field(None, max_length=255)
    manufacturer: str = Field(..., max_length=255)
    strength: str = Field(..., max_length=100)
    dosage_form: str = Field(..., max_length=100)
    unit_price: Decimal = Field(..., gt=0)


class MedicineResponse(MedicineBase):
    """Medicine response schema."""
    id: UUID
    ndc_number: Optional[str] = None
    drug_schedule: Optional[str] = None
    active_ingredients: List[str] = []
    route_of_administration: str
    therapeutic_class: Optional[str] = None
    prescription_required: bool
    controlled_substance: bool
    generic_alternatives: Optional[List[str]] = None
    brand_alternatives: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class MedicineAlternatives(BaseModel):
    """Medicine alternatives response."""
    medicine_id: UUID
    medicine_name: str
    generic_alternatives: List[MedicineResponse] = []
    brand_alternatives: List[MedicineResponse] = []
    total_alternatives: int = 0


class MedicineBatchResponse(BaseModel):
    """Medicine batch response schema."""
    id: UUID
    medicine_id: UUID
    batch_number: str
    manufacturing_date: date
    expiry_date: date
    current_quantity: int
    available_quantity: int
    is_expired: bool
    days_to_expiry: int
    
    class Config:
        from_attributes = True