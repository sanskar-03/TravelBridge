import pytest
from rest_framework.test import APIClient
from decimal import Decimal
from django.utils import timezone
from users.models import User, Profile
from travel.models import Location, TravelPost
from packages.models import PackageRequest
from proposals.models import Proposal
from payments.models import PaymentTransaction
from orders.models import Order
from orders.services import create_order_from_payment

@pytest.mark.django_db
class TestOrderLifecycle:
    def setup_method(self):
        self.client = APIClient()
        self.user_r = User.objects.create_user(email="req@test.com", password="pwd")
        self.user_t = User.objects.create_user(email="trav@test.com", password="pwd")
        Profile.objects.create(user=self.user_r, role="REQUESTER")
        Profile.objects.create(user=self.user_t, role="TRAVELER")
        
        loc = Location.objects.create(city="City A", country_code="US")
        
        self.package = PackageRequest.objects.create(
            requester=self.user_r, origin=loc, destination=loc,
            required_delivery_date=timezone.now() + timezone.timedelta(days=5), weight_kg=5.0, status="PUBLISHED"
        )
        self.trip = TravelPost.objects.create(
            traveler=self.user_t, origin=loc, destination=loc,
            departure_date=timezone.now() + timezone.timedelta(days=4), capacity_kg=10.0, status="PUBLISHED"
        )
        self.proposal = Proposal.objects.create(
            traveler=self.user_t, requester=self.user_r, trip=self.trip, package_request=self.package,
            proposed_price=Decimal("100.00"), status="ACCEPTED"
        )
        self.payment = PaymentTransaction.objects.create(
            user=self.user_r, proposal=self.proposal, base_amount=Decimal("100.00"),
            platform_fee=Decimal("5.00"), total_amount=Decimal("105.00"),
            idempotency_key="test_key", status=PaymentTransaction.Status.SUCCEEDED
        )

    def test_order_creation_from_payment(self):
        order = create_order_from_payment(self.payment)
        assert order.status == 'CONFIRMED'
        assert order.delivery_status == 'PENDING'
        assert order.agreed_price == Decimal("100.00")
        assert order.package_weight_kg == Decimal("5.00")
        
        self.trip.refresh_from_db()
        assert self.trip.capacity_kg == Decimal("5.00") # 10.0 - 5.0 consumed

    def test_delivery_state_machine_security(self):
        order = create_order_from_payment(self.payment)
        
        # Traveler cannot mark ready
        self.client.force_authenticate(user=self.user_t)
        res = self.client.post(f'/api/orders/{order.id}/mark_ready/')
        assert res.status_code == 400
        
        # Requester marks ready
        self.client.force_authenticate(user=self.user_r)
        res = self.client.post(f'/api/orders/{order.id}/mark_ready/')
        assert res.status_code == 200
        assert res.json()['delivery_status'] == 'READY_FOR_PICKUP'
        
        # Traveler marks picked up
        self.client.force_authenticate(user=self.user_t)
        res = self.client.post(f'/api/orders/{order.id}/mark_picked_up/')
        assert res.status_code == 200
        assert res.json()['delivery_status'] == 'PICKED_UP'
