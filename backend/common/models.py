import uuid
from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    """
    Abstract base model providing UUID primary key and timestamps.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
