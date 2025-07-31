# app/schemas/report.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
import uuid
from datetime import datetime

class TestResult(BaseModel):
    """Schema for a single test result within a report."""
    test_name: str
    value: str
    unit: Optional[str] = None
    range: Optional[str] = None

class ReportBase(BaseModel):
    """Base schema for a report."""
    report_type: str = Field(..., description="High-level type of the report, e.g., 'Blood Test'")
    test_results: Optional[List[TestResult]] = Field(None, description="A list of individual test results.")

class ReportCreate(BaseModel):
    """
    Schema for creating a new report. This is used when uploading.
    The file itself will be handled as a separate upload form field.
    """
    appointment_id: uuid.UUID
    report_type: str
    test_results: Optional[List[TestResult]] = None
    additional_data: Optional[dict[str, Any]] = None
    
class ReportUpdate(BaseModel):
    """Schema for updating a report's metadata. All fields are optional."""
    report_type: Optional[str] = None
    test_results: Optional[List[TestResult]] = None
    additional_data: Optional[dict[str, Any]] = None

class Report(ReportBase):
    """
    Schema for reading a report.
    This is the main response model.
    """
    id: uuid.UUID
    patient_user_id: uuid.UUID
    uploading_lab_id: uuid.UUID
    appointment_id: uuid.UUID
    created_at: datetime
    # We will add a presigned_url field later for secure downloads
    download_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ReportWithDownloadUrl(Report):
    """
    A specific response model that includes a temporary, secure URL for downloading the report file.
    """
    download_url: str