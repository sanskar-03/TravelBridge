from rest_framework import serializers
from .models import UserVerification
import os

class UserVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVerification
        fields = ['id', 'user', 'status', 'document', 'rejection_reason', 'reviewed_at', 'created_at']
        read_only_fields = ['id', 'user', 'status', 'rejection_reason', 'reviewed_at', 'created_at']

    def validate_document(self, value):
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError("Document file too large (Max 10MB).")
            
        ext = os.path.splitext(value.name)[1].lower()
        valid_exts = ['.jpg', '.jpeg', '.png', '.pdf']
        if ext not in valid_exts:
            raise serializers.ValidationError("Unsupported format. Only JPG, PNG, and PDF files are permitted.")
        return value
