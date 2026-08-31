from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator
from common.models import BaseModel
from proposals.models import Proposal

class PaymentTransaction(BaseModel):
    """
    Authoritative record of a payment transaction.
    """
    class Status(models.TextChoices):
        CREATED = 'CREATED', 'Created'
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        SUCCEEDED = 'SUCCEEDED', 'Succeeded'
        FAILED = 'FAILED', 'Failed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        REFUNDED = 'REFUNDED', 'Refunded'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='transactions')
    proposal = models.OneToOneField(Proposal, on_delete=models.PROTECT, related_name='payment')
    
    # Authoritative Price Snapshot
    base_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    currency = models.CharField(max_length=3, default='INR')
    
    # Gateway Identifiers
    gateway_order_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    gateway_payment_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    idempotency_key = models.CharField(max_length=100, unique=True, db_index=True)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED, db_index=True)
    failure_reason = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"Tx {self.id} | {self.total_amount} {self.currency} | {self.status}"
