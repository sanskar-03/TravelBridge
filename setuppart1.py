import os
from pathlib import Path

# 1. Define Directories
DIRECTORIES = [
    "backend",
    "frontend",
    "docs",
    "tests",
    ".github/workflows"
]

# 2. Define File Contents
FILES = {
    ".env.example": """# ==========================================
# TRAVELBRIDGE ENVIRONMENT CONFIGURATION
# ==========================================
# WARNING: NEVER put real secrets in this file!
# Copy this file to .env and fill in local values.

# DJANGO
DJANGO_SECRET_KEY=
DJANGO_DEBUG=

# DATABASE
DATABASE_URL=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=

# CACHE / BROKER
REDIS_URL=

# FIREBASE AUTHENTICATION
FIREBASE_PROJECT_ID=
FIREBASE_CLIENT_EMAIL=
FIREBASE_PRIVATE_KEY=

# CLOUDINARY (MEDIA STORAGE)
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# PAYMENTS
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=

# MODES
AI_MODE=mock
PAYMENT_MODE=sandbox
""",

    ".gitignore": """# Environment Variables
.env
.env.*
!.env.example

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# Node
node_modules/
.next/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Local Databases
*.sqlite3
*.db

# Generated Build/Test Files
coverage/
dist/
build/

# Uploads / Local Media
media/
uploads/

# Editor / OS
.DS_Store
Thumbs.db
.vscode/
.idea/
""",

    "docker-compose.yml": """version: '3.8'
# Foundation Docker configuration for TravelBridge.
# (Celery, Channels, etc. to be configured in later parts).

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-travelbridge}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: 
      context: ./backend
    # Placeholder command until Part 02
    command: echo "Backend container foundation ready."
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgres://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@db:5432/${POSTGRES_DB:-travelbridge}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  frontend:
    build:
      context: ./frontend
    # Placeholder command until Part 02
    command: echo "Frontend container foundation ready."
    volumes:
      - ./frontend:/app
    ports:
      - "3000:3000"

volumes:
  postgres_data:
""",

    "README.md": """# TravelBridge

TravelBridge is a peer-to-peer travel and baggage marketplace connecting travelers who have available baggage capacity with requesters who need items transported between locations.

## High-Level Architecture
* **Backend:** Python, Django, Django REST Framework, PostgreSQL, Redis, Celery, Django Channels.
* **Frontend:** Next.js, React, TypeScript.
* **Infrastructure:** Docker, Docker Compose.
* **Third-Party Integrations:** Firebase Auth, Cloudinary, Stripe/Razorpay.

*Note: This repository is currently at **Part 01** of 22 in its development lifecycle. Features like matching, chat, and payments are architected but not yet implemented.*
""",

    "SETUP.md": """# TravelBridge Setup Guide

## Prerequisites
- Docker and Docker Compose
- Python 3.10+
- Node.js 18+

## Initial Setup
1. Clone the repository.
2. Copy `.env.example` to `.env` and fill in local placeholder values (Do NOT use production secrets).
3. (Future parts will detail `docker-compose up` commands and environment hydration).

*Note: Application frameworks will be initialized in Part 02.*
""",

    "MASTER_EXECUTION_RULES.md": """# MASTER EXECUTION RULES

This file is the permanent rulebook for Parts 01–22. AI agents MUST abide by these rules:

1. Work on the existing repository; never regenerate completely.
2. Read HANDOFF_STATE.md before starting a new part.
3. Read DESIGN_SYSTEM.md before frontend work.
4. Preserve working functionality.
5. Do not hardcode secrets.
6. Never commit .env.
7. Use TypeScript strict mode and avoid `any`.
8. Use Python type hints.
9. Validate all external input and uploaded files.
10. Enforce authorization server-side.
*(See master prompt for the full 40-rule list. Security, strict typing, and modularity are strictly enforced).*
""",

    "DESIGN_SYSTEM.md": """# TravelBridge Design System Foundation

## Core Directives for UI Agents
This file serves as the single source of truth for visual design.

**AVOID Generic AI-generated UI:**
- No random blue/purple gradients.
- No excessive glassmorphism or repetitive card grids.
- No generic SaaS dashboard templates.

**Identity & Themes:**
- The visual identity must communicate: travel, movement, routes, baggage, trust, and connection.
- A detailed visual system, typography, and component library will be established in Part 03.
""",

    "HANDOFF_STATE.md": """# TravelBridge Handoff State

## Current Part
Part 01 of 22

## Current Status
Foundation stage completed.

## Product
TravelBridge peer-to-peer travel and baggage marketplace

## Completed in Part 01
- Repository folder structure initialized.
- Environment variables template created (secrets protected).
- Gitignore established.
- Docker compose foundation mapped.
- Master execution, design, and handoff rules documented.

## Not Yet Implemented
Authentication, marketplace workflows, matching, chat, delivery, pricing, payments, reviews, fraud detection, verification, admin, deployment, and other future functionality are NOT implemented yet.

## Next Part
Part 02 — Repository, Environment & Configuration
"""
}

def create_scaffold():
    print("🚀 Initializing TravelBridge Foundation (Part 01)...\n")

    # Create directories
    for directory in DIRECTORIES:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}/")

    # Create files
    for filename, content in FILES.items():
        filepath = Path(filename)
        # We use 'w' to write, overwriting if something was there to ensure clean state
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 Created file:      {filename}")

    print("\n✅ Part 01 Foundation setup complete!")
    print("👉 You can now run: 'ls -la' to verify, and then provide the Prompt for Part 02.")

if __name__ == "__main__":
    create_scaffold()