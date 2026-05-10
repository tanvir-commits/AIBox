# PrivateAI Box — Architecture

## 1. High-Level Architecture

```text
LAN Users
   |
   v
nginx Reverse Proxy
   |
   v
PrivateAI Backend API
 ├── Auth Service
 ├── Chat Service
 ├── Document Service
 ├── Source Service
 ├── Model Service
 ├── Admin Service
 ├── Backup Service
 └── RAG Service
   |
   +--------------------+
   |                    |
   v                    v
PostgreSQL          Qdrant
Metadata DB         Vector DB
   |
   v
Local File Storage
   |
   v
Document Ingestion Worker
   |
   v
Ollama / vLLM
```

---

## 2. Recommended Tech Stack

### Backend

Use:

- Python 3.11+
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- pytest

### Frontend

Use:

- React
- TypeScript
- Vite
- Tailwind
- shadcn/ui or equivalent

### AI Runtime

Phase 1:

- Ollama

Phase 2:

- Optional vLLM backend

### Vector Database

- Qdrant

### Metadata Database

- PostgreSQL

### Reverse Proxy

- nginx

### Deployment

- Docker Compose first
- systemd wrapper for appliance mode

---

## 3. Repo Structure

Create this repo:

```text
privateai-box/
├── README.md
├── docker-compose.yml
├── docker-compose.test.yml
├── .env.example
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── rag/
│   │   ├── workers/
│   │   └── security/
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── web/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── ingestion/
│   ├── parsers/
│   ├── chunkers/
│   ├── embeddings/
│   ├── watchers/
│   └── workers/
├── appliance/
│   ├── firstboot/
│   ├── image-build/
│   ├── nginx/
│   ├── qemu/
│   └── systemd/
├── scripts/
│   ├── dev_start.sh
│   ├── install_ubuntu.sh
│   ├── build_appliance_image.sh
│   ├── qemu_boot_image.sh
│   ├── qemu_test_image.sh
│   ├── backup.sh
│   ├── restore.sh
│   └── reset_factory.sh
├── tests/
│   ├── integration/
│   ├── gpu/
│   └── appliance/
├── e2e/
│   └── playwright/
└── docs/
```

---

## 4. Core Backend Objects

### User

```python
class User:
    id: str
    email: str
    password_hash: str
    role: str
    created_at: datetime
    last_login_at: datetime | None
```

### Document

```python
class Document:
    id: str
    filename: str
    file_type: str
    file_size: int
    sha256: str
    source_type: str
    source_path: str
    status: str
    page_count: int | None
    chunk_count: int
    created_at: datetime
    updated_at: datetime
```

### DocumentChunk

```python
class DocumentChunk:
    id: str
    document_id: str
    chunk_index: int
    page_number: int | None
    text: str
    token_count: int
    qdrant_point_id: str
```

### Source

```python
class Source:
    id: str
    name: str
    source_type: str
    path: str
    enabled: bool
    scan_interval_seconds: int
    last_scan_at: datetime | None
```

### ChatSession

```python
class ChatSession:
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
```

### ChatMessage

```python
class ChatMessage:
    id: str
    session_id: str
    role: str
    content: str
    citations: list
    created_at: datetime
```

---

## 5. API Routes

### Health

```http
GET /health
GET /api/system/status
```

### Auth

```http
POST /api/auth/login
POST /api/auth/logout
GET /api/auth/me
```

### Documents

```http
GET /api/documents
GET /api/documents/{id}
POST /api/documents/upload
DELETE /api/documents/{id}
POST /api/documents/{id}/reindex
```

### Sources

```http
GET /api/sources
POST /api/sources
PATCH /api/sources/{id}
DELETE /api/sources/{id}
POST /api/sources/{id}/scan
```

### Chat

```http
POST /api/chat
GET /api/chat/sessions
GET /api/chat/sessions/{id}
DELETE /api/chat/sessions/{id}
```

### Models

```http
GET /api/models
POST /api/models/pull
DELETE /api/models/{name}
POST /api/models/default
```

### Admin

```http
GET /api/admin/system
GET /api/admin/logs
GET /api/admin/audit
POST /api/admin/backup
POST /api/admin/restore
```

---

## 6. RAG Pipeline

```text
User question
    |
    v
Create query embedding
    |
    v
Search Qdrant
    |
    v
Fetch top chunks
    |
    v
Build grounded prompt
    |
    v
Send to LLM provider
    |
    v
Return answer with citations
```

---

## 7. LLM Provider Interface

Implement provider abstraction early.

```python
class LLMProvider:
    def generate(self, prompt: str, stream: bool = False) -> str:
        ...

class EmbeddingProvider:
    def embed(self, text: str) -> list[float]:
        ...
```

Providers:

```text
mock_llm
mock_embedding
ollama_llm
ollama_embedding
```

Default test provider:

```text
mock_llm
mock_embedding
```

This is critical so Cursor can test without GPU.
