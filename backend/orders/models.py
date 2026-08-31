import string
import random
from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator
from common.models import BaseModel
from proposals.models import Proposal
from payments.models import PaymentTransaction
from travel.models import TravelPost
from packages.models import PackageRequest

def generate_order_reference():
    return 'ORD-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class Order(BaseModel):
    class Status(models.TextChoices):
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        DISPUTED = 'DISPUTED', 'Disputed'

    class DeliveryStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        READY_FOR_PICKUP = 'READY_FOR_PICKUP', 'Ready for Pickup'
        PICKED_UP = 'PICKED_UP', 'Picked Up'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
        DELIVERED = 'DELIVERED', 'Delivered'

    reference_code = models.CharField(max_length=20, unique=True, default=generate_order_reference, db_index=True)
    
    # Core Relationships
    traveler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders_as_traveler')
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders_as_requester')
    proposal = models.OneToOneField(Proposal, on_delete=models.PROTECT, related_name='order')
    payment = models.OneToOneField(PaymentTransaction, on_delete=models.PROTECT, related_name='order')
    trip = models.ForeignKey(TravelPost, on_delete=models.PROTECT, related_name='orders')
    package_request = models.ForeignKey(PackageRequest, on_delete=models.PROTECT, related_name='orders')

    # Authoritative Historical Snapshots
    agreed_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    currency = models.CharField(max_length=3)
    origin_city = models.CharField(max_length=100)
    destination_city = models.CharField(max_length=100)
    package_weight_kg = models.DecimalField(max_digits=5, decimal_places=2)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED, db_index=True)
    delivery_status = models.CharField(max_length=20, choices=DeliveryStatus.choices, default=DeliveryStatus.PENDING, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'delivery_status']),
            models.Index(fields=['traveler', 'status']),
            models.Index(fields=['requester', 'status']),
        ]

    def __str__(self):
        return f"Order {self.reference_code} | {self.status} | {self.delivery_status}"
