# PrivateAI Box — Cursor Start Here

You are building **PrivateAI Box**, a local AI appliance for small businesses.

The product is a private, local, ChatGPT-like document assistant that runs on an Ubuntu AI box. Office users access it from Windows/Mac PCs through a browser at:

```text
http://privateai.local
```

## What to build first

Do not build the whole system at once.

Start with:

1. Docker Compose development stack
2. Backend health API
3. Frontend dashboard shell
4. PostgreSQL
5. Qdrant
6. Mock LLM provider
7. Mock embedding provider
8. Document upload skeleton
9. Basic tests

The first runnable command must be:

```bash
docker compose up --build
```

Expected URLs:

```text
Frontend: http://localhost:3000
Backend:  http://localhost:8000
```

## Product direction

This eventually becomes a bootable Ubuntu appliance image:

```text
PrivateAI_Box.img
```

The image should boot on a PC, start services, expose a setup wizard, and behave like a Synology/Ubiquiti/Home Assistant style appliance.

## Critical engineering rule

Every feature must have a CPU-only test path.

GPU/Ollama tests must be optional and skipped unless:

```bash
ENABLE_GPU_TESTS=1
```

## Cursor workflow

For each phase:

1. Implement working code
2. Add tests
3. Update README
4. Keep Docker Compose working
5. Do not overbuild
6. Do not add unnecessary abstractions
7. Prefer boring, debuggable code

Read these files in order:

1. `01_PRODUCT_SPEC.md`
2. `02_ARCHITECTURE.md`
3. `03_PHASED_BUILD_PLAN.md`
4. `04_TEST_STRATEGY.md`
5. `05_APPLIANCE_IMAGE_AND_QEMU.md`
6. `06_SECURITY_AND_DEPLOYMENT.md`
