import pytest
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from users.models import User, Profile
from travel.models import Location
from packages.models import PackageRequest

@pytest.mark.django_db
class TestPackageRequestSecurityAndLifecycle:
    def setup_method(self):
        self.client = APIClient()
        
        self.user_requester = User.objects.create_user(email="requester@travelbridge.test", password="password123")
        self.profile_r, _ = Profile.objects.get_or_create(user=self.user_requester, role="REQUESTER")
        
        self.user_traveler = User.objects.create_user(email="traveler@travelbridge.test", password="password123")
        self.profile_t, _ = Profile.objects.get_or_create(user=self.user_traveler, role="TRAVELER")

        self.loc_ny = Location.objects.create(city="New York", country="USA", country_code="US")
        self.loc_ldn = Location.objects.create(city="London", country="UK", country_code="GB")
        self.future_date = timezone.now() + timedelta(days=10)

    def test_requester_can_create_draft(self):
        self.client.force_authenticate(user=self.user_requester)
        response = self.client.post('/api/packages/requests/', {
            "origin_id": str(self.loc_ny.id),
            "destination_id": str(self.loc_ldn.id),
            "required_delivery_date": self.future_date.isoformat(),
            "weight_kg": "2.50",
            "title": "Important Documents",
            "description": "Legal papers, do not bend.",
            "category": "DOC"
        }, format='json')
        
        assert response.status_code == 201
        assert response.json()['status'] == 'DRAFT'
        assert response.json()['requester']['id'] == str(self.profile_r.id)

    def test_traveler_role_denied_package_creation(self):
        self.client.force_authenticate(user=self.user_traveler)
        response = self.client.post('/api/packages/requests/', {
            "origin_id": str(self.loc_ny.id),
            "destination_id": str(self.loc_ldn.id),
            "required_delivery_date": self.future_date.isoformat(),
            "weight_kg": "1.00",
            "title": "Test Item"
        }, format='json')
        assert response.status_code in (403, 400)

    def test_idor_protection_cannot_edit_others_request(self):
        pkg = PackageRequest.objects.create(
            requester=self.user_requester, origin=self.loc_ny, destination=self.loc_ldn,
            required_delivery_date=self.future_date, weight_kg=1.5, title="Test", status=PackageRequest.Status.PUBLISHED
        )
        self.client.force_authenticate(user=self.user_traveler)
        response = self.client.patch(f'/api/packages/requests/{pkg.id}/', {"weight_kg": "10.00"}, format='json')
        assert response.status_code in (403, 400)

    def test_state_transitions(self):
        pkg = PackageRequest.objects.create(
            requester=self.user_requester, origin=self.loc_ny, destination=self.loc_ldn,
            required_delivery_date=self.future_date, weight_kg=1.5, title="Test", status=PackageRequest.Status.DRAFT
        )
        self.client.force_authenticate(user=self.user_requester)
        
        res_pub = self.client.post(f'/api/packages/requests/{pkg.id}/publish/')
        assert res_pub.status_code == 200
        assert res_pub.json()['status'] == 'PUBLISHED'

        res_pause = self.client.post(f'/api/packages/requests/{pkg.id}/pause/')
        assert res_pause.status_code == 200
        assert res_pause.json()['status'] == 'PAUSED'
