from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Profile
from .serializers import CurrentUserProfileSerializer, PublicProfileSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    return Response({
        "id": str(user.id),
        "email": user.email,
        "firebase_uid": user.firebase_uid,
        "is_active": user.is_active,
        "is_email_verified": user.is_email_verified
    })

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def manage_current_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        serializer = CurrentUserProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = CurrentUserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_public_profile(request, pk):
    profile = get_object_or_404(Profile, id=pk)
    serializer = PublicProfileSerializer(profile)
    return Response(serializer.data)
