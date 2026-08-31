from rest_framework import serializers
from .models import TrackingEvent, ProofOfDelivery
import os

class TrackingEventSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.profile.display_name', read_only=True)

    class Meta:
        model = TrackingEvent
        fields = ['id', 'order', 'actor', 'actor_name', 'location_name', 'description', 'latitude', 'longitude', 'created_at']
        read_only_fields = ['id', 'actor', 'actor_name', 'created_at']


class ProofOfDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProofOfDelivery
        fields = ['id', 'order', 'submitted_by', 'image', 'notes', 'verified', 'created_at']
        read_only_fields = ['id', 'submitted_by', 'verified', 'created_at']

    def validate_image(self, value):
        # 1. File Size Validation (Max 5MB)
        max_size = 5 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("Image file too large ( > 5MB ).")
            
        # 2. Extension Validation
        ext = os.path.splitext(value.name)[1].lower()
        valid_extensions = ['.jpg', '.jpeg', '.png']
        if ext not in valid_extensions:
            raise serializers.ValidationError("Unsupported file extension. Only JPG and PNG are allowed.")
            
        # 3. Content Type Validation
        if value.content_type not in ['image/jpeg', 'image/png']:
            raise serializers.ValidationError("Invalid image format.")
            
        return value
