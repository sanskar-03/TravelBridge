from rest_framework import serializers
from .models import Review
from users.serializers import PublicProfileSerializer

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = PublicProfileSerializer(source='reviewer.profile', read_only=True)
    reviewee = PublicProfileSerializer(source='reviewee.profile', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'order', 'reviewer', 'reviewee', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reviewer', 'reviewee', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate_comment(self, value):
        if value:
            if '<' in value or '>' in value or 'javascript:' in value.lower():
                raise serializers.ValidationError("Comment contains disallowed HTML or markup.")
        return value.strip()
