# PrivateAI Box

Local AI appliance for SMB document search — **Phases 0–3** (Compose bootstrap, app shell, auth, document upload + indexing).

## Quick start

```bash
cp .env.example .env   # optional; Compose has defaults
docker compose up --build
```

- **Frontend:** http://localhost:3000 (sign-in required)  
- **Backend:** http://localhost:8000  
- **Health (public):** `curl http://localhost:8000/health` → `{"status":"ok"}`  

**Default sign-in (Compose / `.env.example`):**

- Email: `admin@example.com`  
- Password: `changeme`  

**System status (requires Bearer token):**

```bash
TOKEN=$(curl -sS -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"changeme"}' | jq -r .access_token)
curl -sS http://localhost:8000/api/system/status \
  -H "Authorization: Bearer $TOKEN"
```

(`email-validator` rejects `.local` addresses; use `example.com` for dev.)

## Stack

- FastAPI backend (`backend/`) — JWT auth, Postgres-backed users, bootstrap admin
- React + Vite + Tailwind + React Router (`web/`) — sidebar shell, protected routes, documents UI
- PostgreSQL 16, Qdrant 1.12
- **Mock** LLM and embedding providers (CPU-only; no GPU) — used for chunk embeddings in Phase 3

## Tests

**Unit tests** (no containers required):

```bash
cd backend && pip install -e ".[dev]" && pytest -q -m "not integration"
```

**Integration tests** (Postgres + Qdrant via Compose):

```bash
docker compose -f docker-compose.test.yml run --rm --build backend-test
```

CI (`.github/workflows/ci.yml`) runs unit tests, `npm run build` for the web app, `docker compose build`, and the Compose integration job on pushes and pull requests.

If you run the **web dev server on the host** (`npm run dev`), the Vite proxy targets `http://127.0.0.1:8000` by default; start the backend (Compose or `uvicorn`). In Docker, `VITE_PROXY_API=http://backend:8000` is set in the web image.

## Scripts

```bash
./scripts/dev_start.sh --help
```

## Roadmap (from spec)

See `privateai_cursor_pack/` for full phases.

- [x] Phase 0 — Compose, health, system status, mocks, tests  
- [x] Phase 1 — Web shell (nav + placeholder pages)  
- [x] Phase 2 — Local auth (JWT), roles on user, bootstrap admin  
- [x] Phase 3 — Document upload (pdf/docx/txt/md/csv), parse → chunk → mock embed → Qdrant + Postgres metadata  
- [ ] Phase 4 — Mock RAG chat with citations  
- [ ] Phase 5 — Ollama integration (`ENABLE_GPU_TESTS=1` optional)  
- [ ] Later — watched folders, admin metrics, Ubuntu installer, appliance image, QEMU  

## License

Proprietary / TBD.
