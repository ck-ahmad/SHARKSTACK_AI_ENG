import pytest

@pytest.mark.asyncio
async def test_root_ui(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert "EnterpriseIQ" in response.text

@pytest.mark.asyncio
async def test_health(async_client):
    response = await async_client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
