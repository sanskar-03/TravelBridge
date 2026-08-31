import pytest
from rest_framework.test import APIClient
from users.models import User
from notifications.models import Notification
from notifications.services import create_system_notification

@pytest.mark.django_db
class TestNotificationSecurityAndAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user_a = User.objects.create_user(email="userA@test.com", password="pwd")
        self.user_b = User.objects.create_user(email="userB@test.com", password="pwd")

        self.notif_a = create_system_notification(
            recipient=self.user_a,
            event_type=Notification.EventType.SYSTEM_ALERT,
            title="Alert A",
            message="Test message for A"
        )
        self.notif_b = create_system_notification(
            recipient=self.user_b,
            event_type=Notification.EventType.SYSTEM_ALERT,
            title="Alert B",
            message="Test message for B"
        )

    def test_idor_protection_list(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get('/api/notifications/')
        assert res.status_code == 200
        data = res.json()
        # Safely handle both paginated and flat-list DRF responses
        results = data.get('results', data) if isinstance(data, dict) else data
        assert len(results) == 1
        assert results[0]['title'] == "Alert A" # Cannot see B's notification

    def test_idor_protection_mark_read(self):
        self.client.force_authenticate(user=self.user_a)
        # Attempt to mark User B's notification as read
        res = self.client.post(f'/api/notifications/{self.notif_b.id}/mark_read/')
        assert res.status_code == 404 # get_object() fails safely

    def test_unread_count_and_mark_all_read(self):
        self.client.force_authenticate(user=self.user_a)
        
        count_res = self.client.get('/api/notifications/unread_count/')
        assert count_res.json()['unread_count'] == 1
        
        mark_res = self.client.post('/api/notifications/mark_all_read/')
        assert mark_res.status_code == 200
        assert mark_res.json()['updated_count'] == 1
        
        count_res_2 = self.client.get('/api/notifications/unread_count/')
        assert count_res_2.json()['unread_count'] == 0

    def test_mass_assignment_protection(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.patch(f'/api/notifications/{self.notif_a.id}/', {
            "title": "Hacked Title",
            "message": "<script>alert('XSS')</script>"
        }, format='json')
        assert res.status_code == 405 # Method Not Allowed - ReadOnlyModelViewSet enforces this safely
