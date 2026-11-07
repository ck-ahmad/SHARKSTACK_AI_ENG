import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_full_enterprise_rag_lifecycle(async_client):
    headers = {
        "X-User-Id": "usr_master",
        "X-Tenant-Id": "tenant_enterprise",
        "X-Role": "admin"
    }

    # 1. Check Health
    health_res = await async_client.get("/api/v1/health/")
    assert health_res.status_code == 200

    # 2. Ingest Document
    file_content = b"EnterpriseIQ delivers high-security enterprise RAG with strict tenant isolation and role-based access control."
    files = {"file": ("enterprise_policy.txt", file_content, "text/plain")}
    ingest_res = await async_client.post("/api/v1/documents/ingest", files=files, headers=headers)
    assert ingest_res.status_code == 200
    doc_id = ingest_res.json()["document_id"]

    # 3. Perform Hybrid Search
    search_payload = {
        "query": "security enterprise RAG tenant isolation",
        "document_id": doc_id,
        "top_k": 2,
        "search_mode": "hybrid"
    }
    search_res = await async_client.post("/api/v1/search/query", json=search_payload, headers=headers)
    assert search_res.status_code == 200
    assert search_res.json()["results_count"] > 0

    # 4. Generate RAG Chat Completion
    chat_payload = {
        "message": "What security features does EnterpriseIQ deliver?",
        "document_id": doc_id,
        "top_k": 2
    }
    chat_res = await async_client.post("/api/v1/chat/completions", json=chat_payload, headers=headers)
    assert chat_res.status_code == 200
    assert "[Source 1]" in chat_res.json()["response"]

    # 5. Check Admin Analytics & Diagnostics
    analytics_res = await async_client.get("/api/v1/admin/analytics", headers=headers)
    assert analytics_res.status_code == 200

    diag_res = await async_client.get("/api/v1/admin/diagnostics", headers=headers)
    assert diag_res.status_code == 200
    assert diag_res.json()["status"] == "healthy"
