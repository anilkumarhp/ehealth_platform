"""
Prescription models for managing prescriptions and items
"""

from sqlalchemy import Column, String, Text, Integer, Date, Boolean, JSON, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class PrescriptionStatusEnum(enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    VALIDATED = "validated"
    REJECTED = "rejected"
    FULFILLED = "fulfilled"
    EXPIRED = "expired"


class Prescription(BaseModel):
    """Prescription entity with OCR and validation."""
    
    __tablename__ = "prescriptions"
    
    # Basic Information
    prescription_number = Column(String(100), unique=True, nullable=False, index=True)
    patient_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    pharmacy_id = Column(UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=True, index=True)
    
    # Prescription Details
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False, index=True)
    status = Column(String(50), default=PrescriptionStatusEnum.UPLOADED.value, index=True)
    
    # Patient Information
    patient_name = Column(String(255), nullable=False)
    patient_age = Column(Integer, nullable=True)
    patient_gender = Column(String(10), nullable=True)
    patient_weight = Column(Numeric(5, 2), nullable=True)  # kg
    
    # Doctor Information
    doctor_name = Column(String(255), nullable=False)
    doctor_license = Column(String(100), nullable=True)
    clinic_name = Column(String(255), nullable=True)
    
    # File Information
    original_image_path = Column(String(500), nullable=True)
    processed_image_path = Column(String(500), nullable=True)
    s3_bucket = Column(String(100), nullable=True)
    s3_key = Column(String(500), nullable=True)
    
    # OCR Results
    ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(Numeric(5, 2), nullable=True)
    ocr_processed_at = Column(Date, nullable=True)
    
    # Validation
    validation_status = Column(String(50), default="pending")  # pending, approved, rejected
    validation_notes = Column(Text, nullable=True)
    validated_by = Column(UUID(as_uuid=True), nullable=True)
    validated_at = Column(Date, nullable=True)
    
    # Clinical Information
    diagnosis = Column(Text, nullable=True)
    allergies = Column(JSON, nullable=True)  # Patient allergies
    current_medications = Column(JSON, nullable=True)  # Current medications
    
    # Special Instructions
    special_instructions = Column(Text, nullable=True)
    refills_allowed = Column(Integer, default=0)
    refills_remaining = Column(Integer, default=0)
    
    # Compliance
    controlled_substance = Column(Boolean, default=False)
    dea_number_required = Column(Boolean, default=False)
    
    # Relationships
    pharmacy = relationship("Pharmacy", back_populates="prescriptions")
    prescription_items = relationship("PrescriptionItem", back_populates="prescription")
    orders = relationship("Order", back_populates="prescription")
    
    def __repr__(self):
        return f"<Prescription(number='{self.prescription_number}', status='{self.status}')>"


class PrescriptionItem(BaseModel):
    """Individual medicine items in a prescription."""
    
    __tablename__ = "prescription_items"
    
    # References
    prescription_id = Column(UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=False, index=True)
    medicine_id = Column(UUID(as_uuid=True), ForeignKey("medicines.id"), nullable=False, index=True)
    
    # Prescription Details
    medicine_name = Column(String(255), nullable=False)  # As written on prescription
    strength = Column(String(100), nullable=False)
    dosage_form = Column(String(100), nullable=False)
    
    # Quantity and Instructions
    quantity_prescribed = Column(Integer, nullable=False)
    quantity_dispensed = Column(Integer, default=0)
    unit = Column(String(50), nullable=False)  # tablets, ml, etc.
    
    # Dosage Instructions
    dosage_instructions = Column(Text, nullable=False)
    frequency = Column(String(100), nullable=True)  # "twice daily", "as needed"
    duration = Column(String(100), nullable=True)  # "7 days", "until finished"
    
    # Substitution
    generic_substitution_allowed = Column(Boolean, default=True)
    brand_substitution_allowed = Column(Boolean, default=False)
    substituted_medicine_id = Column(UUID(as_uuid=True), ForeignKey("medicines.id"), nullable=True)
    
    # Pricing
    unit_price = Column(Numeric(10, 2), nullable=True)
    total_price = Column(Numeric(10, 2), nullable=True)
    insurance_copay = Column(Numeric(10, 2), nullable=True)
    patient_pay = Column(Numeric(10, 2), nullable=True)
    
    # Status
    dispensed = Column(Boolean, default=False)
    dispensed_at = Column(Date, nullable=True)
    dispensed_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    prescription = relationship("Prescription", back_populates="prescription_items")
    medicine = relationship("Medicine", back_populates="prescription_items", foreign_keys=[medicine_id])
    substituted_medicine = relationship("Medicine", foreign_keys=[substituted_medicine_id])
    
    def __repr__(self):
        return f"<PrescriptionItem(medicine='{self.medicine_name}', qty={self.quantity_prescribed})>"