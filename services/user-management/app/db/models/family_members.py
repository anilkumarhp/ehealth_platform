from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.base import Base


class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class RelationEnum(str, enum.Enum):
    SPOUSE = "spouse"
    FATHER = "father"
    MOTHER = "mother"
    SON = "son"
    DAUGHTER = "daughter"
    BROTHER = "brother"
    SISTER = "sister"
    GRANDFATHER = "grandfather"
    GRANDMOTHER = "grandmother"
    GRANDSON = "grandson"
    GRANDDAUGHTER = "granddaughter"
    UNCLE = "uncle"
    AUNT = "aunt"
    NEPHEW = "nephew"
    NIECE = "niece"
    COUSIN = "cousin"
    OTHER = "other"


class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Aadhaar Security Fields
    aadhaar_last_4 = Column(String(4), nullable=True)
    hashed_aadhaar = Column(String, unique=True, index=True, nullable=True)
    aadhaar_verified = Column(Boolean, default=False, nullable=False)
    
    relation = Column(Enum(RelationEnum), nullable=False)
    full_name = Column(String(255), nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    contact_number = Column(String(15), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    modified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="family_members")
    creator = relationship("User", foreign_keys=[created_by])
    modifier = relationship("User", foreign_keys=[modified_by])