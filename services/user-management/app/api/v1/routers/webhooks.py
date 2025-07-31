from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import stripe

from app.api.v1 import deps
from app.core.config import settings
from app.crud import crud_organization, crud_user, crud_rbac, crud_patient
# ... other imports as needed

router = APIRouter()

@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(deps.get_public_db)):
    """
    Handles incoming webhook events from Stripe.
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail=str(e))
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail=str(e))

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        org_id = session.get('metadata', {}).get('organization_id')

        if not org_id:
            # Log an error: metadata was missing
            return {"status": "error", "message": "Missing organization_id in webhook metadata"}

        # TODO: Find the pending organization by its ID,
        # create the user from details stored temporarily (e.g., in Redis or another table),
        # activate the organization, and send the welcome/verification emails.
        print(f"--- STRIPE WEBHOOK SUCCESS ---")
        print(f"Payment successful for Organization ID: {org_id}")
        print(f"Next steps: Activate org, create user, send emails.")
        
    return {"status": "success"}