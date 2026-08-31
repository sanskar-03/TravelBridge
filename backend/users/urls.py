from django.urls import path
from .views import manage_current_profile, get_public_profile, current_user

urlpatterns = [
    path('me/', current_user, name='current-user'),
    path('profile/', manage_current_profile, name='manage-profile'),
    path('profile/<uuid:pk>/', get_public_profile, name='public-profile'),
]
