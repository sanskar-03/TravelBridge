from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import TravelPost, Location
from .serializers import TravelPostSerializer, PublicTravelPostSerializer, LocationSerializer
from .services import find_matches_for_trip

class IsTravelerOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.traveler == request.user

class TravelPostViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['departure_date', 'capacity_kg', 'created_at']
    ordering = ['departure_date']

    def get_queryset(self):
        user = self.request.user
        if self.action == 'my_trips':
            if user.is_authenticated:
                return TravelPost.objects.filter(traveler=user).select_related('origin', 'destination', 'traveler__profile')
            return TravelPost.objects.none()

        queryset = TravelPost.objects.filter(status=TravelPost.Status.PUBLISHED).select_related('origin', 'destination', 'traveler__profile')
        origin_id = self.request.query_params.get('origin_id')
        destination_id = self.request.query_params.get('destination_id')
        if origin_id:
            queryset = queryset.filter(origin_id=origin_id)
        if destination_id:
            queryset = queryset.filter(destination_id=destination_id)
        return queryset

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve'] and self.action != 'my_trips':
            return PublicTravelPostSerializer
        return TravelPostSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'my_trips', 'publish', 'pause', 'cancel', 'matches']:
            return [permissions.IsAuthenticated(), IsTravelerOwnerOrReadOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        profile = getattr(self.request.user, 'profile', None)
        if profile and profile.role == 'REQUESTER':
            raise PermissionDenied("Requester-only accounts cannot publish travel posts.")
        serializer.save(traveler=self.request.user, status=TravelPost.Status.DRAFT)

    @action(detail=False, methods=['get'])
    def my_trips(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TravelPostSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TravelPostSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def matches(self, request, pk=None):
        """
        Returns matching package requests for a traveler's trip. Secured against IDOR.
        """
        trip = self.get_object()
        if trip.traveler != request.user:
            return Response({"detail": "Not authorized to view matches for this trip."}, status=status.HTTP_403_FORBIDDEN)
        
        results = find_matches_for_trip(trip)
        page = self.paginate_queryset(results)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(results)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        trip = self.get_object()
        if trip.traveler != request.user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        if trip.status not in [TravelPost.Status.DRAFT, TravelPost.Status.PAUSED]:
            return Response({"detail": f"Cannot publish a trip with status '{trip.status}'."}, status=status.HTTP_400_BAD_REQUEST)
        if trip.departure_date < timezone.now():
            return Response({"detail": "Cannot publish a trip whose departure date has passed."}, status=status.HTTP_400_BAD_REQUEST)
        trip.status = TravelPost.Status.PUBLISHED
        trip.save()
        return Response(TravelPostSerializer(trip).data)

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        trip = self.get_object()
        if trip.traveler != request.user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        if trip.status != TravelPost.Status.PUBLISHED:
            return Response({"detail": "Only published trips can be paused."}, status=status.HTTP_400_BAD_REQUEST)
        trip.status = TravelPost.Status.PAUSED
        trip.save()
        return Response(TravelPostSerializer(trip).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        trip = self.get_object()
        if trip.traveler != request.user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        if trip.status in [TravelPost.Status.COMPLETED, TravelPost.Status.CANCELLED]:
            return Response({"detail": "Trip is already completed or cancelled."}, status=status.HTTP_400_BAD_REQUEST)
        trip.status = TravelPost.Status.CANCELLED
        trip.save()
        return Response(TravelPostSerializer(trip).data)

class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['city', 'country', 'country_code']
