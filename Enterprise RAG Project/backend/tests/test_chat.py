import pytest
from httpx import AsyncClient
from app.services.generation import PromptPipelineService, CitationEngine, LLMGenerationEngine

def test_prompt_building():
    context = [{"chunk_id": "c1", "content": "Enterprise security policy details."}]
    prompt = PromptPipelineService.build_rag_prompt("What is the security policy?", context)
    assert "Enterprise security policy details." in prompt
    assert "[Source 1]" in prompt

def test_citation_formatting():
    context = [{"chunk_id": "c1", "content": "Sample content text.", "rrf_score": 0.033}]
    citations = CitationEngine.format_sources(context)
    assert len(citations) == 1
    assert citations[0]["source_tag"] == "[Source 1]"
    assert citations[0]["chunk_id"] == "c1"

@pytest.mark.asyncio
async def test_chat_completions_endpoint(async_client):
    # Upload test document
    file_content = b"EnterpriseIQ provides zero-trust access control and role-based policies for document retrieval."
    files = {"file": ("policy.txt", file_content, "text/plain")}
    ingest_res = await async_client.post("/api/v1/documents/ingest", files=files)
    doc_id = ingest_res.json()["document_id"]

    # Test RAG completion endpoint
    payload = {
        "message": "What security policies are provided?",
        "document_id": doc_id,
        "top_k": 2
    }
    response = await async_client.post("/api/v1/chat/completions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "citations" in data
    assert data["context_chunks_used"] > 0
    assert "[Source 1]" in data["response"]
