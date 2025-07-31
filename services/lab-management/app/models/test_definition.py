from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import BaseModel

class TestDefinition(BaseModel):
    """
    Represents a single, specific test that is part of a LabService.
    For example, "Sodium" is a test definition within the "Comprehensive
    Metabolic Panel" service.
    """
    __tablename__ = "test_definitions"

    # The name of the specific test, e.g., "Glucose", "TSH", "Sodium".
    name = Column(String, nullable=False)

    # The unit of measurement for the test result, e.g., "mg/dL", "mmol/L".
    unit = Column(String, nullable=True)

    # The normal or expected range for the test result, e.g., "70-100".
    # Stored as a string for flexibility (e.g., "< 5.0", "Negative").
    reference_range = Column(String, nullable=True)

    # Foreign key linking this test back to the service panel it belongs to.
    service_id = Column(UUID(as_uuid=True), ForeignKey("lab_services.id"), nullable=False, index=True)

    # SQLAlchemy relationship to link back to the parent LabService model.
    # The 'back_populates' argument matches the relationship name in LabService.
    service = relationship("LabService", back_populates="test_definitions")