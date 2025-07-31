import uuid
import enum
from sqlalchemy import (Column, String, DateTime, ForeignKey, func, Enum as SQLEnum)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..base import Base

class DocumentStatus(str, enum.Enum):
    PENDING_UPLOAD = "PENDING_UPLOAD"
    UPLOAD_COMPLETE = "UPLOAD_COMPLETE"
    UPLOAD_FAILED = "UPLOAD_FAILED"

# --- THIS IS THE MISSING ENUM ---
class DocumentCategory(str, enum.Enum):
    LAB_REPORT = "LAB_REPORT"
    PRESCRIPTION = "PRESCRIPTION"
    DISCHARGE_SUMMARY = "DISCHARGE_SUMMARY"
    INVOICE = "INVOICE"
    INSURANCE = "INSURANCE"
    OTHER = "OTHER"

class MedicalDocument(Base):
    __tablename__ = 'medical_documents'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    patient_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    uploader_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # --- HIERARCHICAL METADATA COLUMNS ---
    source_organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=True, index=True)
    source_practitioner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)
    document_category = Column(SQLEnum(DocumentCategory), nullable=False, default=DocumentCategory.OTHER)
    
    # --- Existing Fields ---
    file_name = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    s3_key = Column(String, unique=True, nullable=False)
    status = Column(SQLEnum(DocumentStatus), nullable=False, default=DocumentStatus.PENDING_UPLOAD)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # --- Relationships ---
    patient = relationship("User", foreign_keys=[patient_id], backref="medical_documents")
    uploader = relationship("User", foreign_keys=[uploader_id])
    source_organization = relationship("Organization", foreign_keys=[source_organization_id])
    source_practitioner = relationship("User", foreign_keys=[source_practitioner_id])