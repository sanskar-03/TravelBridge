from rest_framework import serializers
from .models import Proposal
from travel.models import TravelPost
from packages.models import PackageRequest
from travel.serializers import PublicTravelPostSerializer
from packages.serializers import PublicPackageRequestSerializer
from users.serializers import PublicProfileSerializer

class ProposalSerializer(serializers.ModelSerializer):
    traveler = PublicProfileSerializer(source='traveler.profile', read_only=True)
    requester = PublicProfileSerializer(source='requester.profile', read_only=True)
    trip_detail = PublicTravelPostSerializer(source='trip', read_only=True)
    package_detail = PublicPackageRequestSerializer(source='package_request', read_only=True)

    class Meta:
        model = Proposal
        fields = [
            'id', 'traveler', 'requester', 'trip', 'trip_detail', 'package_request', 'package_detail',
            'proposed_price', 'currency', 'traveler_notes', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'traveler', 'requester', 'currency', 'created_at', 'updated_at']

    def validate(self, data):
        # Prevent XSS in notes
        notes = data.get('traveler_notes', '')
        if notes and ('<' in notes or '>' in notes or 'javascript:' in notes.lower()):
            raise serializers.ValidationError({"traveler_notes": "Notes contain disallowed HTML or markup."})
        return data
