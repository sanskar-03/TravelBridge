from packages.models import PackageRequest
from packages.serializers import PublicPackageRequestSerializer

def find_matches_for_trip(trip):
    """
    Deterministic matching engine finding eligible packages for a traveler's trip.
    Applies strict ORM-level hard constraints before scoring.
    """
    if trip.status not in ['PUBLISHED', 'DRAFT']:
        return []

    # HARD CONSTRAINTS
    packages = PackageRequest.objects.filter(
        status=PackageRequest.Status.PUBLISHED,
        requester__is_active=True,
        origin=trip.origin,
        destination=trip.destination,
        required_delivery_date__gte=trip.departure_date,
        weight_kg__lte=trip.capacity_kg
    ).select_related('origin', 'destination', 'requester__profile')

    results = []
    for pkg in packages:
        score = 50
        reasons = [
            "Exact route match",
            f"Fits your available capacity ({pkg.weight_kg} kg)",
            "Delivery deadline is feasible"
        ]

        # SOFT SIGNALS
        if pkg.requester.is_email_verified:
            score += 20
            reasons.append("Verified Requester")

        if hasattr(pkg.requester, 'profile') and pkg.requester.profile.verification_status == 'VERIFIED':
            score += 15
            reasons.append("Identity Verified")

        time_diff = pkg.required_delivery_date - trip.departure_date
        days_diff = max(0, time_diff.days)
        if days_diff <= 2:
            score += 15
            reasons.append("Tight turnaround (Needs delivery shortly after you depart)")
        elif days_diff <= 7:
            score += 5
            reasons.append("Comfortable delivery window")

        results.append({
            "package": PublicPackageRequestSerializer(pkg).data,
            "score": min(100, score),
            "reasons": reasons
        })
        
    results.sort(key=lambda x: x['score'], reverse=True)
    return results
