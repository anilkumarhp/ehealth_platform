"""
Prescription management schemas
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal


class PrescriptionItemCreate(BaseModel):
    """Schema for creating prescription items."""
    medicine_id: UUID
    medicine_name: str = Field(..., min_length=2, max_length=255)
    strength: str = Field(..., max_length=100)
    dosage_form: str = Field(..., max_length=100)
    quantity_prescribed: int = Field(..., gt=0)
    unit: str = Field(..., max_length=50)
    dosage_instructions: str = Field(..., min_length=5)
    frequency: Optional[str] = Field(None, max_length=100)
    duration: Optional[str] = Field(None, max_length=100)
    generic_substitution_allowed: bool = True


class PrescriptionCreate(BaseModel):
    """Schema for creating prescriptions."""
    prescription_number: Optional[str] = None  # Add prescription_number field
    patient_id: UUID
    doctor_id: UUID
    pharmacy_id: Optional[UUID] = None
    patient_name: str = Field(..., min_length=2, max_length=255)
    patient_age: Optional[int] = Field(None, ge=0, le=150)
    patient_gender: Optional[str] = Field(None, pattern=r'^(male|female|other)$')
    patient_weight: Optional[Decimal] = Field(None, gt=0)
    doctor_name: str = Field(..., min_length=2, max_length=255)
    doctor_license: Optional[str] = Field(None, max_length=100)
    clinic_name: Optional[str] = Field(None, max_length=255)
    issue_date: date
    expiry_date: date
    diagnosis: Optional[str] = None
    allergies: Optional[List[str]] = None
    current_medications: Optional[List[Dict[str, Any]]] = None
    special_instructions: Optional[str] = None
    refills_allowed: int = Field(default=0, ge=0, le=12)
    items: Optional[List[PrescriptionItemCreate]] = Field(default=[])
    
    @validator('expiry_date')
    def validate_expiry_date(cls, v, values):
        if 'issue_date' in values and v <= values['issue_date']:
            raise ValueError('Expiry date must be after issue date')
        return v


class PrescriptionItemResponse(BaseModel):
    """Prescription item response schema."""
    id: UUID
    medicine_name: str
    strength: str
    dosage_form: str
    quantity_prescribed: int
    quantity_dispensed: int
    unit: str
    dosage_instructions: str
    frequency: Optional[str] = None
    duration: Optional[str] = None
    generic_substitution_allowed: bool
    dispensed: bool
    dispensed_at: Optional[date] = None
    
    class Config:
        from_attributes = True


class PrescriptionResponse(BaseModel):
    """Prescription response schema."""
    id: UUID
    prescription_number: str
    patient_id: UUID
    doctor_id: UUID
    pharmacy_id: Optional[UUID] = None
    patient_name: str
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    patient_weight: Optional[Decimal] = None
    doctor_name: str
    doctor_license: Optional[str] = None
    clinic_name: Optional[str] = None
    issue_date: date
    expiry_date: date
    status: str
    diagnosis: Optional[str] = None
    allergies: Optional[List[str]] = None
    current_medications: Optional[List[Dict[str, Any]]] = None
    special_instructions: Optional[str] = None
    refills_allowed: int
    refills_remaining: int
    controlled_substance: bool
    validation_status: str
    validation_notes: Optional[str] = None
    validated_at: Optional[date] = None
    ocr_text: Optional[str] = None
    ocr_confidence: Optional[Decimal] = None
    items: List[PrescriptionItemResponse] = []
    
    class Config:
        from_attributes = True


class PrescriptionValidation(BaseModel):
    """Prescription validation response."""
    prescription_id: UUID
    validation_status: str
    validated_by: UUID
    validated_at: datetime
    validation_notes: Optional[str] = None
    issues_found: List[str] = []
    recommendations: List[str] = []
    approved: bool