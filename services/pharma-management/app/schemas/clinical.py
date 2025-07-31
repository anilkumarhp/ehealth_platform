"""
Clinical support schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date


class InteractionCheckRequest(BaseModel):
    """Schema for drug interaction check request."""
    patient_id: UUID
    medicine_ids: List[UUID] = Field(..., min_items=2, max_items=20)
    current_medications: Optional[List[Dict[str, Any]]] = None
    patient_age: Optional[int] = Field(None, ge=0, le=150)
    patient_weight: Optional[float] = Field(None, gt=0)
    allergies: Optional[List[str]] = None
    medical_conditions: Optional[List[str]] = None


class DrugInteractionDetail(BaseModel):
    """Drug interaction detail schema."""
    drug1_name: str
    drug2_name: str
    interaction_type: str
    severity: str
    mechanism: str
    clinical_effect: str
    management_strategy: Optional[str] = None
    monitoring_required: bool = False
    alternative_drugs: Optional[List[str]] = None


class InteractionCheckResponse(BaseModel):
    """Drug interaction check response."""
    check_id: str
    patient_id: UUID
    medicines_checked: List[str]
    interactions_found: int
    highest_severity: Optional[str] = None
    interactions: List[DrugInteractionDetail] = []
    recommendations: List[str] = []
    requires_pharmacist_review: bool = False
    check_timestamp: str


class ADRReportCreate(BaseModel):
    """Schema for creating ADR reports."""
    reporter_type: str = Field(..., pattern=r'^(pharmacist|doctor|patient)$')
    reporter_id: UUID
    patient_id: Optional[UUID] = None
    patient_age: Optional[int] = Field(None, ge=0, le=150)
    patient_gender: Optional[str] = Field(None, pattern=r'^(male|female|other)$')
    patient_weight: Optional[float] = Field(None, gt=0)
    suspected_drug_id: UUID
    suspected_drug_name: str
    batch_number: Optional[str] = None
    dose: str
    frequency: str
    route_of_administration: str
    start_date: date
    stop_date: Optional[date] = None
    reaction_description: str = Field(..., min_length=10)
    reaction_start_date: date
    reaction_end_date: Optional[date] = None
    severity: str = Field(..., pattern=r'^(mild|moderate|severe|life_threatening|fatal)$')
    outcome: str = Field(..., pattern=r'^(recovered|recovering|not_recovered|fatal)$')
    concomitant_medications: Optional[List[Dict[str, Any]]] = None
    relevant_medical_history: Optional[str] = None
    treatment_given: Optional[str] = None


class ADRReportResponse(BaseModel):
    """ADR report response schema."""
    id: UUID
    report_id: str
    reporter_type: str
    patient_age: Optional[int] = None
    suspected_drug_name: str
    reaction_description: str
    severity: str
    outcome: str
    status: str
    report_date: date
    reported_to_authority: bool = False
    authority_report_number: Optional[str] = None
    
    class Config:
        from_attributes = True