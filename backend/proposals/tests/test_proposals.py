import pytest
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from users.models import User, Profile
from travel.models import Location, TravelPost
from packages.models import PackageRequest
from proposals.models import Proposal

@pytest.mark.django_db
class TestProposalWorkflow:
    def setup_method(self):
        self.client = APIClient()
        self.user_r = User.objects.create_user(email="requester@test.com", password="pwd")
        self.user_t = User.objects.create_user(email="traveler@test.com", password="pwd")
        self.user_other = User.objects.create_user(email="other@test.com", password="pwd")
        
        self.loc_a = Location.objects.create(city="City A", country="USA", country_code="US")
        self.loc_b = Location.objects.create(city="City B", country="USA", country_code="US")
        self.future_date = timezone.now() + timedelta(days=5)

        self.package = PackageRequest.objects.create(
            requester=self.user_r, origin=self.loc_a, destination=self.loc_b,
            required_delivery_date=self.future_date, weight_kg=5.0, status="PUBLISHED"
        )
        self.trip = TravelPost.objects.create(
            traveler=self.user_t, origin=self.loc_a, destination=self.loc_b,
            departure_date=self.future_date - timedelta(days=1), capacity_kg=10.0, status="PUBLISHED"
        )

    def test_traveler_can_propose(self):
        self.client.force_authenticate(user=self.user_t)
        res = self.client.post('/api/proposals/', {
            "trip": str(self.trip.id),
            "package_request": str(self.package.id),
            "proposed_price": "50.00",
            "traveler_notes": "I can pick it up today."
        }, format='json')
        assert res.status_code == 201
        assert res.json()['status'] == 'PENDING'

    def test_self_dealing_rejected(self):
        # Make the traveler own the package
        self.package.requester = self.user_t
        self.package.save()
        
        self.client.force_authenticate(user=self.user_t)
        res = self.client.post('/api/proposals/', {
            "trip": str(self.trip.id),
            "package_request": str(self.package.id),
            "proposed_price": "50.00"
        }, format='json')
        assert res.status_code == 403

    def test_requester_can_accept_and_idor_protection(self):
        proposal = Proposal.objects.create(
            traveler=self.user_t, requester=self.user_r, trip=self.trip,
            package_request=self.package, proposed_price="50.00", status="PENDING"
        )
        
        # User Other tries to accept
        self.client.force_authenticate(user=self.user_other)
        res_fail = self.client.post(f'/api/proposals/{proposal.id}/accept/')
        assert res_fail.status_code == 403

        # Requester accepts
        self.client.force_authenticate(user=self.user_r)
        res_ok = self.client.post(f'/api/proposals/{proposal.id}/accept/')
        assert res_ok.status_code == 200
        assert res_ok.json()['status'] == 'ACCEPTED'
