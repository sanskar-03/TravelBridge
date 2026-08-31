import uuid
from django.db import models
from django.conf import settings
from common.models import BaseModel
from proposals.models import Proposal

class Conversation(BaseModel):
    """
    Canonical conversation entity linking a Traveler and Requester 
    through a specific business proposal/relationship.
    """
    proposal = models.OneToOneField(Proposal, on_delete=models.PROTECT, related_name='conversation')
    traveler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='conversations_as_traveler')
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='conversations_as_requester')
    
    class Meta:
        indexes = [
            models.Index(fields=['traveler', 'updated_at']),
            models.Index(fields=['requester', 'updated_at']),
        ]

    def __str__(self):
        return f"Chat for Proposal {self.proposal.id}"


class Message(BaseModel):
    """
    Canonical message entity. Strictly bounded text limits.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sent_messages')
    
    content = models.TextField(max_length=2000)
    is_read = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['created_at'] # Chronological order
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]

    def __str__(self):
        return f"Msg {self.id} | {self.sender.email}"
