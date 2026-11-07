import math
from typing import List, Dict, Any
from app.services.vector_store import EmbeddingService, VectorStoreService

class BM25SearchEngine:
    @staticmethod
    def calculate_bm25_scores(query: str, corpus: List[Dict[str, Any]], k1: float = 1.5, b: float = 0.75) -> List[float]:
        query_terms = query.lower().split()
        if not query_terms or not corpus:
            return [0.0] * len(corpus)
            
        doc_texts = [doc["content"].lower().split() for doc in corpus]
        doc_lens = [len(doc) for doc in doc_texts]
        avg_doc_len = sum(doc_lens) / len(doc_lens) if doc_lens else 1.0
        n_docs = len(corpus)
        
        # Calculate Inverse Document Frequency (IDF)
        idf = {}
        for term in set(query_terms):
            n_containing = sum(1 for doc in doc_texts if term in doc)
            idf[term] = math.log((n_docs - n_containing + 0.5) / (n_containing + 0.5) + 1.0)
            
        scores = []
        for idx, doc in enumerate(doc_texts):
            score = 0.0
            doc_len = doc_lens[idx]
            term_freqs = {term: doc.count(term) for term in query_terms}
            for term in query_terms:
                tf = term_freqs[term]
                numerator = tf * (k1 + 1)
                denominator = tf + k1 * (1 - b + b * (doc_len / avg_doc_len))
                score += idf[term] * (numerator / (denominator if denominator != 0 else 1.0))
            scores.append(score)
        return scores

class DenseVectorSearchEngine:
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm_a = sum(a * a for a in vec1) ** 0.5
        norm_b = sum(b * b for b in vec2) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    @classmethod
    def search(cls, query_vector: List[float], corpus: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for doc in corpus:
            sim = cls.cosine_similarity(query_vector, doc.get("embedding", []))
            results.append({"chunk_id": doc.get("chunk_id"), "content": doc.get("content"), "score": sim, "metadata": doc.get("metadata")})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

class HybridRetrievalService:
    @staticmethod
    def reciprocal_rank_fusion(dense_results: List[Dict[str, Any]], sparse_results: List[Dict[str, Any]], k: int = 60) -> List[Dict[str, Any]]:
        scores: Dict[str, float] = {}
        doc_map: Dict[str, Dict[str, Any]] = {}
        
        for rank, item in enumerate(dense_results):
            cid = item["chunk_id"]
            scores[cid] = scores.get(cid, 0.0) + (1.0 / (k + rank + 1))
            doc_map[cid] = item
            
        for rank, item in enumerate(sparse_results):
            cid = item["chunk_id"]
            scores[cid] = scores.get(cid, 0.0) + (1.0 / (k + rank + 1))
            if cid not in doc_map:
                doc_map[cid] = item
                
        fused = []
        for cid, rrf_score in scores.items():
            entry = doc_map[cid].copy()
            entry["rrf_score"] = rrf_score
            fused.append(entry)
            
        fused.sort(key=lambda x: x["rrf_score"], reverse=True)
        return fused
