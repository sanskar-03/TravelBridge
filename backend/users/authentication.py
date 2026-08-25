from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from firebase_admin import auth
from django.conf import settings
from .models import User
import logging

logger = logging.getLogger('travelbridge')

class FirebaseAuthentication(BaseAuthentication):
    """
    Verifies Firebase ID tokens against the Firebase Admin SDK.
    Maps verified tokens to Django Users securely.
    """
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
