from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.db.models import Q
from .models import Review
from .serializers import ReviewSerializer
from orders.models import Order
from notifications.services import create_system_notification

class IsOrderParticipantForReview(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in [obj.reviewer, obj.reviewee]

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrderParticipantForReview]

    def get_queryset(self):
        user = self.request.user
        reviewee_id = self.request.query_params.get('reviewee_id')
        qs = Review.objects.filter(Q(reviewer=user) | Q(reviewee=user)).select_related('reviewer__profile', 'reviewee__profile', 'order')
        if reviewee_id:
            qs = qs.filter(reviewee_id=reviewee_id)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        order_id = self.request.data.get('order')
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise PermissionDenied("Order not found.")

        # Server-side eligibility check: Order must be COMPLETED or DELIVERED
        if order.status != 'COMPLETED' and order.delivery_status != 'DELIVERED':
            raise PermissionDenied("Reviews are only allowed for completed orders.")

        # Verify user is a participant
        if user not in [order.traveler, order.requester]:
            raise PermissionDenied("You were not a participant in this order.")

        # Determine reviewee
        reviewee = order.requester if user == order.traveler else order.traveler

        if user == reviewee:
            raise PermissionDenied("You cannot review yourself.")

        # Check for duplicate review
        if Review.objects.filter(order=order, reviewer=user, reviewee=reviewee).exists():
            raise PermissionDenied("You have already reviewed this participant for this order.")

        review = serializer.save(reviewer=user, reviewee=reviewee, order=order)

        # Notify reviewee
        create_system_notification(
            recipient=reviewee,
            event_type='SYSTEM_ALERT',
            title="New Review Received",
            message=f"You received a {review.rating}-star review for order {order.reference_code}.",
            related_object_id=review.id
        )
