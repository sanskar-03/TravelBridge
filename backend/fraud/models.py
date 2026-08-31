from django.db import models
from django.conf import settings
from common.models import BaseModel

class FraudFlag(BaseModel):
    class Severity(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        RESOLVED = 'RESOLVED', 'Resolved'
        DISMISSED = 'DISMISSED', 'Dismissed'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fraud_flags')
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MEDIUM, db_index=True)
    status = models.CharField(max_length=20, choices=Status.Status if hasattr(Status, 'Status') else Status.choices, default=Status.OPEN, db_index=True)
    reason = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)
    
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_fraud_flags')

    class Meta:
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"FraudFlag [{self.severity}] for {self.user.email} - {self.reason}"
