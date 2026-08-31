from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import BaseModel
from orders.models import Order

class Review(BaseModel):
    """
    Canonical review model allowing participants of a completed order to review each other.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='reviews_given')
    reviewee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='reviews_received')
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=1000, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(rating__gte=1) & models.Q(rating__lte=5), name='valid_rating_range'),
            models.CheckConstraint(check=~models.Q(reviewer=models.F('reviewee')), name='prevent_self_review'),
            models.UniqueConstraint(fields=['order', 'reviewer', 'reviewee'], name='unique_review_per_participant_per_order')
        ]
        indexes = [
            models.Index(fields=['reviewee', 'rating']),
        ]

    def __str__(self):
        return f"Review {self.rating}★ by {self.reviewer} for {self.reviewee} on Order {self.order.reference_code}"
