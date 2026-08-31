from rest_framework import serializers
from .models import Conversation, Message
from users.serializers import PublicProfileSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.profile.display_name', read_only=True)
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_name', 'is_mine', 'content', 'is_read', 'created_at']
        read_only_fields = ['id', 'conversation', 'sender', 'sender_name', 'is_read', 'created_at']

    def get_is_mine(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.sender == request.user
        return False

    def validate_content(self, value):
        text = value.strip()
        if not text:
            raise serializers.ValidationError("Message cannot be empty.")
        if len(text) > 2000:
            raise serializers.ValidationError("Message exceeds maximum length of 2000 characters.")
        return text


class ConversationSerializer(serializers.ModelSerializer):
    traveler = PublicProfileSerializer(source='traveler.profile', read_only=True)
    requester = PublicProfileSerializer(source='requester.profile', read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'proposal', 'traveler', 'requester', 'last_message', 'unread_count', 'updated_at']

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return MessageSerializer(last_msg, context=self.context).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0
