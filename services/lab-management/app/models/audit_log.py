import enum
from sqlalchemy import Column, String, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.db.base import Base # Note: We are not using BaseModel here

class AuditActionEnum(enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class AuditLog(Base):
    """
    SQLAlchemy model for a centralized audit log.
    This table stores the history of all significant changes in the system.
    """
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=func.now(), nullable=False)

    # The user who performed the action.
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # The action that was performed.
    action = Column(Enum(AuditActionEnum), nullable=False)

    # The name of the table that was affected (e.g., 'reports', 'appointments').
    table_name = Column(String, nullable=False, index=True)

    # The ID of the specific record that was changed.
    record_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # The state of the data *before* the change. NULL for CREATE actions.
    old_values = Column(JSONB, nullable=True)

    # The state of the data *after* the change. NULL for DELETE actions.
    new_values = Column(JSONB, nullable=True)

    # A free-text field for any extra context or reason for the change.
    change_reason = Column(Text, nullable=True)