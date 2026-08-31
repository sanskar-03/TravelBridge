from .models import AdminActionAudit

def log_admin_action(admin, action: str, target_type: str, target_id: str, reason: str = "", metadata: dict = None):
    AdminActionAudit.objects.create(
        admin=admin,
        action=action,
        target_type=target_type,
        target_id=str(target_id),
        reason=reason,
        metadata=metadata or {}
    )
