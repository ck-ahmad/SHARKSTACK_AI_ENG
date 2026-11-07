import pytest
from httpx import AsyncClient
from app.services.parser import DocumentParserService
from app.services.chunker import ChunkingService
from app.services.vector_store import EmbeddingService

def test_parser_txt():
    content = b"Enterprise RAG Platform Test Document."
    text = DocumentParserService.parse_file("test.txt", content)
    assert text == "Enterprise RAG Platform Test Document."

def test_chunker_recursive():
    text = "Paragraph 1 line text.\n\nParagraph 2 line text."
    chunks = ChunkingService.recursive_character_chunking(text, chunk_size=30, chunk_overlap=5)
    assert len(chunks) > 0
    assert "Paragraph 1" in chunks[0]["content"]

def test_embedding_generation():
    texts = ["Sample chunk 1", "Sample chunk 2"]
    embeddings = EmbeddingService.generate_embeddings(texts, dimension=128)
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 128

@pytest.mark.asyncio
async def test_ingest_document_endpoint(async_client):
    file_content = b"Phase 2 test file content for document ingestion pipeline."
    files = {"file": ("test_ingest.txt", file_content, "text/plain")}
    response = await async_client.post("/api/v1/documents/ingest", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert data["chunks_count"] > 0
