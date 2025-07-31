from pydantic import BaseModel, EmailStr
import uuid
from decimal import Decimal

class RegisterInitiateRequest(BaseModel):
    plan_id: uuid.UUID
    organization_name: str
    user_email: EmailStr
    user_password: str
    billing_cycle: str = "monthly" # "monthly" or "yearly"
    coupon_code: str | None = None

class RegisterInitiateResponse(BaseModel):
    payment_gateway_order_id: str
    final_amount: Decimal
    currency: str = "INR"