from django.db import models
from django.conf import settings
from common.models import BaseModel
from orders.models import Order

class Dispute(BaseModel):
    """
    Canonical dispute model linked to an active/completed order transaction.
    """
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'

    class Reason(models.TextChoices):
        ITEM_NOT_DELIVERED = 'ITEM_NOT_DELIVERED', 'Item Not Delivered'
        ITEM_DAMAGED = 'ITEM_DAMAGED', 'Item Damaged'
        ITEM_MISSING = 'ITEM_MISSING', 'Item Missing'
        PAYMENT_PROBLEM = 'PAYMENT_PROBLEM', 'Payment Problem'
        OTHER = 'OTHER', 'Other'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='disputes')
    opened_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='disputes_opened')
    against_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='disputes_against')
    
    reason = models.CharField(max_length=30, choices=Reason.choices, default=Reason.OTHER)
    description = models.TextField(max_length=2000)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True)
    resolution_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='disputes_resolved')

    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"Dispute {self.id} on Order {self.order.reference_code} ({self.status})"
