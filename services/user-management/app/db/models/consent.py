import uuid
import enum
from sqlalchemy import (Column, String, DateTime, ForeignKey, func, Enum as SQLEnum, JSON, Boolean)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from ..base import Base

class ConsentStatus(str, enum.Enum):
    GRANTED = "GRANTED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"

class ConsentRecord(Base):
    __tablename__ = 'consent_records'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # The patient who owns the data and is giving consent
    patient_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # The user (doctor, family member) who is being given access
    data_fiduciary_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)

    status = Column(SQLEnum(ConsentStatus), nullable=False, default=ConsentStatus.GRANTED)
    
    # Details of the consent based on DPDPA principles
    purpose = Column(String, nullable=False)
    data_categories = Column(ARRAY(String), nullable=False) # e.g., ["MEDICAL_REPORTS", "PRESCRIPTIONS"]
    
    granted_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False) # Consent must have an expiry
    withdrawn_at = Column(DateTime, nullable=True)
    
    # A JSON object representing the DPDPA-compliant consent artifact
    consent_artifact = Column(JSON, nullable=True)

    patient = relationship("User", foreign_keys=[patient_id])
    data_fiduciary = relationship("User", foreign_keys=[data_fiduciary_id])

class DataSharingLog(Base):
    __tablename__ = 'data_sharing_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    consent_record_id = Column(UUID(as_uuid=True), ForeignKey('consent_records.id'), nullable=False)
    
    # The user who accessed the data
    data_consumer_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    # The patient whose data was accessed
    patient_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    data_accessed = Column(ARRAY(String), nullable=False)
    accessed_at = Column(DateTime, server_default=func.now(), nullable=False)
    purpose_fulfilled = Column(Boolean, default=False)