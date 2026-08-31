import pytest
from rest_framework.test import APIClient
from decimal import Decimal
from django.utils import timezone
from users.models import User, Profile
from travel.models import Location, TravelPost
from packages.models import PackageRequest
from proposals.models import Proposal
from chat.models import Conversation, Message

@pytest.mark.django_db
class TestChatSecurity:
    def setup_method(self):
        self.client = APIClient()
        self.user_t = User.objects.create_user(email="trav@test.com", password="pwd")
        self.user_r = User.objects.create_user(email="req@test.com", password="pwd")
        self.user_x = User.objects.create_user(email="hacker@test.com", password="pwd")
        
        Profile.objects.create(user=self.user_t, display_name="Traveler Bob")
        Profile.objects.create(user=self.user_r, display_name="Requester Alice")
        Profile.objects.create(user=self.user_x, display_name="Hacker Eve")

        loc = Location.objects.create(city="City A", country_code="US")
        pkg = PackageRequest.objects.create(requester=self.user_r, origin=loc, destination=loc, required_delivery_date=timezone.now(), weight_kg=1.0)
        trip = TravelPost.objects.create(traveler=self.user_t, origin=loc, destination=loc, departure_date=timezone.now(), capacity_kg=5.0)
        
        self.proposal = Proposal.objects.create(
            traveler=self.user_t, requester=self.user_r, trip=trip, package_request=pkg,
            proposed_price=Decimal("100.00"), status="ACCEPTED"
        )
        self.conv = Conversation.objects.create(proposal=self.proposal, traveler=self.user_t, requester=self.user_r)

    def test_idor_conversation_access(self):
        # User X tries to read the chat between T and R
        self.client.force_authenticate(user=self.user_x)
        res = self.client.get(f'/api/chat/messages/?conversation_id={self.conv.id}')
        # Should return an empty list because the queryset strictly scopes to the user
        assert res.status_code == 200
        data = res.json()
        results = data.get('results', data) if isinstance(data, dict) else data
        assert len(results) == 0

    def test_idor_message_send(self):
        # User X tries to send a message into T and R's chat
        self.client.force_authenticate(user=self.user_x)
        res = self.client.post('/api/chat/messages/', {
            "conversation_id": str(self.conv.id),
            "content": "I am intercepting this chat."
        })
        assert res.status_code == 403

    def test_xss_protection_and_length(self):
        self.client.force_authenticate(user=self.user_t)
        
        # Test Empty
        res_empty = self.client.post('/api/chat/messages/', {"conversation_id": str(self.conv.id), "content": "   "})
        assert res_empty.status_code == 400
        
        # Test Too Long
        long_text = "A" * 2001
        res_long = self.client.post('/api/chat/messages/', {"conversation_id": str(self.conv.id), "content": long_text})
        assert res_long.status_code == 400

    def test_business_boundary_enforcement(self):
        self.client.force_authenticate(user=self.user_t)
        self.proposal.status = "REJECTED"
        self.proposal.save()

        res = self.client.post('/api/chat/conversations/get_or_create/', {
            "proposal_id": str(self.proposal.id)
        })
        assert res.status_code == 400
        assert "Chat is closed" in res.json()['detail']
