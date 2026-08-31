from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Q
from .models import Proposal
from .serializers import ProposalSerializer
from travel.models import TravelPost
from packages.models import PackageRequest

class ProposalViewSet(viewsets.ModelViewSet):
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Users can only see proposals where they are the traveler or requester
        return Proposal.objects.filter(
            Q(traveler=user) | Q(requester=user)
        ).select_related(
            'trip__origin', 'trip__destination', 'package_request__origin', 
            'package_request__destination', 'traveler__profile', 'requester__profile'
        ).order_params('-created_at') if hasattr(Proposal.objects, 'order_params') else Proposal.objects.filter(
            Q(traveler=user) | Q(requester=user)
        ).order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user
        trip_id = self.request.data.get('trip')
        package_id = self.request.data.get('package_request')

        try:
            trip = TravelPost.objects.get(id=trip_id, traveler=user, status=TravelPost.Status.PUBLISHED)
        except TravelPost.DoesNotExist:
            raise PermissionDenied("You do not own this published trip.")

        try:
            package_req = PackageRequest.objects.get(id=package_id, status=PackageRequest.Status.PUBLISHED)
        except PackageRequest.DoesNotExist:
            raise PermissionDenied("Package request is unavailable or not published.")

        if package_req.requester == user:
            raise PermissionDenied("You cannot create a proposal for your own package.")

        # Hard constraints re-validation before proposal
        if trip.capacity_kg < package_req.weight_kg:
            raise PermissionDenied("Insufficient capacity for this package.")
        if trip.departure_date > package_req.required_delivery_date:
            raise PermissionDenied("Trip departure date is past the delivery deadline.")

        serializer.save(
            traveler=user,
            requester=package_req.requester,
            status=Proposal.Status.PENDING
        )

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """
        Atomic transaction to safely accept a proposal and prevent race conditions.
        """
        with transaction.atomic():
            # select_for_update() locks the row to prevent concurrent acceptance
            try:
                proposal = Proposal.objects.select_for_update().get(pk=pk, requester=request.user)
            except Proposal.DoesNotExist:
                return Response({"detail": "Not authorized or proposal does not exist."}, status=status.HTTP_403_FORBIDDEN)

            if proposal.status != Proposal.Status.PENDING:
                return Response({"detail": f"Proposal cannot be accepted because it is '{proposal.status}'."}, status=status.HTTP_400_BAD_REQUEST)

            proposal.status = Proposal.Status.ACCEPTED
            proposal.save()

            # Optional: Advance the package status conceptually
            pkg = proposal.package_request
            pkg.status = 'MATCHED'
            pkg.save()

            return Response(ProposalSerializer(proposal).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        proposal = self.get_object()
        if proposal.requester != request.user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        if proposal.status != Proposal.Status.PENDING:
            return Response({"detail": "Only pending proposals can be rejected."}, status=status.HTTP_400_BAD_REQUEST)

        proposal.status = Proposal.Status.REJECTED
        proposal.save()
        return Response(ProposalSerializer(proposal).data)

    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        proposal = self.get_object()
        if proposal.traveler != request.user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        if proposal.status != Proposal.Status.PENDING:
            return Response({"detail": "Only pending proposals can be withdrawn."}, status=status.HTTP_400_BAD_REQUEST)

        proposal.status = Proposal.Status.WITHDRAWN
        proposal.save()
        return Response(ProposalSerializer(proposal).data)
