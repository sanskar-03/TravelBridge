from django.db import models
from django.conf import settings
from common.models import BaseModel
from orders.models import Order

class TrackingEvent(BaseModel):
    """
    Immutable historical tracking event for an order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking_events')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    
    location_name = models.CharField(max_length=255, blank=True, help_text="Human readable location milestone.")
    description = models.TextField(blank=True)
    
    # Coordinates are optional, supporting future GPS integration if authorized
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', 'created_at']),
        ]

    def __str__(self):
        return f"Event for {self.order.reference_code} at {self.created_at}"


class ProofOfDelivery(BaseModel):
    """
    Securely stored Proof of Delivery (POD) record.
    """
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='proof_of_delivery')
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    
    # Stored in protected media directory; served only via authorized API endpoints
    image = models.ImageField(upload_to='pod_uploads/')
    notes = models.TextField(blank=True)
    verified = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Proofs of Delivery"

    def __str__(self):
        return f"POD for {self.order.reference_code}"
