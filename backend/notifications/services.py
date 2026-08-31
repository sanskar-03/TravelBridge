from django.db import transaction
import logging
from .models import Notification

logger = logging.getLogger('travelbridge')

def _dispatch_delivery_channels(notification_id):
    """
    Simulates an asynchronous background worker (e.g., Celery).
    In production, this is where Email/Push delivery triggers.
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        # TODO: Trigger Email Service (AWS SES / SendGrid)
        # TODO: Trigger Push Service (FCM / APNs)
        logger.info(f"Asynchronously dispatched notification {notification_id} to {notification.recipient.email}")
    except Notification.DoesNotExist:
        pass

def create_system_notification(recipient, event_type, title, message, related_object_id=None):
    """
    Centralized event handler. Enforces idempotency and schedules external delivery
    only AFTER the primary database transaction commits successfully.
    """
    # Basic Idempotency: Prevent duplicate notifications for the exact same event/object within a short timeframe.
    if related_object_id:
        exists = Notification.objects.filter(
            recipient=recipient,
            event_type=event_type,
            related_object_id=str(related_object_id)
        ).exists()
        if exists and event_type not in ['DELIVERY_UPDATE']: 
            return None # Skip duplicate non-recurring events

    notification = Notification.objects.create(
        recipient=recipient,
        event_type=event_type,
        title=title,
        message=message,
        related_object_id=str(related_object_id) if related_object_id else None
    )

    # Schedule external delivery hooks to fire only if the DB transaction fully succeeds
    transaction.on_commit(lambda: _dispatch_delivery_channels(notification.id))
    
    return notification
