from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.vector_store import EmbeddingService
from app.services.retrieval import BM25SearchEngine, DenseVectorSearchEngine, HybridRetrievalService
from app.services.generation import PromptPipelineService, LLMGenerationEngine
from app.api.endpoints.documents import vector_store

router = APIRouter()

class ChatCompletionRequest(BaseModel):
    message: str
    document_id: Optional[str] = None
    top_k: int = 3
    temperature: float = 0.7

@router.post("/completions")
async def chat_completions(request: ChatCompletionRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message prompt cannot be empty.")
        
    # Gather documents
    corpus = []
    if request.document_id:
        corpus = vector_store.get_document_chunks(request.document_id)
    else:
        for doc_id, chunks in vector_store._store.items():
            corpus.extend(chunks)

    # Retrieval step
    retrieved_context = []
    if corpus:
        query_vector = EmbeddingService.generate_embeddings([request.message])[0]
        dense_results = DenseVectorSearchEngine.search(query_vector, corpus)
        bm25_scores = BM25SearchEngine.calculate_bm25_scores(request.message, corpus)
        
        sparse_results = []
        for doc, score in zip(corpus, bm25_scores):
            sparse_results.append({"chunk_id": doc.get("chunk_id"), "content": doc.get("content"), "score": score, "metadata": doc.get("metadata")})
        sparse_results.sort(key=lambda x: x["score"], reverse=True)

        retrieved_context = HybridRetrievalService.reciprocal_rank_fusion(dense_results, sparse_results)[:request.top_k]

    # Prompt assembly & response generation
    prompt = PromptPipelineService.build_rag_prompt(request.message, retrieved_context)
    result = LLMGenerationEngine.generate_response(prompt, retrieved_context)

    return {
        "model": "EnterpriseIQ-RAG-v1",
        "message": request.message,
        "response": result["answer"],
        "citations": result["citations"],
        "context_chunks_used": len(retrieved_context)
    }
