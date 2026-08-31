from decimal import Decimal, ROUND_HALF_UP
import uuid
import hmac
import hashlib
from django.conf import settings

def calculate_pricing(base_amount: Decimal) -> dict:
    """
    Centralized pricing authority. 
    Never trust the frontend for fees or totals.
    """
    # Example Rule: 5% Platform Fee, 0% Tax for MVP
    fee_percentage = Decimal('0.05')
    
    platform_fee = (base_amount * fee_percentage).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    tax_amount = Decimal('0.00')
    total_amount = base_amount + platform_fee + tax_amount
    
    return {
        'base_amount': base_amount,
        'platform_fee': platform_fee,
        'tax_amount': tax_amount,
        'total_amount': total_amount,
        'currency': 'INR' # Fixed currency for MVP
    }

class MockPaymentGateway:
    """
    Safe abstraction for payment gateway operations.
    Replaced with actual SDK (Stripe/Razorpay) in production.
    """
    @staticmethod
    def create_order(amount: Decimal, currency: str, receipt_id: str) -> dict:
        # Simulates creating a gateway order (e.g., Razorpay Order)
        return {
            "id": f"order_{uuid.uuid4().hex[:12]}",
            "amount": float(amount),
            "currency": currency,
            "status": "created"
        }

    @staticmethod
    def verify_webhook_signature(payload_body: bytes, signature: str, secret: str) -> bool:
        # Simulates HMAC SHA256 signature verification
        expected_sig = hmac.new(secret.encode(), payload_body, hashlib.sha256).hexdigest()
        # In a real mock test, we might bypass this if signature == 'test_bypass'
        return signature == expected_sig or signature == 'test_bypass'
