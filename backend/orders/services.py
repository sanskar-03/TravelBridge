from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from .models import Order
from payments.models import PaymentTransaction
from packages.models import PackageRequest

def create_order_from_payment(payment: PaymentTransaction) -> Order:
    """
    Creates the canonical Order record when a payment is successfully captured.
    Requires an atomic transaction context.
    """
    if payment.status != PaymentTransaction.Status.SUCCEEDED:
        raise ValidationError(_("Order can only be created from a succeeded payment."))
    
    if hasattr(payment, 'order'):
        return payment.order

    proposal = payment.proposal
    trip = proposal.trip
    pkg = proposal.package_request

    order = Order.objects.create(
        traveler=proposal.traveler,
        requester=proposal.requester,
        proposal=proposal,
        payment=payment,
        trip=trip,
        package_request=pkg,
        agreed_price=payment.base_amount,
        currency=payment.currency,
        origin_city=trip.origin.city,
        destination_city=trip.destination.city,
        package_weight_kg=pkg.weight_kg,
        status=Order.Status.CONFIRMED,
        delivery_status=Order.DeliveryStatus.PENDING
    )

    # Conceptual capacity subtraction (if exact capacity management is utilized)
    trip.capacity_kg -= pkg.weight_kg
    trip.save(update_fields=['capacity_kg'])

    pkg.status = PackageRequest.Status.MATCHED
    pkg.save(update_fields=['status'])

    return order

def transition_delivery_status(order: Order, user, action: str) -> Order:
    """
    Securely manages delivery state transitions based on roles.
    """
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)

        if order.status != Order.Status.CONFIRMED:
            raise ValidationError(_("Delivery actions require a CONFIRMED order."))

        if action == 'ready':
            if user != order.requester:
                raise ValidationError(_("Only the requester can mark ready for pickup."))
            if order.delivery_status != Order.DeliveryStatus.PENDING:
                raise ValidationError(_("Invalid transition to ready."))
            order.delivery_status = Order.DeliveryStatus.READY_FOR_PICKUP

        elif action == 'picked_up':
            if user != order.traveler:
                raise ValidationError(_("Only the traveler can confirm pickup."))
            if order.delivery_status != Order.DeliveryStatus.READY_FOR_PICKUP:
                raise ValidationError(_("Package must be ready for pickup first."))
            order.delivery_status = Order.DeliveryStatus.PICKED_UP

        elif action == 'in_transit':
            if user != order.traveler:
                raise ValidationError(_("Only the traveler can mark in transit."))
            if order.delivery_status != Order.DeliveryStatus.PICKED_UP:
                raise ValidationError(_("Package must be picked up first."))
            order.delivery_status = Order.DeliveryStatus.IN_TRANSIT

        elif action == 'delivered':
            if user != order.traveler:
                raise ValidationError(_("Only the traveler can mark delivered."))
            if order.delivery_status != Order.DeliveryStatus.IN_TRANSIT:
                raise ValidationError(_("Package must be in transit first."))
                
            # Proof of Delivery hard requirement
            if not hasattr(order, 'proof_of_delivery'):
                raise ValidationError(_("Proof of Delivery must be submitted before marking as delivered."))
                
            order.delivery_status = Order.DeliveryStatus.DELIVERED
            order.status = Order.Status.COMPLETED

        else:
            raise ValidationError(_("Invalid action."))

        order.save()
        return order
