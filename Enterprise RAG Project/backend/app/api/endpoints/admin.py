from fastapi import APIRouter, Depends
from app.services.rbac import get_current_user_context, UserContext, RBACEnforcer, Role
from app.services.analytics import AnalyticsEngine

router = APIRouter()

@router.get("/analytics", dependencies=[Depends(RBACEnforcer.require_role([Role.ADMIN, Role.ANALYST]))])
async def get_dashboard_analytics(user_ctx: UserContext = Depends(get_current_user_context)):
    analytics = AnalyticsEngine.get_tenant_analytics(user_ctx.tenant_id)
    return {
        "status": "success",
        "dashboard": "EnterpriseIQ Admin Analytics",
        "data": analytics
    }

@router.get("/diagnostics", dependencies=[Depends(RBACEnforcer.require_role([Role.ADMIN]))])
async def get_system_diagnostics(user_ctx: UserContext = Depends(get_current_user_context)):
    return {
        "status": "healthy",
        "system_version": "0.6.0-enterprise",
        "active_tenant": user_ctx.tenant_id,
        "database_status": "connected",
        "vector_store_status": "operational",
        "cache_status": "redis_connected"
    }
