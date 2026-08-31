import os
from django.db import models
from django.conf import settings
from common.models import BaseModel

class UserVerification(BaseModel):
    class Status(models.TextChoices):
        NOT_SUBMITTED = 'NOT_SUBMITTED', 'Not Submitted'
        PENDING = 'PENDING', 'Pending Review'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='verification_record')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    document = models.FileField(upload_to='verifications/')
    rejection_reason = models.TextField(blank=True)
    
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_verifications')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Verification for {self.user.email} - {self.status}"
