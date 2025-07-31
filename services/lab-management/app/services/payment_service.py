# app/services/payment_service.py

import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from uuid import UUID
from fastapi import HTTPException, status

from app.core.config import settings
from app.repositories.payment_repo import payment_repo
from app.repositories.appointment_repo import appointment_repo
from app.models.payment import Payment, PaymentStatusEnum
from app.models.appointment import AppointmentStatusEnum as ApptStatus
from app.schemas.payment import PaymentIntent

# Configure the Stripe API key on startup
stripe.api_key = settings.STRIPE_API_KEY

class PaymentService:
    """
    The business logic layer for handling payments and Stripe integration.
    """
    async def create_payment_intent(
        self, db: AsyncSession, *, appointment_id: UUID, user_id: UUID
    ) -> PaymentIntent:
        """
        Creates a payment intent with Stripe for a given appointment.
        If a payment record doesn't exist, it creates one.
        """
        # --- Business Logic: Validate appointment and permissions ---
        appointment = await appointment_repo.get(db, id=appointment_id)
        if not appointment:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Appointment not found.")
        if appointment.patient_user_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Permission denied.")

        # --- Get or Create Payment Record ---
        payment = await payment_repo.get_by_appointment_id(db, appointment_id=appointment_id)
        if not payment:
            payment = await payment_repo.create_for_appointment(db, appointment=appointment)

        if payment.status == PaymentStatusEnum.SUCCESSFUL:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "This appointment has already been paid for.")

        # --- Interact with Stripe API ---
        try:
            # Stripe expects the amount in the smallest currency unit (e.g., paise for INR)
            amount_in_paise = int(payment.amount * 100)

            intent = stripe.PaymentIntent.create(
                amount=amount_in_paise,
                currency=payment.currency.lower(),
                automatic_payment_methods={"enabled": True},
                # Add our internal IDs to the metadata for tracking in webhooks
                metadata={
                    "payment_id": str(payment.id),
                    "appointment_id": str(appointment.id),
                    "user_id": str(user_id),
                },
            )
            return PaymentIntent(client_secret=intent.client_secret, payment_id=payment.id)
        except Exception as e:
            # Handle potential exceptions from the Stripe API
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Stripe error: {str(e)}")

    async def handle_stripe_webhook(self, db: AsyncSession, payload: bytes, stripe_signature: str) -> None:
        """
        Handles incoming webhooks from Stripe to update payment and appointment status.
        """
        try:
            event = stripe.Webhook.construct_event(
                payload=payload, sig_header=stripe_signature, secret=settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Invalid webhook signature: {e}")

        # Handle the payment_intent.succeeded event
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            metadata = payment_intent["metadata"]
            payment_id = UUID(metadata["payment_id"])

            payment = await payment_repo.get(db, id=payment_id)
            if payment and payment.status != PaymentStatusEnum.SUCCESSFUL:
                # Update our payment record
                payment.status = PaymentStatusEnum.SUCCESSFUL
                payment.gateway_transaction_id = payment_intent["id"]
                db.add(payment)

                # Update the associated appointment status
                appointment = await appointment_repo.get(db, id=payment.appointment_id)
                if appointment:
                    appointment.status = ApptStatus.CONFIRMED
                    db.add(appointment)

                await db.commit()
        else:
            # Handle other event types if necessary
            print(f"Unhandled event type {event['type']}")

        return None

# Instantiate the service
payment_service = PaymentService()