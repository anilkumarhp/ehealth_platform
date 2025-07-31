import stripe
from app.core.config import settings
from app.db.models import SubscriptionPlan, Coupon
from decimal import Decimal

# Configure the Stripe library with our secret key
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_subscription_checkout_session(plan: SubscriptionPlan, org_id: str) -> stripe.checkout.Session:
    """
    Creates a Stripe Checkout Session for starting a new subscription.
    """
    # In Stripe, prices must be in the smallest currency unit (e.g., cents, paise)
    # So, Rs 100.00 becomes 10000 paise.
    unit_amount = int(plan.price_monthly * 100)

    # In a real app, you would first create a Product and Price in the Stripe Dashboard
    # and use the Price ID here (e.g., price_xxxxxxxx).
    # For simplicity, we'll create the price on the fly.
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': f"{plan.name} Plan",
                    },
                    'unit_amount': unit_amount,
                    'recurring': {'interval': 'month'},
                },
                'quantity': 1,
            }],
            mode='subscription',
            # We store our internal organization ID in the metadata to retrieve it in the webhook
            metadata={
                "organization_id": org_id
            },
            # URLs to redirect the user to after payment
            success_url="http://localhost:3000/register/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:3000/register/canceled",
        )
        return session
    except Exception as e:
        # Handle exceptions from the Stripe API
        print(f"Error creating Stripe session: {e}")
        return None