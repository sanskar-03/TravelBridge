from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Protected endpoint to fetch the current authenticated user's basic info.
    """
    user = request.user
    return Response({
        "id": str(user.id),
        "email": user.email,
        "firebase_uid": user.firebase_uid,
        "is_active": user.is_active,
        "is_email_verified": user.is_email_verified
    })
