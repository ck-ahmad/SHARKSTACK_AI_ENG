import pytest
from httpx import AsyncClient
from app.services.retrieval import BM25SearchEngine, DenseVectorSearchEngine, HybridRetrievalService

def test_bm25_search():
    corpus = [
        {"chunk_id": "1", "content": "Enterprise RAG architectural design pattern."},
        {"chunk_id": "2", "content": "PostgreSQL pgvector storage database setup."}
    ]
    scores = BM25SearchEngine.calculate_bm25_scores("RAG architecture", corpus)
    assert len(scores) == 2
    assert scores[0] > scores[1]

def test_rrf_fusion():
    dense = [{"chunk_id": "doc1", "content": "Text A"}, {"chunk_id": "doc2", "content": "Text B"}]
    sparse = [{"chunk_id": "doc2", "content": "Text B"}, {"chunk_id": "doc1", "content": "Text A"}]
    fused = HybridRetrievalService.reciprocal_rank_fusion(dense, sparse)
    assert len(fused) == 2
    assert fused[0]["rrf_score"] == fused[1]["rrf_score"]

@pytest.mark.asyncio
async def test_search_query_endpoint(async_client):
    # Ingest test document first
    file_content = b"Phase 3 tests hybrid search retrieval engine with BM25 and vector embeddings."
    files = {"file": ("search_test.txt", file_content, "text/plain")}
    ingest_res = await async_client.post("/api/v1/documents/ingest", files=files)
    doc_id = ingest_res.json()["document_id"]

    # Test Hybrid Search
    payload = {
        "query": "hybrid search retrieval engine",
        "document_id": doc_id,
        "top_k": 3,
        "search_mode": "hybrid"
    }
    response = await async_client.post("/api/v1/search/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["results_count"] > 0
    assert "rrf_score" in data["results"][0]
