from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from users.models import Profile
from fraud.models import FraudFlag
from verifications.models import UserVerification
from disputes.models import Dispute
from .models import AdminActionAudit
from .services import log_admin_action
from django.utils import timezone

User = get_user_model()

class IsAdminUserOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))

class AdminDashboardViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAdminUserOrStaff]

    @action(detail=False, methods=['get'])
    def overview(self, data_request):
        users_count = User.objects.count()
        pending_verifications = UserVerification.objects.filter(status='PENDING').count()
        open_fraud_flags = FraudFlag.objects.filter(status='OPEN').count()
        open_disputes = Dispute.objects.filter(status='OPEN').count()
        
        return Response({
            "total_users": users_count,
            "pending_verifications": pending_verifications,
            "open_fraud_flags": open_fraud_flags,
            "open_disputes": open_disputes
        })

class AdminUserManagementViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAdminUserOrStaff]

    def list(self, request):
        users = User.objects.all().select_related('profile', 'verification_record').order_by('-created_at')[:50]
        data = [{
            "id": str(u.id),
            "email": u.email,
            "is_active": u.is_active,
            "is_staff": u.is_staff,
            "role": getattr(u, 'profile', None) and u.profile.role or 'UNKNOWN',
            "verification_status": getattr(u, 'verification_record', None) and u.verification_record.status or 'NOT_SUBMITTED',
            "created_at": u.created_at
        } for u in users]
        return Response(data)

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        reason = request.data.get('reason', 'Administrative suspension.')
        target_user.is_active = False
        target_user.save(update_fields=['is_active'])

        log_admin_action(request.user, 'USER_SUSPENDED', 'User', target_user.id, reason)
        return Response({"status": "user suspended successfully"})

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        reason = request.data.get('reason', 'Administrative restoration.')
        target_user.is_active = True
        target_user.save(update_fields=['is_active'])

        log_admin_action(request.user, 'USER_RESTORED', 'User', target_user.id, reason)
        return Response({"status": "user restored successfully"})


class AdminVerificationViewSet(viewsets.ModelViewSet):
    queryset = UserVerification.objects.all().select_related('user__profile')
    permission_classes = [permissions.IsAuthenticated, IsAdminUserOrStaff]

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        verification = self.get_object()
        verification.status = UserVerification.Status.APPROVED
        verification.reviewed_by = request.user
        verification.reviewed_at = timezone.now()
        verification.save()

        # Update profile verification badge if applicable
        profile = getattr(verification.user, 'profile', None)
        if profile:
            profile.verification_status = 'VERIFIED'
            profile.save(update_fields=['verification_status'])

        log_admin_action(request.user, 'VERIFICATION_APPROVED', 'UserVerification', verification.id)
        return Response({"status": "approved"})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        verification = self.get_object()
        reason = request.data.get('reason', 'Document rejected by reviewer.')
        verification.status = UserVerification.Status.REJECTED
        verification.rejection_reason = reason
        verification.reviewed_by = request.user
        verification.reviewed_at = timezone.now()
        verification.save()

        log_admin_action(request.user, 'VERIFICATION_REJECTED', 'UserVerification', verification.id, reason)
        return Response({"status": "rejected"})


class AdminFraudFlagViewSet(viewsets.ModelViewSet):
    queryset = FraudFlag.objects.all().select_related('user__profile')
    permission_classes = [permissions.IsAuthenticated, IsAdminUserOrStaff]

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        flag = self.get_object()
        flag.status = FraudFlag.Status.RESOLVED
        flag.resolved_by = request.user
        flag.save()

        log_admin_action(request.user, 'FRAUD_FLAG_RESOLVED', 'FraudFlag', flag.id)
        return Response({"status": "resolved"})


class AdminAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdminActionAudit.objects.all().select_related('admin')
    permission_classes = [permissions.IsAuthenticated, IsAdminUserOrStaff]
