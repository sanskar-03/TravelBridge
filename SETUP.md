# TravelBridge Setup Guide

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
