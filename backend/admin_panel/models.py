from django.db import models
from django.conf import settings
from common.models import BaseModel

class AdminActionAudit(BaseModel):
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='audit_logs')
    action = models.CharField(max_length=100, db_index=True)
    target_type = models.CharField(max_length=50)
    target_id = models.CharField(max_length=100)
    reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action', 'created_at']),
        ]

    def __str__(self):
        return f"[{self.action}] by {self.admin.email} on {self.target_type}:{self.target_id}"
