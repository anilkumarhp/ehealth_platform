import uuid
import enum
from sqlalchemy import (Boolean, Column, String, DateTime, func, Numeric, Integer, ForeignKey, Table)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..base import Base

# This is a many-to-many association table
plan_coupon_association = Table(
    'plan_coupon_association',
    Base.metadata,
    Column('plan_id', UUID(as_uuid=True), ForeignKey('subscription_plans.id'), primary_key=True),
    Column('coupon_id', UUID(as_uuid=True), ForeignKey('coupons.id'), primary_key=True)
)

class Coupon(Base):
    __tablename__ = 'coupons'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False, index=True) # e.g., "WELCOME20"
    discount_percentage = Column(Numeric(5, 2), nullable=False) # e.g., 20.00 for 20%
    
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    max_uses = Column(Integer, default=1)
    current_uses = Column(Integer, default=0)

    # Relationship to define which plans this coupon is valid for
    applicable_plans = relationship("SubscriptionPlan", secondary=plan_coupon_association, back_populates="available_coupons")