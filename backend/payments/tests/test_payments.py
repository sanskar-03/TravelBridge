import pytest
import json
from rest_framework.test import APIClient
from decimal import Decimal
from django.utils import timezone
from users.models import User, Profile
from travel.models import Location, TravelPost
from packages.models import PackageRequest
from proposals.models import Proposal
from payments.models import PaymentTransaction

@pytest.mark.django_db
class TestPaymentSecurity:
    def setup_method(self):
        self.client = APIClient()
        self.user_r = User.objects.create_user(email="req@test.com", password="pwd")
        self.user_t = User.objects.create_user(email="trav@test.com", password="pwd")
        
        loc_a = Location.objects.create(city="City A", country_code="US")
        loc_b = Location.objects.create(city="City B", country_code="US")

        package = PackageRequest.objects.create(
            requester=self.user_r, origin=loc_a, destination=loc_b,
            required_delivery_date=timezone.now() + timezone.timedelta(days=5), 
            weight_kg=5.0, status="PUBLISHED"
        )
        trip = TravelPost.objects.create(
            traveler=self.user_t, origin=loc_a, destination=loc_b,
            departure_date=timezone.now() + timezone.timedelta(days=4), 
            capacity_kg=10.0, status="PUBLISHED"
        )
        self.proposal = Proposal.objects.create(
            traveler=self.user_t, requester=self.user_r, trip=trip, package_request=package,
            proposed_price=Decimal("100.00"), status="ACCEPTED"
        )

    def test_price_tampering_prevented(self):
        """
        Ensures the client cannot inject arbitrary amounts. The backend calculates pricing.
        """
        self.client.force_authenticate(user=self.user_r)
        
        # Malicious payload trying to pay 1.00 instead of 100.00
        res = self.client.post('/api/payments/checkout/', {
            "proposal_id": str(self.proposal.id),
            "total_amount": "1.00",
            "base_amount": "1.00",
            "platform_fee": "0.00",
            "currency": "USD"
        }, format='json')
        
        assert res.status_code == 201
        data = res.json()
        
        # Backend authority overrides malicious payload
        assert data['base_amount'] == "100.00"
        assert data['platform_fee'] == "5.00"
        assert data['total_amount'] == "105.00"
        assert data['currency'] == "INR"

    def test_idempotency_prevents_duplicate_orders(self):
        self.client.force_authenticate(user=self.user_r)
        
        res1 = self.client.post('/api/payments/checkout/', {
            "proposal_id": str(self.proposal.id)
        }, format='json')
        
        res2 = self.client.post('/api/payments/checkout/', {
            "proposal_id": str(self.proposal.id)
        }, format='json')
        
        # Both requests return 200/201, but ID is the exact same.
        assert res1.json()['id'] == res2.json()['id']
        assert PaymentTransaction.objects.count() == 1

    def test_webhook_signature_verification(self):
        # 1. Bypass signature flag (Mocking valid signature)
        res_ok = self.client.post('/api/payments/webhook/', json.dumps({
            "order_id": "fake_order",
            "status": "captured"
        }), content_type='application/json', HTTP_X_GATEWAY_SIGNATURE='test_bypass')
        assert res_ok.status_code == 404 # 404 because order doesn't exist, but signature passed

        # 2. Invalid signature
        res_fail = self.client.post('/api/payments/webhook/', json.dumps({
            "order_id": "fake_order",
            "status": "captured"
        }), content_type='application/json', HTTP_X_GATEWAY_SIGNATURE='invalid_sig')
        assert res_fail.status_code == 400
        assert res_fail.json()['detail'] == 'Invalid signature.'
