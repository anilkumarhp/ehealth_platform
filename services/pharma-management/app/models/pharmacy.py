"""
Pharmacy model for managing pharmacy information
"""

from sqlalchemy import Column, String, Text, Boolean, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Pharmacy(BaseModel):
    """Pharmacy entity with registration and operational details."""
    
    __tablename__ = "pharmacies"
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    license_number = Column(String(100), unique=True, nullable=False, index=True)
    registration_number = Column(String(100), unique=True, nullable=False)
    
    # Contact Information
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    website = Column(String(255), nullable=True)
    
    # Address
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False, default="USA")
    
    # Geolocation for delivery radius calculation
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Operational Details
    operating_hours = Column(JSON, nullable=True)  # Store as JSON
    delivery_radius_km = Column(Float, default=10.0)
    home_delivery_available = Column(Boolean, default=True)
    
    # Compliance & Certifications
    dea_number = Column(String(50), nullable=True)  # For controlled substances
    state_license_expiry = Column(String(10), nullable=True)  # YYYY-MM-DD
    certifications = Column(JSON, nullable=True)  # Array of certifications
    
    # Business Information
    owner_name = Column(String(255), nullable=False)
    pharmacist_in_charge = Column(String(255), nullable=False)
    tax_id = Column(String(50), nullable=True)
    
    # Settings
    auto_refill_enabled = Column(Boolean, default=True)
    generic_substitution_allowed = Column(Boolean, default=True)
    insurance_accepted = Column(JSON, nullable=True)  # List of accepted insurance
    
    # Status
    verification_status = Column(String(50), default="pending")  # pending, verified, suspended
    operational_status = Column(String(50), default="active")  # active, inactive, maintenance
    
    # Relationships
    staff_members = relationship("PharmacyStaff", back_populates="pharmacy")
    inventory_items = relationship("InventoryItem", back_populates="pharmacy")
    orders = relationship("Order", back_populates="pharmacy")
    prescriptions = relationship("Prescription", back_populates="pharmacy")
    audit_logs = relationship("AuditLog", back_populates="pharmacy")
    
    def __repr__(self):
        return f"<Pharmacy(name='{self.name}', license='{self.license_number}')>"