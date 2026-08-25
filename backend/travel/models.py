from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from common.models import BaseModel

class Location(BaseModel):
    """
    Reusable structured location data.
    Privacy Note: Should represent cities, airports, or stations—NOT exact residential addresses.
    """
    city = models.CharField(max_length=100, db_index=True)
    state_province = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2) # ISO 3166-1 alpha-2

    class Meta:
        unique_together = ('city', 'state_province', 'country_code')
        indexes = [
            models.Index(fields=['country_code', 'city']),
        ]

    def __str__(self):
        return f"{self.city}, {self.country_code}"

class TravelPost(BaseModel):
    """
    Represents a journey published by a traveler.
    """
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'
        PAUSED = 'PAUSED', 'Paused'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    traveler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='travel_posts')
    
    origin = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='travels_from')
    destination = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='travels_to')
    
    departure_date = models.DateTimeField(db_index=True)
    arrival_date = models.DateTimeField(null=True, blank=True)
    
    # Baggage Info
    capacity_kg = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.1'))]
    )
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(capacity_kg__gt=0), name='capacity_must_be_positive'),
        ]
        indexes = [
            models.Index(fields=['status', 'departure_date']),
            models.Index(fields=['origin', 'destination']),
        ]

    def __str__(self):
        return f"{self.traveler} | {self.origin} -> {self.destination}"
