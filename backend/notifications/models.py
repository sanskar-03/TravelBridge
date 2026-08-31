import uuid
from django.db import models
from django.conf import settings
from common.models import BaseModel

class Notification(BaseModel):
    """
    Canonical notification entity for system events.
    """
    class EventType(models.TextChoices):
        PROPOSAL_ACCEPTED = 'PROPOSAL_ACCEPTED', 'Proposal Accepted'
        PROPOSAL_REJECTED = 'PROPOSAL_REJECTED', 'Proposal Rejected'
        ORDER_CONFIRMED = 'ORDER_CONFIRMED', 'Order Confirmed'
        DELIVERY_UPDATE = 'DELIVERY_UPDATE', 'Delivery Update'
        SYSTEM_ALERT = 'SYSTEM_ALERT', 'System Alert'

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    event_type = models.CharField(max_length=30, choices=EventType.choices, db_index=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Optional generic reference to the related business object (e.g., Order ID, Proposal ID)
    related_object_id = models.CharField(max_length=100, blank=True, null=True)
    
    is_read = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at']),
        ]

    def __str__(self):
        return f"Notification for {self.recipient.email}: {self.title}"
