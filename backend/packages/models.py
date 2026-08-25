from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from common.models import BaseModel
from travel.models import Location

class PackageRequest(BaseModel):
    """
    Represents a requester's need to transport an item.
    """
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        OPEN = 'OPEN', 'Open'
        MATCHING = 'MATCHING', 'Matching'
        MATCHED = 'MATCHED', 'Matched'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'
        DISPUTED = 'DISPUTED', 'Disputed'

    class ItemCategory(models.TextChoices):
        DOCUMENTS = 'DOC', 'Documents'
        CLOTHING = 'CLO', 'Clothing'
        ELECTRONICS = 'ELE', 'Electronics'
        PERSONAL = 'PER', 'Personal Items'
        GIFTS = 'GFT', 'Gifts'
        OTHER = 'OTH', 'Other'

    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='package_requests')
    
    origin = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='packages_from')
    destination = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='packages_to')
    
    requested_pickup_date = models.DateTimeField()
    required_delivery_date = models.DateTimeField(db_index=True)
    
    weight_kg = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.1'))]
    )
    
    # Structured dimensions: Length x Width x Height in cm
    length_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    width_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    
    category = models.CharField(max_length=3, choices=ItemCategory.choices, default=ItemCategory.OTHER)
    description = models.TextField()
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(weight_kg__gt=0), name='weight_must_be_positive'),
        ]
        indexes = [
            models.Index(fields=['status', 'required_delivery_date']),
            models.Index(fields=['origin', 'destination']),
        ]

    def __str__(self):
        return f"Package {self.id} | {self.origin} -> {self.destination}"
