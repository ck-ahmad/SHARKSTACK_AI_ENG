from fastapi import APIRouter, UploadFile, File, HTTPException, Query, status
from app.services.parser import DocumentParserService
from app.services.chunker import ChunkingService
from app.services.vector_store import EmbeddingService, VectorStoreService
import uuid

router = APIRouter()
vector_store = VectorStoreService()

@router.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    chunk_size: int = Query(500, ge=50, le=4000),
    chunk_overlap: int = Query(50, ge=0, le=500)
):
    try:
        content = await file.read()
        extracted_text = DocumentParserService.parse_file(file.filename, content)
        
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="Document contains no extractable text.")
            
        chunks = ChunkingService.recursive_character_chunking(
            extracted_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        
        chunk_texts = [c["content"] for c in chunks]
        embeddings = EmbeddingService.generate_embeddings(chunk_texts)
        
        doc_id = str(uuid.uuid4())
        stored_count = vector_store.insert_chunks(doc_id, chunks, embeddings)
        
        return {
            "document_id": doc_id,
            "filename": file.filename,
            "extracted_length": len(extracted_text),
            "chunks_count": stored_count,
            "message": "Document successfully parsed, chunked, and vectorized."
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@router.get("/{document_id}/chunks")
async def get_chunks(document_id: str):
    chunks = vector_store.get_document_chunks(document_id)
    if not chunks:
        raise HTTPException(status_code=404, detail="Document chunks not found.")
    return {"document_id": document_id, "chunks_count": len(chunks), "chunks": chunks}
