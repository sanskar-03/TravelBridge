from django.db.models.signals import post_save
from django.dispatch import receiver
from proposals.models import Proposal
from orders.models import Order
from .services import create_system_notification

@receiver(post_save, sender=Proposal)
def handle_proposal_events(sender, instance, created, **kwargs):
    """
    Listens for Proposal state changes to trigger notifications dynamically.
    """
    if instance.status == Proposal.Status.ACCEPTED:
        create_system_notification(
            recipient=instance.traveler,
            event_type=Notification.EventType.PROPOSAL_ACCEPTED,
            title="Proposal Accepted!",
            message=f"Your proposal for {instance.trip.origin.city} to {instance.trip.destination.city} was accepted.",
            related_object_id=instance.id
        )

@receiver(post_save, sender=Order)
def handle_order_events(sender, instance, created, **kwargs):
    """
    Listens for Order/Delivery lifecycle changes.
    """
    if created:
        create_system_notification(
            recipient=instance.traveler,
            event_type=Notification.EventType.ORDER_CONFIRMED,
            title="Order Confirmed",
            message=f"Order {instance.reference_code} has been successfully secured and payment captured.",
            related_object_id=instance.id
        )
        create_system_notification(
            recipient=instance.requester,
            event_type=Notification.EventType.ORDER_CONFIRMED,
            title="Order Confirmed",
            message=f"Your package order {instance.reference_code} is confirmed.",
            related_object_id=instance.id
        )
    else:
        # If delivery status changed (simplified trigger)
        create_system_notification(
            recipient=instance.requester,
            event_type=Notification.EventType.DELIVERY_UPDATE,
            title="Delivery Status Updated",
            message=f"Order {instance.reference_code} is now: {instance.delivery_status.replace('_', ' ')}.",
            related_object_id=instance.id
        )
from .models import Notification
