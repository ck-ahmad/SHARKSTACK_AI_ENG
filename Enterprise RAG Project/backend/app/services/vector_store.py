from typing import List, Dict, Any
import random

class EmbeddingService:
    @staticmethod
    def generate_embeddings(texts: List[str], dimension: int = 1536) -> List[List[float]]:
        """Generates normalized embedding vectors (Mocked for testing / customizable for OpenAI/HuggingFace)."""
        embeddings = []
        for text in texts:
            seed = sum(ord(c) for c in text)
            random.seed(seed)
            vector = [random.uniform(-1.0, 1.0) for _ in range(dimension)]
            norm = sum(x**2 for x in vector) ** 0.5
            embeddings.append([x / norm for x in vector])
        return embeddings

class VectorStoreService:
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def insert_chunks(self, doc_id: str, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        self._store[doc_id] = []
        for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            self._store[doc_id].append({
                "chunk_id": f"{doc_id}_{idx}",
                "content": chunk["content"],
                "embedding": emb,
                "metadata": {"chunk_index": idx, "char_count": chunk["char_count"]}
            })
        return len(chunks)

    def get_document_chunks(self, doc_id: str) -> List[Dict[str, Any]]:
        return self._store.get(doc_id, [])
