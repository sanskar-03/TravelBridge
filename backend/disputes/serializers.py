from rest_framework import serializers
from .models import Dispute
from users.serializers import PublicProfileSerializer

class DisputeSerializer(serializers.ModelSerializer):
    opened_by = PublicProfileSerializer(source='opened_by.profile', read_only=True)
    against_user = PublicProfileSerializer(source='against_user.profile', read_only=True)

    class Meta:
        model = Dispute
        fields = [
            'id', 'order', 'opened_by', 'against_user', 'reason', 
            'description', 'status', 'resolution_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'opened_by', 'against_user', 'status', 'resolution_notes', 'created_at', 'updated_at']

    def validate_description(self, value):
        if value:
            if '<' in value or '>' in value or 'javascript:' in value.lower():
                raise serializers.ValidationError("Description contains disallowed HTML or markup.")
        return value.strip()
