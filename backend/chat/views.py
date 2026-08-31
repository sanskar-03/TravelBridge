from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.throttling import UserRateThrottle
from django.db import transaction
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from proposals.models import Proposal
from notifications.services import create_system_notification

class ChatRateThrottle(UserRateThrottle):
    rate = '60/min'

class IsParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Conversation):
            return request.user in [obj.traveler, obj.requester]
        if isinstance(obj, Message):
            return request.user in [obj.conversation.traveler, obj.conversation.requester]
        return False

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def get_queryset(self):
        # IDOR Protection: Hard-scoped to user
        return Conversation.objects.filter(
            Q(traveler=self.request.user) | Q(requester=self.request.user)
        ).order_by('-updated_at')

    @action(detail=False, methods=['post'])
    def get_or_create(self, request):
        """
        Resolves or creates a conversation based on an active business proposal.
        """
        proposal_id = request.data.get('proposal_id')
        try:
            proposal = Proposal.objects.get(id=proposal_id)
        except Proposal.DoesNotExist:
            return Response({"detail": "Proposal not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user not in [proposal.traveler, proposal.requester]:
            return Response({"detail": "Not authorized to chat about this proposal."}, status=status.HTTP_403_FORBIDDEN)

        # Restrict chat to ongoing business relationships
        if proposal.status in ['REJECTED', 'WITHDRAWN', 'CANCELLED', 'EXPIRED']:
            return Response({"detail": f"Chat is closed. Proposal is {proposal.status}."}, status=status.HTTP_400_BAD_REQUEST)

        conversation, created = Conversation.objects.get_or_create(
            proposal=proposal,
            defaults={'traveler': proposal.traveler, 'requester': proposal.requester}
        )
        return Response(ConversationSerializer(conversation, context={'request': request}).data)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]
    throttle_classes = [ChatRateThrottle]

    def get_queryset(self):
        # Always filter by a specific conversation passed in query params
        conv_id = self.request.query_params.get('conversation_id')
        if conv_id:
            # The permission class checks if the user has access to the conversation messages
            return Message.objects.filter(
                conversation_id=conv_id,
                conversation__in=Conversation.objects.filter(Q(traveler=self.request.user) | Q(requester=self.request.user))
            )
        return Message.objects.none()

    def perform_create(self, serializer):
        conv_id = self.request.data.get('conversation_id')
        try:
            conv = Conversation.objects.get(id=conv_id)
        except Conversation.DoesNotExist:
            raise PermissionDenied("Conversation not found.")

        if self.request.user not in [conv.traveler, conv.requester]:
            raise PermissionDenied("You are not a participant in this conversation.")

        message = serializer.save(sender=self.request.user, conversation=conv)
        
        # Touch the conversation to bump it in the inbox list
        conv.save(update_fields=['updated_at'])

        # Notification Integration
        recipient = conv.requester if self.request.user == conv.traveler else conv.traveler
        
        # Trigger notification only after the message transaction commits
        transaction.on_commit(lambda: create_system_notification(
            recipient=recipient,
            event_type='SYSTEM_ALERT',
            title="New Message",
            message=f"You received a new message from {self.request.user.profile.display_name}.",
            related_object_id=conv.id
        ))

    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        conv_id = request.data.get('conversation_id')
        if not conv_id:
            return Response({"detail": "Conversation ID required."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Update messages sent by the OTHER person to is_read=True
        updated = Message.objects.filter(
            conversation_id=conv_id,
            conversation__in=Conversation.objects.filter(Q(traveler=request.user) | Q(requester=request.user)),
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)
        
        return Response({"status": "success", "marked_read": updated})
