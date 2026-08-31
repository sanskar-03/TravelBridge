from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from .models import FraudFlag
from orders.models import Order
from packages.models import PackageRequest

def evaluate_user_risk(user) -> str:
    """
    Deterministic risk-scoring evaluation based on user activity rules.
    """
    risk_score = 0
    reasons = []

    # Rule 1: Account age check (< 24 hours)
    if user.created_at and (timezone.now() - user.created_at) < timedelta(hours=24):
        risk_score += 30
        reasons.append("New account activity (< 24 hours)")

    # Rule 2: Excessive active package requests
    active_requests_count = PackageRequest.objects.filter(requester=user, status='PUBLISHED').count()
    if active_requests_count > 5:
        risk_score += 40
        reasons.append("Unusually high volume of active package requests")

    # Rule 3: Dispute history check
    disputes_count = getattr(user, 'disputes_opened', None)
    if disputes_count and disputes_count.count() >= 2:
        risk_score += 50
        reasons.append("Multiple disputes opened")

    # Determine Severity Level
    if risk_score >= 70:
        severity = FraudFlag.Severity.CRITICAL
    elif risk_score >= 50:
        severity = FraudFlag.Severity.HIGH
    elif risk_score >= 30:
        severity = FraudFlag.Severity.MEDIUM
    else:
        severity = FraudFlag.Severity.LOW

    if risk_score >= 30:
        # Automatically persist or update open flag if high enough
        FraudFlag.objects.get_or_create(
            user=user,
            status=FraudFlag.Status.OPEN,
            defaults={
                'severity': severity,
                'reason': "; ".join(reasons),
                'metadata': {'score': risk_score}
            }
        )

    return severity
