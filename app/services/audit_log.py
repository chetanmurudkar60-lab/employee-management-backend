from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User


def create_audit_log(
    db: Session,
    user: User,
    action: str,
    description: str,
    target_type: str | None = None,
    target_id: int | None = None,
):
    audit_log = AuditLog(
        user_id=user.id,
        user_name=user.name,
        role=user.role,
        action=action,
        description=description,
        target_type=target_type,
        target_id=target_id,
    )

    db.add(audit_log)

    return audit_log