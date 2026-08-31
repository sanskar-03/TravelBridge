from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from common.models import BaseModel
from travel.models import TravelPost
from packages.models import PackageRequest

class Proposal(BaseModel):
    """
    Canonical model for a commercial proposal between a Traveler and a Requester.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'
        WITHDRAWN = 'WITHDRAWN', 'Withdrawn'
        CANCELLED = 'CANCELLED', 'Cancelled'
        EXPIRED = 'EXPIRED', 'Expired'

    traveler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='proposals_sent')
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='proposals_received')
    
    trip = models.ForeignKey(TravelPost, on_delete=models.PROTECT, related_name='proposals')
    package_request = models.ForeignKey(PackageRequest, on_delete=models.PROTECT, related_name='proposals')
    
    proposed_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    currency = models.CharField(max_length=3, default='INR')
    
    traveler_notes = models.TextField(blank=True, max_length=1000)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)

    class Meta:
        constraints = [
            # Prevent accidental duplicate active proposals for the exact same trip/package combination
            models.UniqueConstraint(
                fields=['trip', 'package_request'],
                condition=models.Q(status='PENDING'),
                name='unique_pending_proposal_per_trip_and_package'
            ),
            # Prevent a user from proposing to transport their own package
            models.CheckConstraint(
                check=~models.Q(traveler=models.F('requester')),
                name='prevent_self_dealing_proposal'
            )
        ]
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"Proposal {self.id} | {self.traveler} -> {self.requester} ({self.status})"
