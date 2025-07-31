import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from enum import Enum

from app.core.security import TokenPayload


class AuditAction(Enum):
    """Audit action types for healthcare compliance."""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    ACCESS = "ACCESS"
    CONSENT_GRANTED = "CONSENT_GRANTED"
    CONSENT_REVOKED = "CONSENT_REVOKED"
    REPORT_SHARED = "REPORT_SHARED"
    PAYMENT_PROCESSED = "PAYMENT_PROCESSED"


class AuditLogger:
    """Healthcare compliance audit logger."""
    
    def __init__(self):
        # Configure structured logging for audit trail
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        
        # Create handler if not exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - AUDIT - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    async def log_patient_data_access(
        self,
        user_id: UUID,
        patient_id: UUID,
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log patient data access for HIPAA compliance."""
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "patient_data_access",
            "action": action.value,
            "user_id": str(user_id),
            "patient_id": str(patient_id),
            "resource_type": resource_type,
            "resource_id": str(resource_id) if resource_id else None,
            "details": details or {},
            "compliance": "HIPAA"
        }
        
        self.logger.info(json.dumps(audit_entry))
    
    async def log_consent_change(
        self,
        patient_id: UUID,
        consent_type: str,
        action: AuditAction,
        granted_to: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log consent changes for compliance tracking."""
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "consent_change",
            "action": action.value,
            "patient_id": str(patient_id),
            "consent_type": consent_type,
            "granted_to": str(granted_to) if granted_to else None,
            "details": details or {},
            "compliance": "GDPR,HIPAA"
        }
        
        self.logger.info(json.dumps(audit_entry))
    
    async def log_report_sharing(
        self,
        from_organization: UUID,
        to_organization: UUID,
        patient_id: UUID,
        report_id: UUID,
        authorized_by: UUID,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log medical report sharing between organizations."""
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "report_sharing",
            "action": AuditAction.REPORT_SHARED.value,
            "from_organization": str(from_organization),
            "to_organization": str(to_organization),
            "patient_id": str(patient_id),
            "report_id": str(report_id),
            "authorized_by": str(authorized_by),
            "details": details or {},
            "compliance": "HIPAA,HITECH"
        }
        
        self.logger.info(json.dumps(audit_entry))
    
    async def log_test_order_workflow(
        self,
        order_id: UUID,
        patient_id: UUID,
        action: AuditAction,
        performed_by: UUID,
        workflow_stage: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log test order workflow events."""
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "test_order_workflow",
            "action": action.value,
            "order_id": str(order_id),
            "patient_id": str(patient_id),
            "performed_by": str(performed_by),
            "workflow_stage": workflow_stage,
            "details": details or {}
        }
        
        self.logger.info(json.dumps(audit_entry))
    
    async def log_payment_transaction(
        self,
        transaction_id: str,
        patient_id: UUID,
        amount: float,
        currency: str,
        action: AuditAction,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log payment transactions for financial compliance."""
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "payment_transaction",
            "action": action.value,
            "transaction_id": transaction_id,
            "patient_id": str(patient_id),
            "amount": amount,
            "currency": currency,
            "details": details or {},
            "compliance": "PCI-DSS"
        }
        
        self.logger.info(json.dumps(audit_entry))
    
    async def log_system_access(
        self,
        user: TokenPayload,
        action: AuditAction,
        resource: str,
        success: bool,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log system access attempts."""
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "system_access",
            "action": action.value,
            "user_id": str(user.sub),
            "user_email": user.email,
            "user_roles": user.roles,
            "organization_id": str(user.org_id) if user.org_id else None,
            "resource": resource,
            "success": success,
            "details": details or {}
        }
        
        self.logger.info(json.dumps(audit_entry))
    
    async def log_data_export(
        self,
        exported_by: UUID,
        patient_id: UUID,
        data_type: str,
        export_format: str,
        recipient: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log data exports for compliance tracking."""
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "data_export",
            "action": AuditAction.ACCESS.value,
            "exported_by": str(exported_by),
            "patient_id": str(patient_id),
            "data_type": data_type,
            "export_format": export_format,
            "recipient": recipient,
            "details": details or {},
            "compliance": "GDPR,HIPAA"
        }
        
        self.logger.info(json.dumps(audit_entry))


# Singleton instance
audit_logger = AuditLogger()