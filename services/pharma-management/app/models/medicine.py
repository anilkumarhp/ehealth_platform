"""
Medicine and batch tracking models
"""

from sqlalchemy import Column, String, Text, Numeric, Integer, Date, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Medicine(BaseModel):
    """Medicine master data with regulatory information."""
    
    __tablename__ = "medicines"
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    generic_name = Column(String(255), nullable=False, index=True)
    brand_name = Column(String(255), nullable=True, index=True)
    manufacturer = Column(String(255), nullable=False, index=True)
    
    # Regulatory Information
    ndc_number = Column(String(50), unique=True, nullable=True, index=True)  # National Drug Code
    fda_approval_number = Column(String(100), nullable=True)
    drug_schedule = Column(String(10), nullable=True)  # DEA Schedule (I-V)
    
    # Clinical Information
    active_ingredients = Column(JSON, nullable=False)  # List of active ingredients
    strength = Column(String(100), nullable=False)  # e.g., "500mg", "10mg/ml"
    dosage_form = Column(String(100), nullable=False)  # tablet, capsule, liquid, etc.
    route_of_administration = Column(String(100), nullable=False)  # oral, topical, injection
    
    # Classification
    therapeutic_class = Column(String(255), nullable=True)
    pharmacological_class = Column(String(255), nullable=True)
    atc_code = Column(String(20), nullable=True)  # Anatomical Therapeutic Chemical code
    
    # Prescription Requirements
    prescription_required = Column(Boolean, default=True, nullable=False)
    controlled_substance = Column(Boolean, default=False, nullable=False)
    
    # Storage Requirements
    storage_temperature_min = Column(Numeric(5, 2), nullable=True)  # Celsius
    storage_temperature_max = Column(Numeric(5, 2), nullable=True)  # Celsius
    storage_conditions = Column(Text, nullable=True)  # Special storage instructions
    
    # Pricing
    unit_price = Column(Numeric(10, 2), nullable=False)
    insurance_copay = Column(Numeric(10, 2), nullable=True)
    
    # Alternatives and Interactions
    generic_alternatives = Column(JSON, nullable=True)  # List of generic alternatives
    brand_alternatives = Column(JSON, nullable=True)  # List of brand alternatives
    contraindications = Column(JSON, nullable=True)  # List of contraindications
    drug_interactions = Column(JSON, nullable=True)  # Known drug interactions
    
    # Metadata
    description = Column(Text, nullable=True)
    side_effects = Column(JSON, nullable=True)  # Common side effects
    warnings = Column(JSON, nullable=True)  # FDA warnings and precautions
    
    # Relationships
    batches = relationship("MedicineBatch", back_populates="medicine")
    inventory_items = relationship("InventoryItem", back_populates="medicine")
    prescription_items = relationship("PrescriptionItem", back_populates="medicine", foreign_keys="PrescriptionItem.medicine_id")
    
    def __repr__(self):
        return f"<Medicine(name='{self.name}', ndc='{self.ndc_number}')>"


class MedicineBatch(BaseModel):
    """Batch/Lot tracking for medicines with expiry and recall management."""
    
    __tablename__ = "medicine_batches"
    
    # Batch Information
    medicine_id = Column(UUID(as_uuid=True), ForeignKey("medicines.id"), nullable=False, index=True)
    batch_number = Column(String(100), nullable=False, index=True)
    lot_number = Column(String(100), nullable=True)
    
    # Manufacturing Details
    manufacturing_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False, index=True)
    manufacturer_batch_id = Column(String(100), nullable=True)
    
    # Quantities
    manufactured_quantity = Column(Integer, nullable=False)
    received_quantity = Column(Integer, nullable=False)
    current_quantity = Column(Integer, nullable=False, default=0)
    reserved_quantity = Column(Integer, nullable=False, default=0)
    
    # Quality Control
    quality_test_passed = Column(Boolean, default=False)
    quality_test_date = Column(Date, nullable=True)
    quality_certificate_number = Column(String(100), nullable=True)
    
    # Recall Information
    recall_status = Column(String(50), default="none")  # none, voluntary, mandatory
    recall_date = Column(Date, nullable=True)
    recall_reason = Column(Text, nullable=True)
    
    # Storage Tracking
    storage_location = Column(String(255), nullable=True)
    temperature_log = Column(JSON, nullable=True)  # Temperature monitoring data
    
    # Relationships
    medicine = relationship("Medicine", back_populates="batches")
    inventory_transactions = relationship("InventoryTransaction", back_populates="batch")
    
    def __repr__(self):
        return f"<MedicineBatch(batch='{self.batch_number}', expiry='{self.expiry_date}')>"
    
    @property
    def is_expired(self) -> bool:
        """Check if the batch has expired."""
        from datetime import date
        return self.expiry_date < date.today()
    
    @property
    def available_quantity(self) -> int:
        """Calculate available quantity (current - reserved)."""
        return max(0, self.current_quantity - self.reserved_quantity)
    
    @property
    def days_to_expiry(self) -> int:
        """Calculate days until expiry."""
        from datetime import date
        return (self.expiry_date - date.today()).days