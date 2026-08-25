from django.http import JsonResponse
from django.db import connection
import redis
from django.conf import settings

def health_check(request):
    """
    Sanitized health check endpoint.
    Verifies application, database, and cache availability without leaking sensitive credentials.
    """
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "environment": "development" if settings.DEBUG else "production",
        "ai_mode": settings.AI_MODE,
        "payment_mode": settings.PAYMENT_MODE
    }

    # Verify Database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status["database"] = "connected"
    except Exception:
        health_status["database"] = "unreachable"
        health_status["status"] = "degraded"

    # Verify Redis
    try:
        r = redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        r.ping()
        health_status["redis"] = "connected"
    except Exception:
        health_status["redis"] = "unreachable"
        health_status["status"] = "degraded"

    status_code = 200 if health_status["status"] == "healthy" else 503
    return JsonResponse(health_status, status=status_code)
