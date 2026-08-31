import pytest
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from users.models import User, Profile
from travel.models import Location, TravelPost

@pytest.mark.django_db
class TestTripSecurityAndLifecycle:

    def setup_method(self):
        self.client = APIClient()
        self.user_a = User.objects.create_user(email="travelera@travelbridge.test", password="password123")
        self.profile_a, _ = Profile.objects.get_or_create(user=self.user_a, role="TRAVELER")
        
        self.user_b = User.objects.create_user(email="requesterb@travelbridge.test", password="password123")
        self.profile_b, _ = Profile.objects.get_or_create(user=self.user_b, role="REQUESTER")

        self.loc_chennai = Location.objects.create(city="Chennai", country="India", country_code="IN")
        self.loc_blr = Location.objects.create(city="Bengaluru", country="India", country_code="IN")
        self.future_date = timezone.now() + timedelta(days=5)

    def test_traveler_can_create_trip_draft(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.post('/api/travel/trips/', {
            "origin_id": str(self.loc_chennai.id),
            "destination_id": str(self.loc_blr.id),
            "departure_date": self.future_date.isoformat(),
            "capacity_kg": "5.00",
            "notes": "Fragile items welcome."
        }, format='json')
        
        assert response.status_code == 201
        data = response.json()
        assert data['status'] == 'DRAFT'
        assert data['traveler']['id'] == str(self.profile_a.id)

    def test_requester_role_denied_trip_creation(self):
        self.client.force_authenticate(user=self.user_b)
        response = self.client.post('/api/travel/trips/', {
            "origin_id": str(self.loc_chennai.id),
            "destination_id": str(self.loc_blr.id),
            "departure_date": self.future_date.isoformat(),
            "capacity_kg": "5.00"
        }, format='json')
        assert response.status_code == 403

    def test_idor_protection_cannot_edit_others_trip(self):
        trip = TravelPost.objects.create(
            traveler=self.user_a, origin=self.loc_chennai, destination=self.loc_blr,
            departure_date=self.future_date, capacity_kg=3.50, status=TravelPost.Status.PUBLISHED
        )
        self.client.force_authenticate(user=self.user_b)
        response = self.client.patch(f'/api/travel/trips/{trip.id}/', {"capacity_kg": "10.00"}, format='json')
        assert response.status_code == 403
