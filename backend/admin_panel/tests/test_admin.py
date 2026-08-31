import pytest
from rest_framework.test import APIClient
from users.models import User
from verifications.models import UserVerification
from fraud.models import FraudFlag
from admin_panel.models import AdminActionAudit

@pytest.mark.django_db
class TestAdminControls:
    def setup_method(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(email="admin@test.com", password="pwd", is_staff=True, is_superuser=True)
        self.normal_user = User.objects.create_user(email="user@test.com", password="pwd")
        self.verification = UserVerification.objects.create(user=self.normal_user, status="PENDING")

    def test_normal_user_blocked_from_admin(self):
        self.client.force_authenticate(user=self.normal_user)
        res = self.client.get('/api/v1/admin/dashboard/overview/')
        assert res.status_code == 403

    def test_admin_can_access_overview(self):
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get('/api/v1/admin/dashboard/overview/')
        assert res.status_code == 200
        assert "total_users" in res.json()

    def test_admin_suspension_creates_audit_log(self):
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.post(f'/api/v1/admin/users/{self.normal_user.id}/suspend/', {"reason": "Violation"}, format='json')
        assert res.status_code == 200
        
        self.normal_user.refresh_from_db()
        assert self.normal_user.is_active is False
        assert AdminActionAudit.objects.filter(action="USER_SUSPENDED").exists()
