import uuid
from decimal import Decimal

class MockPaymentGateway:
    """
    A fake payment gateway client that mimics the behavior of Razorpay or Stripe.
    """
    def create_order(self, amount: Decimal, currency: str = "INR") -> dict:
        """
        Creates a fake payment order.
        In a real app, this would make an HTTP request to the payment provider.
        """
        print(f"--- MOCK PAYMENT GATEWAY: Creating order for {amount} {currency} ---")
        if not isinstance(amount, Decimal) or amount <= 0:
            return {"status": "error", "message": "Invalid amount"}
        
        # A real order ID from Razorpay looks like 'order_xxxxxxxxxxxxxx'
        mock_order_id = f"order_mock_{uuid.uuid4().hex}"
        
        print(f"--- MOCK PAYMENT GATEWAY: Order created with ID: {mock_order_id} ---")
        return {"status": "success", "order_id": mock_order_id}

# Create a singleton instance to be used across the app
mock_payment_client = MockPaymentGateway()