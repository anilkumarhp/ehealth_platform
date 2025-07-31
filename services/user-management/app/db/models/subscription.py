import uuid
import enum
from sqlalchemy import (Boolean, Column, String, JSON, Numeric)
from sqlalchemy.dialects.postgresql import UUID
from ..base import Base
from .coupon import plan_coupon_association # Import the association table
from sqlalchemy.orm import relationship

class SubscriptionPlan(Base):
    __tablename__ = 'subscription_plans'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    price_monthly = Column(Numeric(10, 2), nullable=False)
    price_yearly = Column(Numeric(10, 2), nullable=False)
    
    # --- NEW FIELD for general discounts ---
    discount_percentage = Column(Numeric(5, 2), default=0.00)

    features = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)

    # --- NEW RELATIONSHIP to coupons ---
    available_coupons = relationship("Coupon", secondary=plan_coupon_association, back_populates="applicable_plans")