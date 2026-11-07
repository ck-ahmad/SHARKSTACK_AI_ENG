from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.vector_store import EmbeddingService, VectorStoreService
from app.services.retrieval import BM25SearchEngine, DenseVectorSearchEngine, HybridRetrievalService
from app.api.endpoints.documents import vector_store

router = APIRouter()

class SearchQueryRequest(BaseModel):
    query: str
    document_id: Optional[str] = None
    top_k: int = 5
    search_mode: str = "hybrid"  # "hybrid", "dense", "sparse"

@router.post("/query")
async def search_query(request: SearchQueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")
        
    # Gather corpus from vector store
    corpus = []
    if request.document_id:
        corpus = vector_store.get_document_chunks(request.document_id)
    else:
        for doc_id, chunks in vector_store._store.items():
            corpus.extend(chunks)
            
    if not corpus:
        return {"query": request.query, "results_count": 0, "results": []}

    # Dense vector search
    query_vector = EmbeddingService.generate_embeddings([request.query])[0]
    dense_results = DenseVectorSearchEngine.search(query_vector, corpus)

    # Sparse BM25 search
    bm25_scores = BM25SearchEngine.calculate_bm25_scores(request.query, corpus)
    sparse_results = []
    for doc, score in zip(corpus, bm25_scores):
        sparse_results.append({"chunk_id": doc.get("chunk_id"), "content": doc.get("content"), "score": score, "metadata": doc.get("metadata")})
    sparse_results.sort(key=lambda x: x["score"], reverse=True)

    if request.search_mode == "dense":
        final_results = dense_results[:request.top_k]
    elif request.search_mode == "sparse":
        final_results = sparse_results[:request.top_k]
    else:
        # Hybrid with RRF
        final_results = HybridRetrievalService.reciprocal_rank_fusion(dense_results, sparse_results)[:request.top_k]

    return {
        "query": request.query,
        "search_mode": request.search_mode,
        "results_count": len(final_results),
        "results": final_results
    }
