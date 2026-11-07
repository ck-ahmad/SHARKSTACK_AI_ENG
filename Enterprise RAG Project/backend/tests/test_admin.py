import pytest
from httpx import AsyncClient
from app.services.analytics import AnalyticsEngine

def test_analytics_recording():
    metric = AnalyticsEngine.record_request("tenant_analytics", "/chat/completions", 150.5, 450)
    assert metric["tenant_id"] == "tenant_analytics"
    assert metric["tokens_used"] == 450
    summary = AnalyticsEngine.get_tenant_analytics("tenant_analytics")
    assert summary["total_requests"] == 1
    assert summary["total_tokens_consumed"] == 450

@pytest.mark.asyncio
async def test_admin_analytics_endpoint(async_client):
    headers = {
        "X-User-Id": "usr_admin",
        "X-Tenant-Id": "tenant_analytics",
        "X-Role": "admin"
    }
    response = await async_client.get("/api/v1/admin/analytics", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data

@pytest.mark.asyncio
async def test_system_diagnostics_endpoint(async_client):
    headers = {
        "X-User-Id": "usr_admin",
        "X-Tenant-Id": "tenant_analytics",
        "X-Role": "admin"
    }
    response = await async_client.get("/api/v1/admin/diagnostics", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["system_version"] == "0.6.0-enterprise"
