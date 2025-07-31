import uuid
from sqlalchemy import (Boolean, Column, String, DateTime, ForeignKey, func)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..base import Base

class PatientInsurance(Base):
    __tablename__ = 'patient_insurances'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Basic insurance information
    provider_name = Column(String(100), nullable=True)
    policy_number = Column(String(100), nullable=False, index=True)
    scheme_name = Column(String(200), nullable=True)
    insurance_category = Column(String(50), nullable=True)  # 'private' or 'government'
    
    # Additional insurance details
    group_number = Column(String(100), nullable=True)
    plan_type = Column(String(100), nullable=True)
    effective_date = Column(String(20), nullable=True)
    expiration_date = Column(String(20), nullable=True)
    copay_amount = Column(String(50), nullable=True)
    deductible_amount = Column(String(50), nullable=True)
    
    # Policy holder information
    policy_holder_name = Column(String(200), nullable=True)
    relationship_to_policy_holder = Column(String(50), nullable=True)
    
    # Document storage
    document_url = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="insurances")
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)