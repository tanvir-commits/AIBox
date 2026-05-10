# Cursor Implementation Prompt

Build this project incrementally.

Project name:

```text
privateai-box
```

You are building a local AI appliance for SMB document search.

Start with Phase 0 only.

## Immediate task

Create:

- repo structure
- Docker Compose stack
- FastAPI backend
- React/Vite frontend
- PostgreSQL
- Qdrant
- mock LLM provider
- mock embedding provider
- `/health`
- `/api/system/status`
- basic dashboard page
- README
- `.env.example`
- first unit tests

## Hard requirements

1. `docker compose up --build` must work.
2. No GPU required for dev.
3. Tests must use mock providers.
4. Keep code simple.
5. Do not build appliance image yet.
6. Add TODOs for later phases.
7. Keep README updated.
8. Every route should have useful error handling.
9. Every script should have `--help` where practical.
10. Do not use Kubernetes.

## First acceptance test

After implementation:

```bash
docker compose up --build
```

Then:

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"status":"ok"}
```

Frontend:

```text
http://localhost:3000
```

should show dashboard shell.

## Next phases

After Phase 0 passes, continue through:

1. document upload
2. mock RAG
3. real Ollama integration
4. watched folders
5. admin dashboard
6. Ubuntu installer
7. appliance image
8. QEMU appliance tests

Do not skip test strategy.
