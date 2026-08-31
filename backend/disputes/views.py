from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Dispute
from .serializers import DisputeSerializer
from orders.models import Order
from notifications.services import create_system_notification

class IsDisputeParticipantOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return request.user in [obj.opened_by, obj.against_user]

class DisputeViewSet(viewsets.ModelViewSet):
    serializer_class = DisputeSerializer
    permission_classes = [permissions.IsAuthenticated, IsDisputeParticipantOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Dispute.objects.all().select_related('opened_by__profile', 'against_user__profile', 'order')
        return Dispute.objects.filter(Q(opened_by=user) | Q(against_user=user)).select_related('opened_by__profile', 'against_user__profile', 'order')

    def perform_create(self, serializer):
        user = self.request.user
        order_id = self.request.data.get('order')
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise permissions.PermissionDenied("Order not found.")

        if user not in [order.traveler, order.requester]:
            raise permissions.PermissionDenied("You were not a participant in this order.")

        against_user = order.requester if user == order.traveler else order.traveler

        if user == against_user:
            raise permissions.PermissionDenied("You cannot open a dispute against yourself.")

        dispute = serializer.save(opened_by=user, against_user=against_user, order=order, status=Dispute.Status.OPEN)

        # Notify counterparty and protect payment settlement
        create_system_notification(
            recipient=against_user,
            event_type='SYSTEM_ALERT',
            title="Dispute Opened",
            message=f"A dispute has been opened regarding order {order.reference_code}.",
            related_object_id=dispute.id
        )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def resolve(self, request, pk=None):
        dispute = self.get_object()
        notes = request.data.get('resolution_notes', 'Resolved by admin.')
        dispute.status = Dispute.Status.RESOLVED
        dispute.resolution_notes = notes
        dispute.resolved_by = request.user
        dispute.save()

        # Notify participants
        for recipient in [dispute.opened_by, dispute.against_user]:
            create_system_notification(
                recipient=recipient,
                event_type='SYSTEM_ALERT',
                title="Dispute Resolved",
                message=f"The dispute for order {dispute.order.reference_code} has been resolved.",
                related_object_id=dispute.id
            )

        return Response(DisputeSerializer(dispute).data)
