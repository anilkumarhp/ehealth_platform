"""
Compliance and audit schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime


class AuditLogFilter(BaseModel):
    """Schema for filtering audit logs."""
    pharmacy_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    severity: Optional[str] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)


class AuditLogResponse(BaseModel):
    """Audit log response schema."""
    id: UUID
    user_id: Optional[UUID] = None
    pharmacy_id: Optional[UUID] = None
    action: str
    resource_type: str
    resource_id: Optional[UUID] = None
    description: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    severity: str
    created_at: datetime
    hipaa_logged: bool
    
    class Config:
        from_attributes = True


class ControlledSubstanceLogResponse(BaseModel):
    """Controlled substance log response."""
    id: UUID
    pharmacy_id: UUID
    medicine_id: UUID
    dea_schedule: str
    transaction_type: str
    quantity: int
    patient_name: Optional[str] = None
    prescriber_name: Optional[str] = None
    pharmacist_name: str
    created_at: datetime
    reported_to_pdmp: bool
    
    class Config:
        from_attributes = True


class ComplianceReport(BaseModel):
    """Compliance report schema."""
    pharmacy_id: UUID
    report_period: str
    total_transactions: int
    controlled_substance_transactions: int
    prescription_validations: int
    audit_events: int
    compliance_score: float
    issues_found: int
    recommendations: list = []