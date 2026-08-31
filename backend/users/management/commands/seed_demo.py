from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Profile
from travel.models import Location, TravelPost
from packages.models import PackageRequest
from proposals.models import Proposal
from payments.models import PaymentTransaction
from orders.models import Order
from reviews.models import Review
from disputes.models import Dispute
from verifications.models import UserVerification
from fraud.models import FraudFlag
from notifications.models import Notification
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds repeatable, deterministic development and demo data for TravelBridge.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🌱 Seeding TravelBridge demo database..."))

        # 1. Create Demo Users
        traveler_user, _ = User.objects.get_or_create(email="traveler@demo.com", defaults={'is_active': True})
        traveler_user.set_password("demo12345")
        traveler_user.save()
        Profile.objects.get_or_create(user=traveler_user, defaults={'role': 'TRAVELER', 'display_name': 'Demo Traveler', 'verification_status': 'VERIFIED'})

        requester_user, _ = User.objects.get_or_create(email="requester@demo.com", defaults={'is_active': True})
        requester_user.set_password("demo12345")
        requester_user.save()
        Profile.objects.get_or_create(user=requester_user, defaults={'role': 'REQUESTER', 'display_name': 'Demo Requester', 'verification_status': 'VERIFIED'})

        admin_user, _ = User.objects.get_or_create(email="admin@demo.com", defaults={'is_active': True, 'is_staff': True, 'is_superuser': True})
        admin_user.set_password("demo12345")
        admin_user.save()
        Profile.objects.get_or_create(user=admin_user, defaults={'role': 'BOTH', 'display_name': 'Demo Admin', 'verification_status': 'VERIFIED'})

        # 2. Create Locations
        loc_nyc, _ = Location.objects.get_or_create(city="New York", country="USA", country_code="US")
        loc_lon, _ = Location.objects.get_or_create(city="London", country="UK", country_code="GB")

        # 3. Create Travel Post & Package Request
        future_date = timezone.now() + timedelta(days=7)
        trip, _ = TravelPost.objects.get_or_create(
            traveler=traveler_user,
            origin=loc_nyc,
            destination=loc_lon,
            defaults={
                'departure_date': future_date,
                'capacity_kg': Decimal('15.00'),
                'status': 'PUBLISHED'
            }
        )

        package, _ = PackageRequest.objects.get_or_create(
            requester=requester_user,
            origin=loc_nyc,
            destination=loc_lon,
            defaults={
                'title': 'Demo Laptop Shipment',
                'required_delivery_date': future_date + timedelta(days=2),
                'weight_kg': Decimal('3.50'),
                'status': 'PUBLISHED'
            }
        )

        # 4. Create Proposal, Payment & Order
        proposal, _ = Proposal.objects.get_or_create(
            traveler=traveler_user,
            requester=requester_user,
            trip=trip,
            package_request=package,
            defaults={
                'proposed_price': Decimal('150.00'),
                'currency': 'INR',
                'status': 'ACCEPTED'
            }
        )

        payment, _ = PaymentTransaction.objects.get_or_create(
            proposal=proposal,
            defaults={
                'user': requester_user,
                'base_amount': Decimal('150.00'),
                'platform_fee': Decimal('7.50'),
                'total_amount': Decimal('157.50'),
                'currency': 'INR',
                'idempotency_key': 'seed_idempotency_key_001',
                'status': 'SUCCEEDED'
            }
        )

        order, _ = Order.objects.get_or_create(
            proposal=proposal,
            defaults={
                'traveler': traveler_user,
                'requester': requester_user,
                'payment': payment,
                'trip': trip,
                'package_request': package,
                'agreed_price': Decimal('150.00'),
                'currency': 'INR',
                'origin_city': loc_nyc.city,
                'destination_city': loc_lon.city,
                'package_weight_kg': Decimal('3.50'),
                'status': 'COMPLETED',
                'delivery_status': 'DELIVERED'
            }
        )

        # 5. Create Review, Dispute & Fraud Flag
        Review.objects.get_or_create(
            order=order,
            reviewer=requester_user,
            reviewee=traveler_user,
            defaults={'rating': 5, 'comment': 'Seamless delivery experience!'}
        )

        UserVerification.objects.get_or_create(
            user=traveler_user,
            defaults={'status': 'APPROVED', 'document': 'verifications/seed_doc.pdf'}
        )

        FraudFlag.objects.get_or_create(
            user=requester_user,
            reason="Demo risk flag for testing oversight.",
            defaults={'severity': 'LOW', 'status': 'OPEN'}
        )

        Notification.objects.get_or_create(
            recipient=traveler_user,
            event_type='ORDER_CONFIRMED',
            title='Demo Order Confirmed',
            defaults={'message': f'Order {order.reference_code} has been successfully secured.'}
        )

        self.stdout.write(self.style.SUCCESS("✅ Successfully seeded TravelBridge demo data!"))
