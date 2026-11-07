import pytest
from httpx import AsyncClient
from app.services.rbac import Role, AuditLogger, UserContext

def test_audit_logging():
    entry = AuditLogger.log_event("usr_123", "tenant_alpha", "DOCUMENT_UPLOAD", "/documents/ingest")
    assert entry["user_id"] == "usr_123"
    assert entry["tenant_id"] == "tenant_alpha"
    assert len(AuditLogger.get_tenant_logs("tenant_alpha")) > 0

@pytest.mark.asyncio
async def test_tenant_profile_endpoint(async_client):
    headers = {
        "X-User-Id": "usr_test",
        "X-Tenant-Id": "tenant_test",
        "X-Role": "admin"
    }
    response = await async_client.get("/api/v1/audit/tenants/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == "tenant_test"
    assert data["role"] == "admin"

@pytest.mark.asyncio
async def test_rbac_restriction(async_client):
    # Viewer role attempting to access restricted audit logs
    headers = {
        "X-User-Id": "usr_viewer",
        "X-Tenant-Id": "tenant_test",
        "X-Role": "viewer"
    }
    response = await async_client.get("/api/v1/audit/logs", headers=headers)
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]
