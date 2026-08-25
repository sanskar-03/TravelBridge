import firebase_admin
from firebase_admin import credentials
from django.conf import settings
import logging

logger = logging.getLogger('travelbridge')

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK safely as a singleton.
    """
    if not firebase_admin._apps:
        if settings.FIREBASE_PRIVATE_KEY and settings.FIREBASE_PROJECT_ID:
            try:
                # Format private key explicitly (handles newline characters in env vars)
                private_key = settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n')
                
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
