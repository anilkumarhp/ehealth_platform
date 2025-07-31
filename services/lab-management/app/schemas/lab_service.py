from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional
import uuid
from decimal import Decimal

from .validators import HealthcareValidators

# ==================================
# Schemas for TestDefinition
# ==================================

class TestDefinitionBase(BaseModel):
    """Base schema for a test definition."""
    name: str = Field(..., max_length=255, description="Name of the specific test, e.g., 'Glucose'")
    unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement, e.g., 'mg/dL'")
    reference_range: Optional[str] = Field(None, max_length=100, description="Normal range, e.g., '70-100'")
    
    @field_validator('name')
    @classmethod
    def validate_test_name(cls, v):
        return HealthcareValidators.validate_test_name(v)
    
    @field_validator('reference_range')
    @classmethod
    def validate_reference_range(cls, v):
        if v is not None:
            return HealthcareValidators.validate_reference_range(v)
        return v

class TestDefinitionCreate(TestDefinitionBase):
    """Schema used when creating a new test definition within a service."""
    pass

class TestDefinition(TestDefinitionBase):
    """Schema for reading a test definition, includes its ID."""
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


# ==================================
# Schemas for LabService
# ==================================

class LabServiceBase(BaseModel):
    """Base schema for a lab service."""
    name: str = Field(..., max_length=255, description="Name of the service, e.g., 'Comprehensive Metabolic Panel'")
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, description="Price of the service")
    is_active: bool = True
    
    @field_validator('name')
    @classmethod
    def validate_service_name(cls, v):
        return HealthcareValidators.validate_lab_service_name(v)
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if isinstance(v, (int, float)):
            v = Decimal(str(v))
        return Decimal(str(HealthcareValidators.validate_price(float(v))))

class LabServiceCreate(LabServiceBase):
    """
    Schema for creating a new lab service.
    It includes a list of test definitions to be created along with the service.
    """
    test_definitions: List[TestDefinitionCreate] = []

class LabServiceUpdate(BaseModel):
    """Schema for updating an existing lab service. All fields are optional."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    is_active: Optional[bool] = None

class LabService(LabServiceBase):
    """
    Schema for reading a lab service.
    This is the main response model, including the service's ID and its
    full list of test definitions.
    """
    id: uuid.UUID
    lab_id: uuid.UUID
    test_definitions: List[TestDefinition] = []

    model_config = ConfigDict(from_attributes=True)