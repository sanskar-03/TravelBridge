from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminDashboardViewSet, AdminUserManagementViewSet, 
    AdminVerificationViewSet, AdminFraudFlagViewSet, AdminAuditLogViewSet
)

router = DefaultRouter()
router.register(r'dashboard', AdminDashboardViewSet, basename='admin-dashboard')
router.register(r'users', AdminUserManagementViewSet, basename='admin-users')
router.register(r'verifications', AdminVerificationViewSet, basename='admin-verifications')
router.register(r'fraud-flags', AdminFraudFlagViewSet, basename='admin-fraud')
router.register(r'audit-logs', AdminAuditLogViewSet, basename='admin-audit')

urlpatterns = [path('', include(router.urls))]
