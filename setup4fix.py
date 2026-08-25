import os
from pathlib import Path

def fix_django_logging():
    settings_path = Path("backend/travelbridge/settings.py")
    
    logging_config = """
# ==========================================
# DEVELOPMENT LOGGING
# ==========================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO' if not DEBUG else 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'travelbridge': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
"""
    if settings_path.exists():
        # Check if LOGGING is already in the file to prevent duplicates
        with open(settings_path, 'r', encoding='utf-8') as f:
            if 'LOGGING =' in f.read():
                print(f"⚠️ LOGGING already exists in {settings_path}. Skipping.")
                return

        with open(settings_path, 'a', encoding='utf-8') as f:
            f.write(logging_config)
        print(f"✅ Added LOGGING configuration to {settings_path}")
    else:
        print(f"❌ Could not find {settings_path}")


def fix_handoff_state():
    handoff_path = Path("HANDOFF_STATE.md")
    
    part4_handoff = """
# Part 04 Handoff

## Infrastructure Completed
Hardened the local development environment ensuring stable, reproducible infrastructure using Docker. Implemented correct volume mounts, health checks, network segregation, and base security rules.

## Docker Services
* db: PostgreSQL 15 (alpine)
* redis: Redis 7 (alpine)
* backend: Django development server
* frontend: Next.js development server

## PostgreSQL
Configured via environment variables with a persistent volume and an active health check via pg_isready.

## Redis
Configured with a persistent volume and an active health check via redis-cli ping.

## Backend
Updated settings.py for CORS constraints, static/media pathing, timezone (UTC), and added structured development logging. Bound dependencies safely and utilized netcat in entrypoint.sh for database availability.

## Frontend
Starts reliably via Docker, connects to the backend through explicit host configurations, and leverages host mounts for hot-reloading.

## Security Review
* .env properly ignored in multiple .dockerignore contexts.
* Allowed hosts and CORS origins restricted.

## Next Part
PART 05 — Django Foundation, Core Models & Database Architecture
"""
    if handoff_path.exists():
        # Using 'a' (append) instead of 'w' (write/overwrite) to preserve history!
        with open(handoff_path, 'a', encoding='utf-8') as f:
            f.write(part4_handoff)
        print(f"✅ Appended Part 04 to {handoff_path} (History preserved!)")
    else:
        print(f"❌ Could not find {handoff_path}")

if __name__ == "__main__":
    print("🚀 Applying Part 04 Fixes...\n")
    fix_django_logging()
    fix_handoff_state()
    print("\n✅ Fixes applied successfully!")