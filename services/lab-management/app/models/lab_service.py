# app/models/lab_service.py

from sqlalchemy import Column, String, ForeignKey, Boolean, Numeric
from sqlalchemy.ext.hybrid import hybrid_property
from decimal import Decimal
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import BaseModel

class LabService(BaseModel):
    """
    Represents a service (a type of report or panel) offered by a specific lab.
    This forms the lab's service catalog.
    """
    __tablename__ = "lab_services"

    # The name of the service, e.g., "Comprehensive Metabolic Panel".
    name = Column(String, nullable=False)

    # A detailed description of the service.
    description = Column(String, nullable=True)

    # The price for this service. Using Numeric for precision with currency.
    price = Column(Numeric(10, 2), nullable=False)

    # Foreign key to the lab/organization offering this service.
    lab_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # A flag to allow labs to enable/disable services from their public catalog.
    is_active = Column(Boolean, default=True, nullable=False)

    # This creates a one-to-many relationship: one LabService has many TestDefinitions.
    # 'cascade="all, delete-orphan"' means if a LabService is deleted,
    # all its associated TestDefinitions are also deleted.
    test_definitions = relationship(
        "TestDefinition",
        back_populates="service",
        cascade="all, delete-orphan"
    )
    
    # Relationship to test duration configuration
    duration_config = relationship(
        "TestDuration",
        back_populates="lab_service",
        uselist=False  # One-to-one relationship
    )
    
    @hybrid_property
    def price_decimal(self):
        """Ensure price is always returned as Decimal."""
        return Decimal(str(self.price)) if self.price else Decimal('0.00')