from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.http import FileResponse
from rest_framework.throttling import UserRateThrottle
from .models import TrackingEvent, ProofOfDelivery
from orders.models import Order
from .serializers import TrackingEventSerializer, ProofOfDeliverySerializer

class TrackingRateThrottle(UserRateThrottle):
    rate = '20/min'

class PODRateThrottle(UserRateThrottle):
    rate = '5/min'

class IsOrderParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        order = obj.order if hasattr(obj, 'order') else obj
        return request.user in [order.traveler, order.requester]

class TrackingEventViewSet(viewsets.ModelViewSet):
    serializer_class = TrackingEventSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrderParticipant]
    throttle_classes = [TrackingRateThrottle]

    def get_queryset(self):
        return TrackingEvent.objects.filter(
            Q(order__traveler=self.request.user) | Q(order__requester=self.request.user)
        )

    def perform_create(self, serializer):
        order = serializer.validated_data['order']
        if self.request.user != order.traveler:
            raise PermissionDenied("Only the traveler can post tracking updates.")
        if order.delivery_status in ['DELIVERED', 'PENDING']:
            raise PermissionDenied("Cannot update tracking for this delivery status.")
            
        serializer.save(actor=self.request.user)


class ProofOfDeliveryViewSet(viewsets.ModelViewSet):
    serializer_class = ProofOfDeliverySerializer
    permission_classes = [permissions.IsAuthenticated, IsOrderParticipant]
    throttle_classes = [PODRateThrottle]

    def get_queryset(self):
        return ProofOfDelivery.objects.filter(
            Q(order__traveler=self.request.user) | Q(order__requester=self.request.user)
        )

    def perform_create(self, serializer):
        order = serializer.validated_data['order']
        if self.request.user != order.traveler:
            raise PermissionDenied("Only the traveler can submit proof of delivery.")
        if hasattr(order, 'proof_of_delivery'):
            raise PermissionDenied("Proof of delivery already submitted for this order.")
        if order.delivery_status != 'IN_TRANSIT':
            raise PermissionDenied("Order must be in transit to submit POD.")
            
        serializer.save(submitted_by=self.request.user)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Secure endpoint to serve the POD image. Bypasses public media URLs.
        """
        pod = self.get_object()
        if not pod.image:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        response = FileResponse(pod.image.open('rb'), content_type="image/jpeg")
        response['Content-Disposition'] = f'inline; filename="{pod.image.name}"'
        return response
