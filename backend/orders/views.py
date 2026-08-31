from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.core.exceptions import ValidationError
from .models import Order
from .serializers import OrderSerializer
from .services import transition_delivery_status

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            Q(traveler=user) | Q(requester=user)
        ).select_related(
            'traveler__profile', 'requester__profile', 'trip', 'package_request', 'proposal'
        ).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_ready(self, request, pk=None):
        order = self.get_object()
        try:
            updated_order = transition_delivery_status(order, request.user, 'ready')
            return Response(OrderSerializer(updated_order).data)
        except ValidationError as e:
            return Response({"detail": str(e.message)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_picked_up(self, request, pk=None):
        order = self.get_object()
        try:
            updated_order = transition_delivery_status(order, request.user, 'picked_up')
            return Response(OrderSerializer(updated_order).data)
        except ValidationError as e:
            return Response({"detail": str(e.message)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_in_transit(self, request, pk=None):
        order = self.get_object()
        try:
            updated_order = transition_delivery_status(order, request.user, 'in_transit')
            return Response(OrderSerializer(updated_order).data)
        except ValidationError as e:
            return Response({"detail": str(e.message)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        order = self.get_object()
        try:
            updated_order = transition_delivery_status(order, request.user, 'delivered')
            return Response(OrderSerializer(updated_order).data)
        except ValidationError as e:
            return Response({"detail": str(e.message)}, status=status.HTTP_400_BAD_REQUEST)
