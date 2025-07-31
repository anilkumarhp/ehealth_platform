import uuid
from sqlalchemy import (Boolean, Column, String, DateTime, func, JSON)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..base import Base

class Organization(Base):
    __tablename__ = 'organizations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    type = Column(String(50), nullable=True)
    registration_number = Column(String(100), unique=True, nullable=True, index=True)
    abha_facility_id = Column(String(100), unique=True, nullable=True, index=True)
    
    license_details = Column(JSON, nullable=True)
    address = Column(JSON, nullable=True)
    contact_info = Column(JSON, nullable=True)
    
    subscription_tier = Column(String(50), default='FREE', nullable=False)

    payment_gateway_order_id = Column(String, nullable=True, index=True)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    users = relationship("User", back_populates="organization")