"""
Compliance and audit models for regulatory requirements
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class AuditActionEnum(enum.Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    PRESCRIPTION_UPLOAD = "prescription_upload"
    PRESCRIPTION_VALIDATE = "prescription_validate"
    ORDER_CREATE = "order_create"
    ORDER_FULFILL = "order_fulfill"
    INVENTORY_UPDATE = "inventory_update"
    CONTROLLED_SUBSTANCE_DISPENSE = "controlled_substance_dispense"


class AuditLog(BaseModel):
    """Comprehensive audit logging for compliance."""
    
    __tablename__ = "audit_logs"
    
    # Basic Information
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    pharmacy_id = Column(UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=True, index=True)
    session_id = Column(String(255), nullable=True, index=True)
    
    # Action Details
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)  # prescription, order, inventory
    resource_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Request Information
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(Text, nullable=True)
    request_method = Column(String(10), nullable=True)
    request_url = Column(Text, nullable=True)
    
    # Data Changes
    old_values = Column(JSON, nullable=True)  # Before state
    new_values = Column(JSON, nullable=True)  # After state
    
    # Context
    description = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)  # Additional context
    
    # Compliance Fields
    hipaa_logged = Column(Boolean, default=True)
    retention_date = Column(DateTime, nullable=True)  # When to delete (7 years for pharma)
    
    # Status
    severity = Column(String(20), default="info")  # info, warning, error, critical
    
    # Relationships
    pharmacy = relationship("Pharmacy", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(action='{self.action}', user='{self.user_id}')>"


class ControlledSubstanceLog(BaseModel):
    """Special logging for controlled substances (DEA requirement)."""
    
    __tablename__ = "controlled_substance_logs"
    
    # References
    pharmacy_id = Column(UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=False, index=True)
    medicine_id = Column(UUID(as_uuid=True), ForeignKey("medicines.id"), nullable=False, index=True)
    prescription_id = Column(UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=True, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True, index=True)
    
    # DEA Information
    dea_schedule = Column(String(10), nullable=False)  # I, II, III, IV, V
    dea_number = Column(String(50), nullable=False)  # Pharmacy DEA number
    
    # Transaction Details
    transaction_type = Column(String(50), nullable=False)  # receive, dispense, return, destroy
    quantity = Column(Integer, nullable=False)
    unit = Column(String(50), nullable=False)
    
    # Patient Information (for dispensing)
    patient_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    patient_name = Column(String(255), nullable=True)
    patient_address = Column(Text, nullable=True)
    patient_id_verified = Column(Boolean, default=False)
    id_type = Column(String(50), nullable=True)  # drivers_license, passport, etc.
    id_number = Column(String(100), nullable=True)
    
    # Prescriber Information
    prescriber_id = Column(UUID(as_uuid=True), nullable=True)
    prescriber_name = Column(String(255), nullable=True)
    prescriber_dea = Column(String(50), nullable=True)
    prescriber_npi = Column(String(50), nullable=True)
    
    # Pharmacist Information
    pharmacist_id = Column(UUID(as_uuid=True), nullable=False)
    pharmacist_name = Column(String(255), nullable=False)
    pharmacist_license = Column(String(100), nullable=False)
    
    # Compliance
    partial_fill = Column(Boolean, default=False)
    partial_fill_reason = Column(Text, nullable=True)
    days_supply = Column(Integer, nullable=True)
    
    # Reporting
    reported_to_pdmp = Column(Boolean, default=False)  # Prescription Drug Monitoring Program
    pdmp_report_date = Column(DateTime, nullable=True)
    arcos_reported = Column(Boolean, default=False)  # DEA ARCOS reporting
    
    # Relationships
    pharmacy = relationship("Pharmacy")
    medicine = relationship("Medicine")
    prescription = relationship("Prescription")
    order = relationship("Order")
    
    def __repr__(self):
        return f"<ControlledSubstanceLog(schedule='{self.dea_schedule}', type='{self.transaction_type}')>"


class NotificationLog(BaseModel):
    """Track all notifications sent to patients and providers."""
    
    __tablename__ = "notification_logs"
    
    # References
    pharmacy_id = Column(UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=True, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True, index=True)
    prescription_id = Column(UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=True, index=True)
    
    # Recipient Information
    recipient_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    recipient_type = Column(String(50), nullable=False)  # patient, doctor, pharmacist
    recipient_contact = Column(String(255), nullable=False)  # email, phone
    
    # Notification Details
    notification_type = Column(String(100), nullable=False, index=True)  # order_ready, prescription_expired
    channel = Column(String(50), nullable=False)  # email, sms, whatsapp, push
    subject = Column(String(500), nullable=True)
    message = Column(Text, nullable=False)
    
    # Delivery Status
    status = Column(String(50), default="pending")  # pending, sent, delivered, failed
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    failed_reason = Column(Text, nullable=True)
    
    # External Service Details
    external_id = Column(String(255), nullable=True)  # Twilio SID, SendGrid ID
    external_status = Column(String(100), nullable=True)
    
    # Retry Information
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime, nullable=True)
    
    # Relationships
    pharmacy = relationship("Pharmacy")
    order = relationship("Order")
    prescription = relationship("Prescription")
    
    def __repr__(self):
        return f"<NotificationLog(type='{self.notification_type}', status='{self.status}')>"