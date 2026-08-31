import pytest
from rest_framework.test import APIClient
from users.models import User, Profile

@pytest.mark.django_db
class TestProfileSecurityAndAPI:
    
    def setup_method(self):
        self.client = APIClient()
        self.user_a = User.objects.create_user(email="usera@travelbridge.test", password="password123")
        self.profile_a, _ = Profile.objects.get_or_create(user=self.user_a)
        
        self.user_b = User.objects.create_user(email="userb@travelbridge.test", password="password123")
        self.profile_b, _ = Profile.objects.get_or_create(user=self.user_b)

    def test_unauthenticated_profile_access_rejected(self):
        response = self.client.get('/api/users/profile/')
        assert response.status_code in (401, 403)

    def test_authenticated_user_can_read_own_profile(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get('/api/users/profile/')
        assert response.status_code == 200
        assert response.json()['email'] == "usera@travelbridge.test"

    def test_authenticated_user_can_update_own_profile(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.patch('/api/users/profile/', {
            "display_name": "Traveler Alice",
            "bio": "Frequent flyer and enthusiast."
        }, format='json')
        assert response.status_code == 200
        assert response.json()['display_name'] == "Traveler Alice"
        assert response.json()['completion_percentage'] > 0

    def test_mass_assignment_protection_role_and_verification(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.patch('/api/users/profile/', {
            "verification_status": "VERIFIED",
            "role": "ADMIN"
        }, format='json')
        assert response.status_code == 400

        response2 = self.client.patch('/api/users/profile/', {
            "verification_status": "VERIFIED",
            "role": "TRAVELER"
        }, format='json')
        assert response2.status_code == 200
        self.profile_a.refresh_from_db()
        assert self.profile_a.verification_status == "UNVERIFIED"
        assert self.profile_a.role == "TRAVELER"

    def test_public_profile_hides_private_data(self):
        response = self.client.get(f'/api/users/profile/{self.profile_a.id}/')
        assert response.status_code == 200
        data = response.json()
        assert 'email' not in data
        assert 'phone_number' not in data
        assert 'email_notifications' not in data
