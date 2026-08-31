from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TravelPostViewSet

router = DefaultRouter()
router.register(r'trips', TravelPostViewSet, basename='trip')

urlpatterns = [
    path('', include(router.urls)),
]
