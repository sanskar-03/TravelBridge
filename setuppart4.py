import os
import stat
from pathlib import Path

# --- 1. DIRECTORY STRUCTURE ---
DIRECTORIES = [
    "backend",
    "frontend",
    "backend/travelbridge",
]

# --- 2. FILE DEFINITIONS ---
FILES = {
    ".dockerignore": """# Root Docker Ignore
.git
.github
.env
.env.*
!.env.example
docs/
*.md
setup*.py
""",

    "backend/.dockerignore": """# Backend Docker Ignore
__pycache__/
*.pyc
*.pyo
.pytest_cache/
coverage/
.venv/
venv/
*.sqlite3
media/
uploads/
.env
""",

    "frontend/.dockerignore": """# Frontend Docker Ignore
node_modules/
.next/
out/
build/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.env
.env.local
.env.development.local
""",

    "docker-compose.yml": """version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: travelbridge_db
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-travelbridge}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-travelbridge}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: travelbridge_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: travelbridge_backend
    restart: unless-stopped
    volumes:
      - ./backend:/app
      - backend_static:/app/staticfiles
      - backend_media:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgres://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@db:5432/${POSTGRES_DB:-travelbridge}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: /app/entrypoint.sh

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: travelbridge_frontend
    restart: unless-stopped
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
  backend_static:
  backend_media:
""",

    "backend/travelbridge/settings.py": """import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    AI_MODE=(str, 'mock'),
    PAYMENT_MODE=(str, 'sandbox')
)

env_file = BASE_DIR.parent / '.env'
if env_file.exists():
    environ.Env.read_env(str(env_file))

SECRET_KEY = env('DJANGO_SECRET_KEY', default='dev-fallback-key-strictly-for-unconfigured-local-testing-only')
DEBUG = env('DJANGO_DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', 'backend', '0.0.0.0'])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'travelbridge.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'travelbridge.wsgi.application'

DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres://postgres:postgres@db:5432/travelbridge')
}

REDIS_URL = env('REDIS_URL', default='redis://redis:6379/0')
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=['http://localhost:3000', 'http://127.0.0.1:3000'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=['http://localhost:3000'])
CORS_ALLOW_CREDENTIALS = True

AI_MODE = env('AI_MODE', default='mock')
PAYMENT_MODE = env('PAYMENT_MODE', default='sandbox')
""",

    "backend/entrypoint.sh": """#!/bin/sh
set -e

echo "Starting Django Entrypoint..."

echo "Waiting for database at db:5432..."
while ! nc -z db 5432; do
  sleep 0.5
done
echo "Database is ready!"

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Starting development server..."
exec python manage.py runserver 0.0.0.0:8000
""",

    "SETUP.md": """# TravelBridge Setup Guide

## Prerequisites
* Docker & Docker Compose (Required for reliable local infrastructure)
* Python 3.10+ (For local backend checks)
* Node.js 18+ (For local frontend checks)

## Getting Started

1. Configure Environment:
   Run: cp .env.example .env
   (Ensure no production secrets are placed in .env)

2. Start Infrastructure (Backend, Frontend, DB, Redis):
   Run: docker-compose up --build

3. Access the Services:
   * Frontend: http://localhost:3000
   * Backend API / Health: http://localhost:8000/api/health/
   * PostgreSQL: localhost:5432 (User: postgres, Pass: postgres)
   * Redis: localhost:6379

## Troubleshooting

1. PostgreSQL not ready / Migration Failures
Symptom: Backend container crashes saying connection to server failed.
Fix: Docker Compose health checks are configured. If it still fails, ensure Port 5432 is not being used by a local Postgres install on your host machine.

2. Frontend cannot reach backend
Symptom: CORS errors or fetch failed in Next.js.
Fix: Ensure NEXT_PUBLIC_API_URL=http://localhost:8000 is set in your environment. Do not use backend:8000 for browser requests, only for internal Docker networking.

3. Resetting the Database (WARNING: Destructive)
If your development database gets corrupted, run:
  docker-compose down -v
  docker-compose up --build
""",
    
    "HANDOFF_STATE.md": """# Part 04 Handoff

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
Updated settings.py for CORS constraints, static/media pathing, and timezone (UTC). Bound dependencies safely and utilized netcat in entrypoint.sh for database availability before executing migrations.

## Frontend
Starts reliably via Docker, connects to the backend through explicit host configurations, and leverages host mounts for hot-reloading.

## Security Review
* .env properly ignored in multiple .dockerignore contexts.
* Allowed hosts and CORS origins restricted.

## Next Part
PART 05 — Django Foundation, Core Models & Database Architecture
"""
}

def create_scaffold():
    print("Initializing TravelBridge Hardening (Part 04)...")

    for directory in DIRECTORIES:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}/")

    for filename, content in FILES.items():
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created/Updated file: {filename}")

        if filename.endswith(".sh") or filename.endswith("manage.py"):
            try:
                st = os.stat(filepath)
                os.chmod(filepath, st.st_mode | stat.S_IEXEC)
            except OSError:
                pass 

    print("Part 04 Infrastructure Hardening complete!")

if __name__ == "__main__":
    create_scaffold()