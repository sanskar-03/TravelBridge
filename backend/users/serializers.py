from rest_framework import serializers
from .models import Profile, User

class CurrentUserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    is_email_verified = serializers.BooleanField(source='user.is_email_verified', read_only=True)
    completion_percentage = serializers.IntegerField(read_only=True)
    verification_status = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'email', 'display_name', 'bio', 'role', 'verification_status',
            'phone_number', 'phone_verified', 'profile_visibility',
            'email_notifications', 'push_notifications', 'language',
            'is_email_verified', 'completion_percentage', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'phone_verified', 'verification_status']

    def validate_display_name(self, value):
        if value:
            if '<' in value or '>' in value or 'script' in value.lower():
                raise serializers.ValidationError("Display name contains invalid characters or markup.")
            if len(value.strip()) < 2:
                raise serializers.ValidationError("Display name must be at least 2 characters long.")
        return value.strip()

    def validate_bio(self, value):
        if value:
            if '<' in value or '>' in value or 'javascript:' in value.lower():
                raise serializers.ValidationError("Bio contains disallowed HTML or markup.")
        return value.strip()

    def validate_role(self, value):
        valid_roles = [choice[0] for choice in Profile.RoleChoice.choices]
        if value not in valid_roles:
            raise serializers.ValidationError("Invalid role selection.")
        return value


class PublicProfileSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField()
    bio = serializers.CharField()
    role = serializers.CharField()
    verification_status = serializers.CharField()
    completion_percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'display_name', 'bio', 'role', 'verification_status',
            'completion_percentage', 'created_at',
        ]
