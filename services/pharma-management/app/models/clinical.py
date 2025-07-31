"""
Clinical support and compliance models
"""

from sqlalchemy import Column, String, Text, Integer, Date, Boolean, ForeignKey, JSON, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class InteractionSeverityEnum(enum.Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CONTRAINDICATED = "contraindicated"


class ADRSeverityEnum(enum.Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    LIFE_THREATENING = "life_threatening"
    FATAL = "fatal"


class ADRCausalityEnum(enum.Enum):
    CERTAIN = "certain"
    PROBABLE = "probable"
    POSSIBLE = "possible"
    UNLIKELY = "unlikely"
    CONDITIONAL = "conditional"
    UNASSESSABLE = "unassessable"


class DrugInteraction(BaseModel):
    """Drug-drug interaction database."""
    
    __tablename__ = "drug_interactions"
    
    # Drug Information
    drug1_id = Column(UUID(as_uuid=True), ForeignKey("medicines.id"), nullable=False, index=True)
    drug2_id = Column(UUID(as_uuid=True), ForeignKey("medicines.id"), nullable=False, index=True)
    
    # Interaction Details
    interaction_type = Column(String(100), nullable=False)  # pharmacokinetic, pharmacodynamic
    severity = Column(String(50), nullable=False, index=True)
    mechanism = Column(Text, nullable=False)
    clinical_effect = Column(Text, nullable=False)
    
    # Management
    management_strategy = Column(Text, nullable=True)
    monitoring_required = Column(Boolean, default=False)
    monitoring_parameters = Column(JSON, nullable=True)
    
    # Alternative Recommendations
    alternative_drugs = Column(JSON, nullable=True)
    dose_adjustment_required = Column(Boolean, default=False)
    dose_adjustment_details = Column(Text, nullable=True)
    
    # Evidence
    evidence_level = Column(String(50), nullable=True)  # A, B, C, D
    references = Column(JSON, nullable=True)  # Literature references
    
    # Status
    is_active = Column(Boolean, default=True)
    last_reviewed = Column(Date, nullable=True)
    reviewed_by = Column(String(255), nullable=True)
    
    # Relationships
    drug1 = relationship("Medicine", foreign_keys=[drug1_id])
    drug2 = relationship("Medicine", foreign_keys=[drug2_id])
    
    def __repr__(self):
        return f"<DrugInteraction(severity='{self.severity}', type='{self.interaction_type}')>"


class InteractionCheck(BaseModel):
    """Record of drug interaction checks performed."""
    
    __tablename__ = "interaction_checks"
    
    # Basic Information
    check_id = Column(String(100), unique=True, nullable=False, index=True)
    prescription_id = Column(UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=True, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True, index=True)
    patient_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Check Details
    check_date = Column(DateTime, nullable=False)
    checked_by = Column(UUID(as_uuid=True), nullable=False)  # Pharmacist/System
    check_type = Column(String(50), nullable=False)  # manual, automated
    
    # Medicines Checked
    medicines_checked = Column(JSON, nullable=False)  # List of medicine IDs
    current_medications = Column(JSON, nullable=True)  # Patient's current meds
    
    # Results
    interactions_found = Column(Integer, default=0)
    highest_severity = Column(String(50), nullable=True)
    interaction_details = Column(JSON, nullable=True)  # Detailed results
    
    # Actions Taken
    action_required = Column(Boolean, default=False)
    actions_taken = Column(JSON, nullable=True)  # List of actions
    pharmacist_notes = Column(Text, nullable=True)
    
    # Patient Communication
    patient_counseled = Column(Boolean, default=False)
    counseling_notes = Column(Text, nullable=True)
    
    # Relationships
    prescription = relationship("Prescription")
    order = relationship("Order")
    
    def __repr__(self):
        return f"<InteractionCheck(id='{self.check_id}', interactions={self.interactions_found})>"


class AdverseDrugReaction(BaseModel):
    """Adverse Drug Reaction (ADR) reports for pharmacovigilance."""
    
    __tablename__ = "adverse_drug_reactions"
    
    # Report Information
    report_id = Column(String(100), unique=True, nullable=False, index=True)
    report_date = Column(Date, nullable=False)
    reporter_type = Column(String(50), nullable=False)  # pharmacist, doctor, patient
    reporter_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Patient Information
    patient_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    patient_age = Column(Integer, nullable=True)
    patient_gender = Column(String(10), nullable=True)
    patient_weight = Column(Numeric(5, 2), nullable=True)
    patient_medical_history = Column(JSON, nullable=True)
    
    # Drug Information
    suspected_drug_id = Column(UUID(as_uuid=True), ForeignKey("medicines.id"), nullable=False, index=True)
    suspected_drug_name = Column(String(255), nullable=False)
    batch_number = Column(String(100), nullable=True)
    manufacturer = Column(String(255), nullable=True)
    
    # Dosage Information
    dose = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    route_of_administration = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    stop_date = Column(Date, nullable=True)
    
    # Reaction Details
    reaction_description = Column(Text, nullable=False)
    reaction_start_date = Column(Date, nullable=False)
    reaction_end_date = Column(Date, nullable=True)
    severity = Column(String(50), nullable=False, index=True)
    outcome = Column(String(100), nullable=False)  # recovered, recovering, not_recovered, fatal
    
    # Causality Assessment
    causality = Column(String(50), nullable=True, index=True)
    causality_assessed_by = Column(UUID(as_uuid=True), nullable=True)
    causality_assessment_date = Column(Date, nullable=True)
    
    # Dechallenge/Rechallenge
    dechallenge = Column(String(50), nullable=True)  # positive, negative, not_applicable
    rechallenge = Column(String(50), nullable=True)  # positive, negative, not_done
    
    # Concomitant Medications
    concomitant_medications = Column(JSON, nullable=True)
    
    # Medical History
    relevant_medical_history = Column(Text, nullable=True)
    relevant_lab_data = Column(JSON, nullable=True)
    
    # Treatment
    treatment_given = Column(Text, nullable=True)
    treatment_outcome = Column(String(100), nullable=True)
    
    # Regulatory Reporting
    reported_to_authority = Column(Boolean, default=False)
    authority_report_number = Column(String(100), nullable=True)
    report_date_to_authority = Column(Date, nullable=True)
    
    # Follow-up
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(Date, nullable=True)
    follow_up_notes = Column(Text, nullable=True)
    
    # Status
    status = Column(String(50), default="draft")  # draft, submitted, under_review, closed
    
    # Relationships
    suspected_drug = relationship("Medicine")
    
    def __repr__(self):
        return f"<AdverseDrugReaction(id='{self.report_id}', severity='{self.severity}')>"


class ClinicalAlert(BaseModel):
    """Clinical alerts and warnings."""
    
    __tablename__ = "clinical_alerts"
    
    # Alert Information
    alert_id = Column(String(100), unique=True, nullable=False, index=True)
    alert_type = Column(String(50), nullable=False, index=True)  # drug_interaction, allergy, contraindication
    severity = Column(String(50), nullable=False, index=True)
    
    # Trigger Information
    medicine_id = Column(UUID(as_uuid=True), ForeignKey("medicines.id"), nullable=True, index=True)
    patient_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    prescription_id = Column(UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=True, index=True)
    
    # Alert Details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=True)
    
    # Trigger Conditions
    trigger_conditions = Column(JSON, nullable=True)
    
    # Actions
    action_required = Column(Boolean, default=True)
    possible_actions = Column(JSON, nullable=True)  # List of possible actions
    
    # Status
    status = Column(String(50), default="active")  # active, acknowledged, dismissed, resolved
    acknowledged_by = Column(UUID(as_uuid=True), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Expiry
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    medicine = relationship("Medicine")
    prescription = relationship("Prescription")
    
    def __repr__(self):
        return f"<ClinicalAlert(type='{self.alert_type}', severity='{self.severity}')>"