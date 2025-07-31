"""
Staff management models
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, JSON, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class StaffRoleEnum(enum.Enum):
    PHARMACIST = "pharmacist"
    PHARMACY_TECHNICIAN = "pharmacy_technician"
    STORE_MANAGER = "store_manager"
    CASHIER = "cashier"
    DELIVERY_PERSON = "delivery_person"
    ADMIN = "admin"


class PharmacyStaff(BaseModel):
    """Staff members working at pharmacies."""
    
    __tablename__ = "pharmacy_staff"
    
    # References
    pharmacy_id = Column(UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # From user management service
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    
    # Professional Information
    role = Column(String(50), nullable=False, index=True)
    license_number = Column(String(100), nullable=True, index=True)  # For pharmacists
    license_expiry = Column(Date, nullable=True)
    certifications = Column(JSON, nullable=True)  # List of certifications
    
    # Employment Details
    hire_date = Column(Date, nullable=False)
    employment_status = Column(String(50), default="active")  # active, inactive, terminated
    
    # Permissions
    can_validate_prescriptions = Column(Boolean, default=False)
    can_dispense_controlled_substances = Column(Boolean, default=False)
    can_manage_inventory = Column(Boolean, default=False)
    can_process_payments = Column(Boolean, default=False)
    
    # Relationships
    pharmacy = relationship("Pharmacy", back_populates="staff_members")
    
    def __repr__(self):
        return f"<PharmacyStaff(name='{self.first_name} {self.last_name}', role='{self.role}')>"