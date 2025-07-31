# app/schemas/payment.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import uuid
from decimal import Decimal

from app.models.payment import PaymentStatusEnum

class PaymentBase(BaseModel):
    """Base schema for a payment."""
    amount: Decimal = Field(..., description="The amount of the transaction.")
    currency: str = Field(..., max_length=3, description="The currency of the transaction (e.g., 'INR', 'USD').")

class PaymentCreate(BaseModel):
    """
    Schema for creating a new payment record.
    This is typically done automatically when an appointment is created.
    """
    appointment_id: uuid.UUID

class PaymentUpdate(BaseModel):
    """Schema for updating a payment record (e.g., after gateway confirmation)."""
    status: Optional[PaymentStatusEnum] = None
    gateway_provider: Optional[str] = None
    gateway_transaction_id: Optional[str] = None

class Payment(PaymentBase):
    """
    Schema for reading a payment record.
    This is the main response model.
    """
    id: uuid.UUID
    appointment_id: uuid.UUID
    user_id: uuid.UUID
    status: PaymentStatusEnum
    gateway_provider: Optional[str] = None
    gateway_transaction_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# This schema will be used for the response from our payment gateway integration
class PaymentIntent(BaseModel):
    """
    Represents the information needed by a frontend client to process a payment.
    """
    client_secret: str = Field(..., description="The client secret provided by the payment gateway (e.g., Stripe).")
    payment_id: uuid.UUID = Field(..., description="The internal ID of our payment record.")