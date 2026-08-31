from rest_framework import serializers
from django.utils import timezone
from .models import PackageRequest
from travel.models import Location
from travel.serializers import LocationSerializer
from users.serializers import PublicProfileSerializer

class PackageRequestSerializer(serializers.ModelSerializer):
    origin_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='origin', write_only=True
    )
    destination_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='destination', write_only=True
    )
    
    origin = LocationSerializer(read_only=True)
    destination = LocationSerializer(read_only=True)
    requester = PublicProfileSerializer(source='requester.profile', read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = PackageRequest
        fields = [
            'id', 'requester', 'origin', 'origin_id', 'destination', 'destination_id',
            'required_delivery_date', 'weight_kg', 'length_cm', 'width_cm', 'height_cm',
            'category', 'title', 'description', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'requester', 'created_at', 'updated_at']

    def validate(self, data):
        origin = data.get('origin', getattr(self.instance, 'origin', None))
        destination = data.get('destination', getattr(self.instance, 'destination', None))
        
        if origin and destination and origin == destination:
            raise serializers.ValidationError({"destination": "Origin and destination cannot be identical."})

        required_delivery_date = data.get('required_delivery_date', getattr(self.instance, 'required_delivery_date', None))
        if required_delivery_date and required_delivery_date < timezone.now():
            raise serializers.ValidationError({"required_delivery_date": "Delivery deadline cannot be in the past."})

        description = data.get('description', '')
        if description and ('<' in description or '>' in description or 'javascript:' in description.lower()):
            raise serializers.ValidationError({"description": "Description contains disallowed HTML or markup."})

        return data

class PublicPackageRequestSerializer(serializers.ModelSerializer):
    origin = LocationSerializer(read_only=True)
    destination = LocationSerializer(read_only=True)
    requester = PublicProfileSerializer(source='requester.profile', read_only=True)

    class Meta:
        model = PackageRequest
        fields = [
            'id', 'requester', 'origin', 'destination', 'required_delivery_date',
            'weight_kg', 'category', 'title', 'description', 'status', 'created_at'
        ]
