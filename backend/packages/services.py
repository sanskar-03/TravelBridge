from travel.models import TravelPost
from travel.serializers import PublicTravelPostSerializer

def find_matches_for_package(package_req):
    """
    Deterministic matching engine finding eligible trips for a package request.
    Applies strict ORM-level hard constraints before scoring.
    """
    if package_req.status not in ['PUBLISHED', 'DRAFT']:
        return []

    # HARD CONSTRAINTS
    trips = TravelPost.objects.filter(
        status=TravelPost.Status.PUBLISHED,
        traveler__is_active=True,
        origin=package_req.origin,
        destination=package_req.destination,
        departure_date__lte=package_req.required_delivery_date,
        capacity_kg__gte=package_req.weight_kg
    ).select_related('origin', 'destination', 'traveler__profile')

    results = []
    for trip in trips:
        score = 50  # Base compatibility score
        reasons = [
            "Exact route match",
            f"Sufficient capacity ({trip.capacity_kg} kg available)",
            "Departure fits your delivery deadline"
        ]

        # SOFT SIGNALS (Ranking)
        if trip.traveler.is_email_verified:
            score += 20
            reasons.append("Verified Traveler")
        
        if hasattr(trip.traveler, 'profile') and trip.traveler.profile.verification_status == 'VERIFIED':
            score += 15
            reasons.append("Identity Verified")

        # Date Proximity Signal
        time_diff = package_req.required_delivery_date - trip.departure_date
        days_diff = max(0, time_diff.days)
        if days_diff <= 2:
            score += 15
            reasons.append("Excellent timing (Arrives shortly before deadline)")
        elif days_diff <= 7:
            score += 5
            reasons.append("Comfortable timeline")

        results.append({
            "trip": PublicTravelPostSerializer(trip).data,
            "score": min(100, score),
            "reasons": reasons
        })

    # Sort best matches first
    results.sort(key=lambda x: x['score'], reverse=True)
    return results
