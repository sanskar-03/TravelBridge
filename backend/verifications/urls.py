from django.urls import path, include
from rest_framework import viewsets, permissions
from rest_framework.routers import DefaultRouter
from .models import UserVerification
from .serializers import UserVerificationSerializer

class UserVerificationViewSet(viewsets.ModelViewSet):
    serializer_class = UserVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserVerification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

router = DefaultRouter()
router.register(r'', UserVerificationViewSet, basename='verification')

urlpatterns = [
    path('', include(router.urls)),
]
