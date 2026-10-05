from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: int
    user_id: int | None
    user_name: str
    role: str
    action: str
    description: str
    target_type: str | None
    target_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    audit_logs: list[AuditLogResponse]