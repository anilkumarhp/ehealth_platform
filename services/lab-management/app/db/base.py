# app/db/base.py (Updated with created_by and updated_by)

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, func, ForeignKey
import uuid
from sqlalchemy.dialects.postgresql import UUID

# Create a base class that all ORM models will inherit from.
Base = declarative_base()

class BaseModel(Base):
    """
    An abstract base model that provides self-updating
    `created_at`, `updated_at`, `created_by`, and `updated_by` fields.
    """
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False) 
    created_by_user_id = Column(UUID(as_uuid=True), nullable=True)
    updated_by_user_id = Column(UUID(as_uuid=True), nullable=True)
   