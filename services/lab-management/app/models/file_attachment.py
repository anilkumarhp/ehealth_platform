from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime

from app.db.base import Base


class FileAttachment(Base):
    """Model for file attachments (lab results, documents, etc.)"""
    
    __tablename__ = "file_attachments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)
    file_category = Column(String(50), nullable=False)  # 'lab_result', 'document', 'image'
    
    # Foreign keys
    test_order_id = Column(UUID(as_uuid=True), ForeignKey("test_orders.id"), nullable=True)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), nullable=False)
    
    # Metadata
    description = Column(Text, nullable=True)
    upload_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    test_order = relationship("TestOrder", back_populates="attachments")
    appointment = relationship("Appointment", back_populates="attachments")