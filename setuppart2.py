import os
import stat
from pathlib import Path

# --- 1. DIRECTORY STRUCTURE ---
DIRECTORIES = [
    "backend/travelbridge",
    "backend/travelbridge/tests",
    "frontend/src/app",
    "frontend/public",
    "docs",
    "tests",
]

# --- 2. FILE DEFINITIONS ---
FILES = {
    # -------------------------------------------------------------
    # ROOT / ENVIRONMENT CONFIGURATION
    # -------------------------------------------------------------
    ".env.example": """# ==========================================
# TRAVELBRIDGE ENVIRONMENT CONFIGURATION
# ==========================================
# WARNING: Do NOT place production secrets in this file.
# Copy to .env for local development.

# ENVIRONMENT & MODES
ENVIRONMENT=development
DJANGO_DEBUG=True
AI_MODE=mock
PAYMENT_MODE=sandbox

# DJANGO
DJANGO_SECRET_KEY=local-dev-insecure-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,backend,0.0.0.0
CORS_ALLOWED_ORIGINS=http://localhost:3000,[http://127.0.0.1:3000](http://127.0.0.1:3000)

# DATABASE (PostgreSQL)
POSTGRES_DB=travelbridge
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgres://postgres:postgres@db:5432/travelbridge

# CACHE / MESSAGE BROKER (Redis)
REDIS_URL=redis://redis:6379/0

# RESERVED FOR FUTURE PARTS (DO NOT POPULATE WITH REAL SECRETS)
FIREBASE_PROJECT_ID=
FIREBASE_CLIENT_EMAIL=
FIREBASE_PRIVATE_KEY=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=
""",

    # -------------------------------------------------------------
    # DOCKER COMPOSE CONFIGURATION (Health-Aware)
    # -------------------------------------------------------------
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
      interval: 5s
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
      interval: 5s
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
""",

    # -------------------------------------------------------------
    # BACKEND: PYTHON / DJANGO CONFIGURATION
    # -------------------------------------------------------------
    "backend/requirements.txt": """Django>=4.2,<5.0
djangorestframework>=3.14.0
django-cors-headers>=4.3.1
psycopg2-binary>=2.9.9
redis>=5.0.1
django-environ>=0.11.2
pytest>=7.4.3
pytest-django>=4.7.0
""",

    "backend/Dockerfile": """FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
""",

    "backend/entrypoint.sh": """#!/bin/sh
set -e

echo "Waiting for database and redis connections..."

# Run database migrations
python manage.py migrate --noinput

# Start development server
exec python manage.py runserver 0.0.0.0:8000
""",

    "backend/manage.py": """#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travelbridge.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Is it installed and available on your PYTHONPATH?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
""",

    "backend/pytest.ini": """[pytest]
DJANGO_SETTINGS_MODULE = travelbridge.settings
python_files = tests.py test_*.py *_tests.py
""",

    "backend/travelbridge/__init__.py": "",

    "backend/travelbridge/wsgi.py": """import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travelbridge.settings')
application = get_wsgi_application()
""",

    "backend/travelbridge/asgi.py": """import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travelbridge.settings')
application = get_asgi_application()
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

# Read .env if present
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

# Database configuration
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres://postgres:postgres@localhost:5432/travelbridge')
}

# Redis Cache configuration
REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS configuration
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=['http://localhost:3000', '[http://127.0.0.1:3000](http://127.0.0.1:3000)'])
CORS_ALLOW_CREDENTIALS = True

# Safety & Modes
AI_MODE = env('AI_MODE', default='mock')
PAYMENT_MODE = env('PAYMENT_MODE', default='sandbox')
""",

    "backend/travelbridge/views.py": """from django.http import JsonResponse
from django.db import connection
import redis
from django.conf import settings

def health_check(request):
    \"\"\"
    Sanitized health check endpoint.
    Verifies application, database, and cache availability without leaking sensitive credentials.
    \"\"\"
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
""",

    "backend/travelbridge/urls.py": """from django.contrib import admin
from django.urls import path
from .views import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health-check'),
    path('api/health/', health_check, name='api-health-check'),
]
""",

    "backend/travelbridge/tests/__init__.py": "",

    "backend/travelbridge/tests/test_health.py": """import pytest
from django.urls import reverse
from django.test import Client

@pytest.mark.django_db
def test_health_check_endpoint():
    client = Client()
    response = client.get(reverse('health-check'))
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "redis" in data
    # Ensure no secrets or connection strings are leaked
    for key, value in data.items():
        assert "password" not in str(value).lower()
        assert "secret" not in str(value).lower()
""",

    # -------------------------------------------------------------
    # FRONTEND: NEXT.JS / TYPESCRIPT CONFIGURATION
    # -------------------------------------------------------------
    "frontend/package.json": """{
  "name": "travelbridge-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "14.2.5",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/node": "^20.14.10",
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "eslint": "^8.57.0",
    "eslint-config-next": "14.2.5",
    "typescript": "^5.5.3"
  }
}
""",

    "frontend/tsconfig.json": """{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
""",

    "frontend/next.config.js": """/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false
};

module.exports = nextConfig;
""",

    "frontend/Dockerfile": """FROM node:18-alpine

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]
""",

    "frontend/src/app/layout.tsx": """import type { ReactNode } from 'react';

export const metadata = {
  title: 'TravelBridge — Peer-to-Peer Travel & Baggage Marketplace',
  description: 'Connecting travelers with available baggage capacity to package senders worldwide.',
};

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: 'system-ui, -apple-system, sans-serif' }}>
        {children}
      </body>
    </html>
  );
}
""",

    "frontend/src/app/page.tsx": """export default function HomePage() {
  return (
    <main style={{ padding: '3rem', maxWidth: '800px', margin: '0 auto', lineHeight: '1.6' }}>
      <h1>TravelBridge</h1>
      <p>
        <strong>Status:</strong> Environment & Development Infrastructure Configured (Part 02).
      </p>
      <p>
        TravelBridge is a peer-to-peer travel and baggage marketplace connecting travelers who have available luggage capacity with requesters who need items safely transported.
      </p>
      <hr style={{ margin: '2rem 0', border: 'none', borderTop: '1px solid #e2e8f0' }} />
      <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
        Design System & Visual Identity will be initialized in Part 03.
      </p>
    </main>
  );
}
""",

    # -------------------------------------------------------------
    # DOCUMENTATION UPDATES (Fixed Formatting)
    # -------------------------------------------------------------
    "SETUP.md": """# TravelBridge Setup Guide

## Prerequisites
* **Docker & Docker Compose** (Recommended — installs and runs Postgres & Redis automatically without needing them on your OS)
* **Python 3.10+** (For local backend development)
* **Node.js 18+** (For local frontend development)

---

## Option 1: Docker (Recommended)
This runs Backend, Frontend, PostgreSQL, and Redis in isolated containers.

1. **Configure Environment:**
   Run: cp .env.example .env

2. **Start Services:**
   Run: docker-compose up --build
"""
}

def create_scaffold():
    print("🚀 Initializing TravelBridge Frameworks (Part 02)...\n")

    # Create directories
    for directory in DIRECTORIES:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}/")

    # Create files
    for filename, content in FILES.items():
        filepath = Path(filename)
        # Ensure parent directories exist for nested files
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 Created file:      {filename}")

        # Make shell scripts executable if we are on a unix-like system
        if filename.endswith(".sh") or filename.endswith("manage.py"):
            try:
                st = os.stat(filepath)
                os.chmod(filepath, st.st_mode | stat.S_IEXEC)
            except OSError:
                pass # Windows fallback

    print("\n✅ Part 02 Setup complete!")
    print("👉 Next Step: Ensure Docker Desktop is open and running, then run 'docker-compose up --build'.")

if __name__ == "__main__":
    create_scaffold()