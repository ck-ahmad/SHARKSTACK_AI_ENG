# Enterprise RAG Platform (EnterpriseIQ Final)

EnterpriseIQ is a production-grade, secure, scalable Enterprise Retrieval-Augmented Generation (RAG) Platform built with FastAPI, PostgreSQL/pgvector, Hybrid Search (BM25 + Dense Vectors), Reciprocal Rank Fusion (RRF), Multi-Tenancy RBAC, Security Audit Logging, Token/Cost Analytics, and Admin Diagnostics.

## Complete Platform Architecture
- **Phase 1**: Core Foundation, Asynchronous Database Setup, Security & JWT Auth Stubs.
- **Phase 2**: Document Ingestion Pipeline, Multi-format Parsers (PDF, DOCX, TXT, MD), Recursive Chunking & Embedding Generator.
- **Phase 3**: Hybrid Retrieval Engine (BM25 Keyword Search + Cosine Dense Vector Search) fused via Reciprocal Rank Fusion (RRF).
- **Phase 4**: LLM Generation Engine, Prompt Pipeline, Citation & Source Attribution Service (`[Source 1]`, `[Source 2]`).
- **Phase 5**: Multi-Tenancy Engine, Role-Based Access Control (Admin, Analyst, Viewer) & Security Audit Logging.
- **Phase 6 & 7**: Enterprise Analytics Engine, Token & Cost Tracking, Admin Dashboard APIs, System Diagnostics & End-to-End Integration Testing.

## Installation & Setup
1. Clone the repository and navigate to the backend directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure your environment variables.
5. Run Docker services (PostgreSQL & Redis):
   ```bash
   docker-compose up -d
   ```
6. Start the API server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation & Testing
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`
- Run the full test suite with pytest:
  ```bash
  pytest -v
  ```
