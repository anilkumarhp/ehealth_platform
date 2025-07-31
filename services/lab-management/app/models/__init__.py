# Import all models to ensure proper SQLAlchemy initialization
from .lab_service import LabService
from .test_definition import TestDefinition
from .test_order import TestOrder
from .appointment import Appointment
from .lab_configuration import LabConfiguration
from .test_duration import TestDuration
from .file_attachment import FileAttachment
from .audit_log import AuditLog

__all__ = [
    "LabService",
    "TestDefinition", 
    "TestOrder",
    "Appointment",
    "LabConfiguration",
    "TestDuration",
    "FileAttachment",
    "AuditLog"
]