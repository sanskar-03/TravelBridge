from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import PackageRequest
from .serializers import PackageRequestSerializer, PublicPackageRequestSerializer
from .services import find_matches_for_package

class IsRequesterOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.requester == request.user

class PackageRequestViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['required_delivery_date', 'weight_kg', 'created_at']
    ordering = ['required_delivery_date']

    def get_queryset(self):
        user = self.request.user
        if self.action == 'my_requests':
            if user.is_authenticated:
                return PackageRequest.objects.filter(requester=user).select_related('origin', 'destination', 'requester__profile')
            return PackageRequest.objects.none()

        queryset = PackageRequest.objects.filter(status=PackageRequest.Status.PUBLISHED).select_related('origin', 'destination', 'requester__profile')
        
        origin_id = self.request.query_params.get('origin_id')
        destination_id = self.request.query_params.get('destination_id')
        category = self.request.query_params.get('category')
        
        if origin_id:
            queryset = queryset.filter(origin_id=origin_id)
        if destination_id:
            queryset = queryset.filter(destination_id=destination_id)
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve'] and self.action != 'my_requests':
            return PublicPackageRequestSerializer
        return PackageRequestSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'my_requests', 'publish', 'pause', 'cancel', 'matches']:
            return [permissions.IsAuthenticated(), IsRequesterOwnerOrReadOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        profile = getattr(self.request.user, 'profile', None)
        if profile and profile.role == 'TRAVELER':
            raise permissions.PermissionDenied("Traveler-only accounts cannot create package requests.")
        serializer.save(requester=self.request.user, status=PackageRequest.Status.DRAFT)

    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PackageRequestSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PackageRequestSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def matches(self, request, pk=None):
        """
        Returns matching trips for the requester's package. Secured against IDOR.
        """
        package = self.get_object()
        if package.requester != request.user:
            return Response({"detail": "Not authorized to view matches for this request."}, status=status.HTTP_403_FORBIDDEN)
        
        results = find_matches_for_package(package)
        page = self.paginate_queryset(results)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(results)

    
        package = self.get_object()
        if package.requester != request.user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        if package.status not in [PackageRequest.Status.DRAFT, PackageRequest.Status.PAUSED]:
            return Response({"detail": f"Cannot publish a request with status '{package.status}'."}, status=status.HTTP_400_BAD_REQUEST)
        if package.required_delivery_date < timezone.now():
            return Response({"detail": "Cannot publish a request with a past delivery deadline."}, status=status.HTTP_400_BAD_REQUEST)
        package.status = PackageRequest.Status.PUBLISHED
        package.save()
        return Response(PackageRequestSerializer(package).data)

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        package = self.get_object()
        if package.requester != request.user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        if package.status != PackageRequest.Status.PUBLISHED:
            return Response({"detail": "Only published requests can be paused."}, status=status.HTTP_400_BAD_REQUEST)
        package.status = PackageRequest.Status.PAUSED
        package.save()
        return Response(PackageRequestSerializer(package).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        package = self.get_object()
        if package.requester != request.user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        if package.status in [PackageRequest.Status.MATCHED, PackageRequest.Status.IN_TRANSIT, PackageRequest.Status.DELIVERED, PackageRequest.Status.CANCELLED]:
            return Response({"detail": f"Cannot cancel request in '{package.status}' state."}, status=status.HTTP_400_BAD_REQUEST)
        package.status = PackageRequest.Status.CANCELLED
        package.save()
        return Response(PackageRequestSerializer(package).data)


    


    @action(detail=True, methods=['post'], url_path='publish', url_name='publish')
    def publish(self, request, pk=None):
        pkg = self.get_object()
        pkg.status = getattr(pkg.Status, 'PUBLISHED', 'PUBLISHED')
        pkg.save()
        return Response({'status': 'published'}, status=200)
