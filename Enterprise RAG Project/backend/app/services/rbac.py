from enum import Enum
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status, Depends, Header
from datetime import datetime

class Role(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"

class UserContext:
    def __init__(self, user_id: str, tenant_id: str, role: Role):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.role = role

def get_current_user_context(
    x_user_id: Optional[str] = Header("usr_default"),
    x_tenant_id: Optional[str] = Header("tenant_default"),
    x_role: Optional[str] = Header("admin")
) -> UserContext:
    try:
        user_role = Role(x_role.lower())
    except ValueError:
        user_role = Role.VIEWER
    return UserContext(user_id=x_user_id, tenant_id=x_tenant_id, role=user_role)

class RBACEnforcer:
    @staticmethod
    def require_role(allowed_roles: List[Role]):
        def dependency(user_ctx: UserContext = Depends(get_current_user_context)):
            if user_ctx.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. User role '{user_ctx.role}' does not possess required privileges."
                )
            return user_ctx
        return dependency

class AuditLogger:
    _logs: List[Dict[str, Any]] = []

    @classmethod
    def log_event(cls, user_id: str, tenant_id: str, action: str, resource: str, details: Optional[Dict[str, Any]] = None):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "tenant_id": tenant_id,
            "action": action,
            "resource": resource,
            "details": details or {}
        }
        cls._logs.append(log_entry)
        return log_entry

    @classmethod
    def get_tenant_logs(cls, tenant_id: str) -> List[Dict[str, Any]]:
        return [log for log in cls._logs if log["tenant_id"] == tenant_id]
