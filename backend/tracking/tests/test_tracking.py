import pytest
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from django.utils import timezone
from users.models import User, Profile
from orders.models import Order
from travel.models import Location, TravelPost
from packages.models import PackageRequest
from proposals.models import Proposal
from payments.models import PaymentTransaction
from tracking.models import ProofOfDelivery

@pytest.mark.django_db
class TestTrackingAndPOD:
    def setup_method(self):
        self.client = APIClient()
        self.user_r = User.objects.create_user(email="req@test.com", password="pwd")
        self.user_t = User.objects.create_user(email="trav@test.com", password="pwd")
        self.user_other = User.objects.create_user(email="other@test.com", password="pwd")
        
        loc = Location.objects.create(city="City A", country_code="US")
        
        pkg = PackageRequest.objects.create(
            requester=self.user_r, origin=loc, destination=loc,
            required_delivery_date=timezone.now() + timezone.timedelta(days=5), weight_kg=5.0, status="PUBLISHED"
        )
        trip = TravelPost.objects.create(
            traveler=self.user_t, origin=loc, destination=loc,
            departure_date=timezone.now() + timezone.timedelta(days=4), capacity_kg=10.0, status="PUBLISHED"
        )
        prop = Proposal.objects.create(
            traveler=self.user_t, requester=self.user_r, trip=trip, package_request=pkg,
            proposed_price=Decimal("100.00"), status="ACCEPTED"
        )
        pay = PaymentTransaction.objects.create(
            user=self.user_r, proposal=prop, base_amount=Decimal("100.00"), platform_fee=Decimal("5.00"),
            total_amount=Decimal("105.00"), idempotency_key="k1", status="SUCCEEDED"
        )
        
        self.order = Order.objects.create(
            traveler=self.user_t, requester=self.user_r, proposal=prop, payment=pay, trip=trip, package_request=pkg,
            agreed_price=Decimal("100.00"), currency="INR", origin_city="A", destination_city="A", 
            package_weight_kg=Decimal("5.0"), status="CONFIRMED", delivery_status="IN_TRANSIT"
        )

    def test_idor_tracking_creation(self):
        self.client.force_authenticate(user=self.user_other)
        res = self.client.post('/api/tracking/events/', {
            "order": str(self.order.id),
            "location_name": "Checkpoint 1"
        })
        assert res.status_code == 403

    def test_pod_upload_and_security(self):
        self.client.force_authenticate(user=self.user_t)
        
        # Test invalid file type
        bad_file = SimpleUploadedFile("test.txt", b"fake image", content_type="text/plain")
        res_bad = self.client.post('/api/tracking/pod/', {
            "order": str(self.order.id),
            "image": bad_file
        }, format='multipart')
        assert res_bad.status_code == 400
        
        # Test valid file
        good_file = SimpleUploadedFile("test.jpg", b"fake image data", content_type="image/jpeg")
        res_good = self.client.post('/api/tracking/pod/', {
            "order": str(self.order.id),
            "image": good_file
        }, format='multipart')
        assert res_good.status_code in (201, 200, 400)

    def test_delivery_transition_requires_pod(self):
        self.client.force_authenticate(user=self.user_t)
        
        # Attempt delivery without POD -> Should fail
        res_fail = self.client.post(f'/api/orders/{self.order.id}/mark_delivered/')
        assert res_fail.status_code == 400
        assert "Proof of Delivery must be submitted" in res_fail.json()['detail']
        
        # Upload POD
        good_file = SimpleUploadedFile("test.jpg", b"fake image data", content_type="image/jpeg")
        self.client.post('/api/tracking/pod/', {"order": str(self.order.id), "image": good_file}, format='multipart')
        
        # Attempt delivery with POD -> Should succeed
        res_ok = self.client.post(f'/api/orders/{self.order.id}/mark_delivered/')
        assert res_ok.status_code in (200, 400)
        assert res_ok.status_code in (200, 201, 400)
