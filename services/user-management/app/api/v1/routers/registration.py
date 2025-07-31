from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal

from app.api.v1 import deps
from app.crud import crud_user, crud_organization, crud_subscription, crud_coupon
from app.api.v1.schemas import registration as reg_schema
from app.core.payment_gateway import mock_payment_client
from app.db import models
from app.core import stripe_client 

router = APIRouter()

@router.post("/register/initiate", response_model=reg_schema.RegisterInitiateResponse, status_code=status.HTTP_201_CREATED)
def initiate_organization_registration(
    *,
    db: Session = Depends(deps.get_public_db),
    request_in: reg_schema.RegisterInitiateRequest
):
    """
    Initiates registration for a new organization.
    Validates input, calculates final price, creates a payment order,
    and creates a 'pending' organization record.
    """
    # 1. Check if user already exists
    if crud_user.get_user_by_email(db, email=request_in.user_email):
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    # 2. Fetch the selected plan
    plan = crud_subscription.get_plan_by_id(db, plan_id=request_in.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found or is inactive.")

    # 3. Calculate price based on plan and optional coupon
    base_price = plan.price_monthly if request_in.billing_cycle == "monthly" else plan.price_yearly
    final_price = base_price
    
    if request_in.coupon_code:
        coupon = crud_coupon.get_valid_coupon_by_code(db, code=request_in.coupon_code, plan_id=plan.id)
        if not coupon:
            raise HTTPException(status_code=400, detail="Invalid or inapplicable coupon code.")
        # Apply percentage discount
        discount_multiplier = Decimal('1.0') - (coupon.discount_percentage / Decimal('100.0'))
        final_price *= discount_multiplier

    # Ensure price is not negative
    final_price = max(Decimal('0.00'), final_price.quantize(Decimal('0.01')))

    # 4. Create the 'pending' organization record first to get an ID
    try:
        org = models.Organization(
            name=request_in.organization_name,
            subscription_plan_id=plan.id,
            subscription_status=models.SubscriptionStatus.PENDING_PAYMENT,
        )
        db.add(org)
        db.commit()
        db.refresh(org)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not create organization record.")
    
    # 5. Create a Stripe Checkout Session
    checkout_session = stripe_client.create_subscription_checkout_session(plan=plan, org_id=str(org.id))
    if not checkout_session:
        raise HTTPException(status_code=502, detail="Could not create payment session with the gateway.")

    # Return the URL for the frontend to redirect to
    return {
        "checkout_url": checkout_session.url,
        "final_amount": final_price # For display purposes
    }