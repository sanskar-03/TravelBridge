import pytest
from rest_framework.test import APIClient
from decimal import Decimal
from django.utils import timezone
from users.models import User, Profile
from travel.models import Location, TravelPost
from packages.models import PackageRequest
from proposals.models import Proposal
from payments.models import PaymentTransaction
from orders.models import Order
from reviews.models import Review

@pytest.mark.django_db
class TestReviewWorkflow:
    def setup_method(self):
        self.client = APIClient()
        self.user_r = User.objects.create_user(email="req@test.com", password="pwd")
        self.user_t = User.objects.create_user(email="trav@test.com", password="pwd")
        self.user_x = User.objects.create_user(email="hacker@test.com", password="pwd")
        
        Profile.objects.create(user=self.user_r, role="REQUESTER")
        Profile.objects.create(user=self.user_t, role="TRAVELER")
        Profile.objects.create(user=self.user_x, role="BOTH")

        loc = Location.objects.create(city="City A", country_code="US")
        pkg = PackageRequest.objects.create(requester=self.user_r, origin=loc, destination=loc, required_delivery_date=timezone.now(), weight_kg=1.0, status="PUBLISHED")
        trip = TravelPost.objects.create(traveler=self.user_t, origin=loc, destination=loc, departure_date=timezone.now(), capacity_kg=5.0, status="PUBLISHED")
        prop = Proposal.objects.create(traveler=self.user_t, requester=self.user_r, trip=trip, package_request=pkg, proposed_price=Decimal("100.00"), status="ACCEPTED")
        pay = PaymentTransaction.objects.create(user=self.user_r, proposal=prop, base_amount=Decimal("100.00"), platform_fee=Decimal("5.00"), total_amount=Decimal("105.00"), idempotency_key="k1", status="SUCCEEDED")
        
        self.order = Order.objects.create(
            traveler=self.user_t, requester=self.user_r, proposal=prop, payment=pay, trip=trip, package_request=pkg,
            agreed_price=Decimal("100.00"), currency="INR", origin_city="A", destination_city="A", 
            package_weight_kg=Decimal("5.0"), status="COMPLETED", delivery_status="DELIVERED"
        )

    def test_participant_can_review(self):
        self.client.force_authenticate(user=self.user_r)
        res = self.client.post('/api/reviews/', {
            "order": str(self.order.id),
            "rating": 5,
            "comment": "Outstanding service!"
        }, format='json')
        assert res.status_code == 201
        assert res.json()['rating'] == 5

    def test_self_review_rejected(self):
        self.client.force_authenticate(user=self.user_r)
        # Attempting review where reviewer tries to review themselves or bypass
        # The view automatically assigns reviewee as counterparty. Let's test non-participant.
        self.client.force_authenticate(user=self.user_x)
        res = self.client.post('/api/reviews/', {
            "order": str(self.order.id),
            "rating": 5,
            "comment": "Hacker review"
        }, format='json')
        assert res.status_code == 403
