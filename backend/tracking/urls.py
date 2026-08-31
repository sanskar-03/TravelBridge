from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrackingEventViewSet, ProofOfDeliveryViewSet

router = DefaultRouter()
router.register(r'events', TrackingEventViewSet, basename='tracking-event')
router.register(r'pod', ProofOfDeliveryViewSet, basename='pod')

urlpatterns = [
    path('', include(router.urls)),
]
