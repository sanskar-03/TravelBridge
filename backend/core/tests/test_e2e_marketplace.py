import pytest
from rest_framework.test import APIClient
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from users.models import User, Profile
from travel.models import Location, TravelPost
from packages.models import PackageRequest
from proposals.models import Proposal
from payments.models import PaymentTransaction
from orders.models import Order
from tracking.models import ProofOfDelivery
from reviews.models import Review

@pytest.mark.django_db
class TestCompleteMarketplaceE2E:
    def setup_method(self):
        self.client = APIClient()
        self.traveler = User.objects.create_user(email="trav_e2e@test.com", password="pwd")
        self.requester = User.objects.create_user(email="req_e2e@test.com", password="pwd")
        Profile.objects.create(user=self.traveler, role="TRAVELER")
        Profile.objects.create(user=self.requester, role="REQUESTER")

        self.loc_origin = Location.objects.create(city="New York", country_code="US")
        self.loc_dest = Location.objects.create(city="London", country_code="GB")

        future_date = timezone.now() + timedelta(days=7)
        self.trip = TravelPost.objects.create(
            traveler=self.traveler,
            origin=self.loc_origin,
            destination=self.loc_dest,
            departure_date=future_date,
            capacity_kg=Decimal('15.00'),
            status='PUBLISHED'
        )

        self.package = PackageRequest.objects.create(
            requester=self.requester,
            origin=self.loc_origin,
            destination=self.loc_dest,
            title='E2E Test Package',
            category='DOC',
            description='Fragile items for testing',
            required_delivery_date=future_date + timedelta(days=2),
            weight_kg=Decimal('3.50'),
            status='PUBLISHED'
        )

    def test_full_marketplace_lifecycle_flow(self):
        # 1. Traveler creates proposal via API
        self.client.force_authenticate(user=self.traveler)
        prop_res = self.client.post('/api/proposals/', {
            "trip": str(self.trip.id),
            "package_request": str(self.package.id),
            "proposed_price": "80.00",
            "traveler_notes": "I can take this."
        }, format='json')
        assert prop_res.status_code == 201
        prop_id = prop_res.json()['id']

        # 2. Requester accepts proposal
        self.client.force_authenticate(user=self.requester)
        accept_res = self.client.post(f'/api/proposals/{prop_id}/accept/')
        assert accept_res.status_code == 200

        # 3. Requester initiates checkout/payment
        pay_res = self.client.post('/api/payments/checkout/', {
            "proposal_id": prop_id
        }, format='json')
        assert pay_res.status_code == 201
        order_id = pay_res.json()['gateway_order_id']

        # Simulate webhook capture
        webhook_res = self.client.post('/api/payments/webhook/', {
            "order_id": order_id,
            "status": "captured",
            "payment_id": "pay_mock_123"
        }, format='json', HTTP_X_GATEWAY_SIGNATURE='test_bypass')
        assert webhook_res.status_code == 200

        # 4. Verify Order is CONFIRMED
        orders_res = self.client.get('/api/orders/')
        assert orders_res.status_code == 200
        orders_data = orders_res.json()
        orders_list = orders_data.get('results', orders_data) if isinstance(orders_data, dict) else orders_data
        order_uuid = orders_list[0]['id']
        assert orders_list[0]['status'] == 'CONFIRMED'

        # 5. Complete delivery workflow & create POD directly via ORM to satisfy delivery constraint cleanly
        order_obj = Order.objects.get(id=order_uuid)
        order_obj.delivery_status = 'IN_TRANSIT'
        order_obj.save()

        from django.core.files.uploadedfile import SimpleUploadedFile
        good_file = SimpleUploadedFile("pod.jpg", b"fake image data", content_type="image/jpeg")
        ProofOfDelivery.objects.create(order=order_obj, submitted_by=self.traveler, image=good_file, notes="Delivered successfully")

        self.client.force_authenticate(user=self.traveler)
        del_res = self.client.post(f'/api/orders/{order_uuid}/mark_delivered/')
        assert del_res.status_code == 200

        # 6. Submit Review
        self.client.force_authenticate(user=self.requester)
        review_res = self.client.post('/api/reviews/', {
            "order": order_uuid,
            "rating": 5,
            "comment": "Perfect end-to-end execution!"
        }, format='json')
        assert review_res.status_code == 201
        assert review_res.json()['rating'] == 5
