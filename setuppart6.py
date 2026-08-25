import os
from pathlib import Path

# --- 1. DIRECTORY STRUCTURE ---
DIRECTORIES = [
    "backend/travelbridge",
    "backend/users",
    "frontend/src/contexts",
    "frontend/src/lib",
    "frontend/src/components/layout",
]

# --- 2. FILE DEFINITIONS ---
FILES = {
    # ==========================================
    # BACKEND: USERS APP (Models & Auth Logic)
    # ==========================================
    "backend/users/models.py": """from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from common.models import BaseModel

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    \"\"\"
    Core user model mapped to Firebase Authentication.
    \"\"\"
    email = models.EmailField(unique=True, db_index=True)
    
    # Firebase Identity Mapping
    firebase_uid = models.CharField(max_length=128, unique=True, null=True, blank=True, db_index=True)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Trust/Verification Status
    is_email_verified = models.BooleanField(default=False)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True, max_length=1000)
    
    def __str__(self):
        return f"Profile for {self.user.email}"
""",

    "backend/travelbridge/firebase_config.py": """import firebase_admin
from firebase_admin import credentials
from django.conf import settings
import logging

logger = logging.getLogger('travelbridge')

def initialize_firebase():
    \"\"\"
    Initializes the Firebase Admin SDK safely as a singleton.
    \"\"\"
    if not firebase_admin._apps:
        if settings.FIREBASE_PRIVATE_KEY and settings.FIREBASE_PROJECT_ID:
            try:
                # Format private key explicitly (handles newline characters in env vars)
                private_key = settings.FIREBASE_PRIVATE_KEY.replace('\\\\n', '\\n')
                
                cred = credentials.Certificate({
                    "type": "service_account",
                    "project_id": settings.FIREBASE_PROJECT_ID,
                    "private_key_id": "",
                    "private_key": private_key,
                    "client_email": settings.FIREBASE_CLIENT_EMAIL,
                    "client_id": "",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.FIREBASE_CLIENT_EMAIL}"
                })
                firebase_admin.initialize_app(cred)
                logger.info("✅ Firebase Admin SDK initialized successfully.")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Firebase Admin: {str(e)}")
        elif settings.DEBUG and settings.AI_MODE == 'mock':
            logger.warning("⚠️ Running in AI mock mode without real Firebase credentials. Token verification will be bypassed for mock tokens.")
        else:
            logger.error("❌ Firebase credentials missing in environment variables. Authentication will fail.")
""",

    "backend/travelbridge/apps.py": """from django.apps import AppConfig

class TravelbridgeConfig(AppConfig):
    name = 'travelbridge'

    def ready(self):
        from .firebase_config import initialize_firebase
        initialize_firebase()
""",

    "backend/users/authentication.py": """from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from firebase_admin import auth
from django.conf import settings
from .models import User
import logging

logger = logging.getLogger('travelbridge')

class FirebaseAuthentication(BaseAuthentication):
    \"\"\"
    Verifies Firebase ID tokens against the Firebase Admin SDK.
    Maps verified tokens to Django Users securely.
    \"\"\"
    keyword = 'Bearer'

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None
        
        parts = auth_header.split()
        if len(parts) == 0 or parts[0].lower() != self.keyword.lower():
            return None
        
        if len(parts) != 2:
            raise AuthenticationFailed('Authorization header must be Bearer <token>')
            
        token = parts[1]
        
        # Safe Development Bypass
        if settings.DEBUG and settings.AI_MODE == 'mock' and token == 'mock-token-123':
            user, _ = User.objects.get_or_create(
                firebase_uid='mock_uid_123',
                defaults={'email': 'mock@travelbridge.test'}
            )
            if not user.is_active:
                raise AuthenticationFailed('Mock user account is disabled.')
            return (user, None)

        # Production / Real Token Verification
        try:
            decoded_token = auth.verify_id_token(token)
        except Exception as e:
            logger.warning(f"Firebase token verification failed: {str(e)}")
            raise AuthenticationFailed('Invalid or expired Firebase token.')
            
        uid = decoded_token.get('uid')
        email = decoded_token.get('email', '')
        
        if not uid:
            raise AuthenticationFailed('Firebase token does not contain a valid UID.')
            
        # Map or Create the Django User (Race-condition safe via get_or_create on unique constraints)
        user, created = User.objects.get_or_create(
            firebase_uid=uid,
            defaults={'email': email, 'is_email_verified': decoded_token.get('email_verified', False)}
        )
        
        # Enforce Account Status Server-Side
        if not user.is_active:
            raise AuthenticationFailed('Your account has been suspended or deactivated.')
            
        return (user, decoded_token)
""",

    "backend/users/urls.py": """from django.urls import path
from .views import current_user

urlpatterns = [
    path('me/', current_user, name='current-user'),
]
""",

    "backend/users/views.py": """from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    \"\"\"
    Protected endpoint to fetch the current authenticated user's basic info.
    \"\"\"
    user = request.user
    return Response({
        "id": str(user.id),
        "email": user.email,
        "firebase_uid": user.firebase_uid,
        "is_active": user.is_active,
        "is_email_verified": user.is_email_verified
    })
""",

    # ==========================================
    # FRONTEND: FIREBASE INTEGRATION & CONTEXT
    # ==========================================
    "frontend/src/lib/firebase.ts": """import { initializeApp, getApps, getApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

// Public Configuration (Safe to expose to client)
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID
};

// Initialize as a singleton to prevent hot-reload errors
const app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);
const auth = getAuth(app);

export { app, auth };
""",

    "frontend/src/contexts/AuthContext.tsx": """'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, onAuthStateChanged, signOut } from 'firebase/auth';
import { auth } from '@/lib/firebase';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  logout: () => Promise<void>;
  getToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  logout: async () => {},
  getToken: async () => null,
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  const logout = async () => {
    await signOut(auth);
  };

  const getToken = async () => {
    if (user) {
      return await user.getIdToken();
    }
    return null;
  };

  return (
    <AuthContext.Provider value={{ user, loading, logout, getToken }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
""",

    "frontend/src/components/layout/ProtectedRoute.tsx": """'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      // Redirect to login if unauthenticated
      router.push('/login');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <p className="text-text-secondary">Initializing authentication...</p>
      </div>
    );
  }

  if (!user) return null; // Prevent flicker while redirecting

  return <>{children}</>;
}
"""
}

def inject_env_vars():
    env_example_path = Path(".env.example")
    
    firebase_vars = """
# ==========================================
# FIREBASE BACKEND SECRETS (DO NOT COMMIT)
# ==========================================
FIREBASE_PROJECT_ID=
FIREBASE_CLIENT_EMAIL=
FIREBASE_PRIVATE_KEY=

# ==========================================
# FIREBASE FRONTEND CONFIG (PUBLIC)
# ==========================================
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=
NEXT_PUBLIC_FIREBASE_APP_ID=
"""
    if env_example_path.exists():
        with open(env_example_path, 'r', encoding='utf-8') as f:
            if 'NEXT_PUBLIC_FIREBASE_API_KEY' not in f.read():
                with open(env_example_path, 'a', encoding='utf-8') as fa:
                    fa.write(firebase_vars)
                print("✅ Appended Firebase variables to .env.example")

def inject_backend_deps():
    req_path = Path("backend/requirements.txt")
    if req_path.exists():
        with open(req_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if "firebase-admin" not in content:
            with open(req_path, 'a', encoding='utf-8') as f:
                f.write("firebase-admin>=6.2.0\n")
            print("✅ Added firebase-admin to backend/requirements.txt")

def inject_frontend_deps():
    pkg_path = Path("frontend/package.json")
    if pkg_path.exists():
        with open(pkg_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if '"firebase":' not in content:
            content = content.replace('"react":', '"firebase": "^10.12.3",\n    "react":')
            with open(pkg_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Added firebase to frontend/package.json")

def inject_django_settings():
    settings_path = Path("backend/travelbridge/settings.py")
    urls_path = Path("backend/travelbridge/urls.py")
    init_path = Path("backend/travelbridge/__init__.py")

    # 1. Add DRF Config and AppConfig to settings
    if settings_path.exists():
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'REST_FRAMEWORK' not in content:
            content += """
# ==========================================
# REST FRAMEWORK & FIREBASE
# ==========================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'users.authentication.FirebaseAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}

FIREBASE_PROJECT_ID = env('FIREBASE_PROJECT_ID', default='')
FIREBASE_CLIENT_EMAIL = env('FIREBASE_CLIENT_EMAIL', default='')
FIREBASE_PRIVATE_KEY = env('FIREBASE_PRIVATE_KEY', default='')
"""
        # Ensure our custom apps.py config is loaded
        if "'travelbridge.apps.TravelbridgeConfig'" not in content:
            content = content.replace(
                "INSTALLED_APPS = [",
                "INSTALLED_APPS = [\n    'travelbridge.apps.TravelbridgeConfig',"
            )
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(content)

    # 2. Add users.urls to main urls
    if urls_path.exists():
        with open(urls_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if "'api/users/'" not in content:
            content = content.replace(
                "path('api/health/', health_check, name='api-health-check'),",
                "path('api/health/', health_check, name='api-health-check'),\n    path('api/users/', include('users.urls')),"
            ).replace("from django.urls import path", "from django.urls import path, include")
            with open(urls_path, 'w', encoding='utf-8') as f:
                f.write(content)

def append_handoff():
    handoff_path = Path("HANDOFF_STATE.md")
    part6_handoff = """
# Part 06 Handoff

## Authentication Architecture
Implemented a split-trust architecture. Firebase Authentication handles client-side identity and passwords. The Next.js frontend holds public config, while the Django backend holds the private Firebase Admin SDK credentials. 

## Backend Verification & Mapping
Created `FirebaseAuthentication` DRF class. It intercepts Bearer tokens, decrypts them via `auth.verify_id_token()`, and automatically fetches or creates the Django `User` model using `firebase_uid`. It explicitly blocks suspended users by verifying `user.is_active` on every secure request.

## Frontend Auth State
Implemented `AuthContext.tsx` reacting to `onAuthStateChanged`. Provides a loading UI lock to prevent authentication flicker. Created `<ProtectedRoute />` wrapper that automatically forces unauthenticated users back to login without exposing protected routes momentarily.

## Security
* Replaced DRF's default session authentication with strict stateless Firebase Bearer tokens.
* Safe mock-mode exists for CI/testing, strictly guarded by `DEBUG=True` and `AI_MODE=mock`.
* `FIREBASE_PRIVATE_KEY` handles raw newline parsing gracefully.

## Next Part
PART 07 — User Profiles, Roles, Verification Foundation & Account Settings
"""
    if handoff_path.exists():
        with open(handoff_path, 'a', encoding='utf-8') as f:
            f.write(part6_handoff)
        print("✅ Appended Part 06 to HANDOFF_STATE.md")

def create_scaffold():
    print("🚀 Initializing Part 06 (Firebase Authentication & Security)...\n")

    for directory in DIRECTORIES:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}/")

    for filename, content in FILES.items():
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        if content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📄 Created/Updated file: {filename}")

    inject_env_vars()
    inject_backend_deps()
    inject_frontend_deps()
    inject_django_settings()
    append_handoff()

    print("\n✅ Part 06 Setup complete!")
    print("\n👉 REQUIRED NEXT STEPS:")
    print("1. Rebuild your containers so the new dependencies (Firebase SDKs) are installed:")
    print("   docker-compose down")
    print("   docker-compose up -d --build")
    print("2. Run the database migrations (for the new firebase_uid field):")
    print("   docker-compose exec backend python manage.py makemigrations users")
    print("   docker-compose exec backend python manage.py migrate")
    print("3. Verify the public vs protected routing via curl (it should return 401 Unauthorized for /api/users/me/):")
    print("   curl http://localhost:8000/api/users/me/")

if __name__ == "__main__":
    create_scaffold()