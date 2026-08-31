from rest_framework import serializers
from django.utils import timezone
from .models import TravelPost, Location
from users.serializers import PublicProfileSerializer

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'city', 'state_province', 'country', 'country_code']

class TravelPostSerializer(serializers.ModelSerializer):
    origin_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='origin', write_only=True
    )
    destination_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='destination', write_only=True
    )
    
    origin = LocationSerializer(read_only=True)
    destination = LocationSerializer(read_only=True)
    traveler = PublicProfileSerializer(source='traveler.profile', read_only=True)
    status = serializers.CharField(read_only=True) 

    class Meta:
        model = TravelPost
        fields = [
            'id', 'traveler', 'origin', 'origin_id', 'destination', 'destination_id',
            'departure_date', 'arrival_date', 'capacity_kg', 'status', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'traveler', 'created_at', 'updated_at']

    def validate(self, data):
        origin = data.get('origin', getattr(self.instance, 'origin', None))
        destination = data.get('destination', getattr(self.instance, 'destination', None))
        
        if origin and destination and origin == destination:
            raise serializers.ValidationError({"destination": "Origin and destination cannot be identical."})

        departure_date = data.get('departure_date', getattr(self.instance, 'departure_date', None))
        arrival_date = data.get('arrival_date', getattr(self.instance, 'arrival_date', None))

        if departure_date and departure_date < timezone.now():
            raise serializers.ValidationError({"departure_date": "Departure date cannot be in the past."})

        if departure_date and arrival_date and arrival_date <= departure_date:
            raise serializers.ValidationError({"arrival_date": "Arrival date must occur after departure date."})

        notes = data.get('notes', '')
        if notes and ('<' in notes or '>' in notes or 'javascript:' in notes.lower()):
            raise serializers.ValidationError({"notes": "Notes contain disallowed HTML or markup."})

        return data

class PublicTravelPostSerializer(serializers.ModelSerializer):
    origin = LocationSerializer(read_only=True)
    destination = LocationSerializer(read_only=True)
    traveler = PublicProfileSerializer(source='traveler.profile', read_only=True)

    class Meta:
        model = TravelPost
        fields = [
            'id', 'traveler', 'origin', 'destination', 'departure_date',
            'arrival_date', 'capacity_kg', 'status', 'notes', 'created_at',
        ]
