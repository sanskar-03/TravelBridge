import pytest
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from users.models import User, Profile
from travel.models import Location, TravelPost
from packages.models import PackageRequest

@pytest.mark.django_db
class TestMatchingEngine:
    def setup_method(self):
        self.client = APIClient()
        
        self.user_r = User.objects.create_user(email="req@test.com", password="pwd")
        self.user_t = User.objects.create_user(email="trav@test.com", password="pwd")
        self.user_other = User.objects.create_user(email="other@test.com", password="pwd")
        
        self.loc_a = Location.objects.create(city="City A", country="USA", country_code="US")
        self.loc_b = Location.objects.create(city="City B", country="USA", country_code="US")
        self.loc_c = Location.objects.create(city="City C", country="USA", country_code="US")

        self.future_date = timezone.now() + timedelta(days=5)

        # Create the Package Request
        self.package = PackageRequest.objects.create(
            requester=self.user_r, origin=self.loc_a, destination=self.loc_b,
            required_delivery_date=self.future_date, weight_kg=5.0, status="PUBLISHED"
        )

    def test_idor_matching_access(self):
        # User Other attempts to get matches for User R's package
        self.client.force_authenticate(user=self.user_other)
        response = self.client.get(f'/api/packages/requests/{self.package.id}/matches/')
        assert response.status_code == 403

    def test_hard_constraints(self):
        # 1. Invalid Route (C -> B)
        TravelPost.objects.create(
            traveler=self.user_t, origin=self.loc_c, destination=self.loc_b,
            departure_date=self.future_date - timedelta(days=1), capacity_kg=10.0, status="PUBLISHED"
        )
        
        # 2. Invalid Capacity (Only 2kg available, 5kg needed)
        TravelPost.objects.create(
            traveler=self.user_t, origin=self.loc_a, destination=self.loc_b,
            departure_date=self.future_date - timedelta(days=1), capacity_kg=2.0, status="PUBLISHED"
        )

        # 3. Invalid Date (Departs after package is needed)
        TravelPost.objects.create(
            traveler=self.user_t, origin=self.loc_a, destination=self.loc_b,
            departure_date=self.future_date + timedelta(days=2), capacity_kg=10.0, status="PUBLISHED"
        )

        # 4. Valid Trip
        valid_trip = TravelPost.objects.create(
            traveler=self.user_t, origin=self.loc_a, destination=self.loc_b,
            departure_date=self.future_date - timedelta(days=1), capacity_kg=10.0, status="PUBLISHED"
        )

        self.client.force_authenticate(user=self.user_r)
        response = self.client.get(f'/api/packages/requests/{self.package.id}/matches/')
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only return the 1 valid trip
        assert len(data) == 1
        assert data[0]['trip']['id'] == str(valid_trip.id)
        assert data[0]['score'] >= 50
