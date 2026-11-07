from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.services.rbac import get_current_user_context, UserContext, RBACEnforcer, Role, AuditLogger

router = APIRouter()

@router.get("/logs", dependencies=[Depends(RBACEnforcer.require_role([Role.ADMIN, Role.ANALYST]))])
async def get_audit_logs(user_ctx: UserContext = Depends(get_current_user_context)):
    logs = AuditLogger.get_tenant_logs(user_ctx.tenant_id)
    return {
        "tenant_id": user_ctx.tenant_id,
        "logs_count": len(logs),
        "logs": logs
    }

@router.get("/tenants/me")
async def get_tenant_profile(user_ctx: UserContext = Depends(get_current_user_context)):
    AuditLogger.log_event(
        user_id=user_ctx.user_id,
        tenant_id=user_ctx.tenant_id,
        action="INSPECT_TENANT_PROFILE",
        resource=f"/tenants/{user_ctx.tenant_id}"
    )
    return {
        "user_id": user_ctx.user_id,
        "tenant_id": user_ctx.tenant_id,
        "role": user_ctx.role,
        "status": "active"
    }
