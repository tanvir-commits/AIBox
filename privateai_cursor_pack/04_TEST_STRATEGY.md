# PrivateAI Box — Test Strategy

## 1. Core Principle

Every feature must have a CPU-only test path.

The product eventually uses GPUs, Ollama, and bootable appliance images, but Cursor must be able to develop and test most logic without a GPU.

---

## 2. Test Layers

```text
Layer 1: Unit tests
Layer 2: Docker integration tests
Layer 3: Browser E2E tests
Layer 4: Ollama/GPU optional tests
Layer 5: Ubuntu installer tests
Layer 6: QEMU appliance image tests
Layer 7: Bare-metal manual GPU tests
```

---

## 3. Unit Tests

Use:

```bash
pytest
```

Test:

- file hashing
- PDF parsing
- DOCX parsing
- text chunking
- metadata models
- auth logic
- prompt construction
- citation formatting
- mock LLM
- mock embeddings

Cursor must run these frequently.

---

## 4. Integration Tests

Use:

```bash
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

Test:

- backend connects to PostgreSQL
- backend connects to Qdrant
- document upload API works
- ingestion worker stores chunks
- vector search returns expected chunks
- RAG endpoint returns cited answer

Use mock providers by default.

---

## 5. Browser E2E Tests

Use Playwright.

Command:

```bash
npm run test:e2e
```

Test:

1. Login
2. Upload sample document
3. Wait for indexed status
4. Ask question
5. Verify answer
6. Verify citation visible
7. Open citation panel
8. Add watched folder
9. Trigger scan
10. Open admin dashboard

---

## 6. Mock LLM Strategy

Tests must not require real Ollama.

Implement:

```text
mock_llm
mock_embedding
```

Mock embedding can generate deterministic vectors from text hash.

Mock LLM can:

- return answer if context contains keyword
- return "I could not find that..." if no context
- include citation list

This lets Cursor test the full product without GPU.

---

## 7. Optional GPU Tests

GPU tests are skipped unless:

```bash
ENABLE_GPU_TESTS=1
```

Run:

```bash
ENABLE_GPU_TESTS=1 pytest tests/gpu
```

Test:

- `nvidia-smi` works
- Docker can see GPU
- Ollama responds
- model is loaded
- embedding generated
- inference works
- VRAM is detected

If no GPU, tests must skip cleanly.

---

## 8. Installer Tests

Test `scripts/install_ubuntu.sh` in an Ubuntu VM.

The installer should support dry-run mode:

```bash
sudo ./scripts/install_ubuntu.sh --dry-run
```

And test mode:

```bash
sudo ./scripts/install_ubuntu.sh --test-mode
```

Test mode should:

- use mock model
- skip giant model download
- skip GPU requirement
- start services
- expose setup wizard

---

## 9. Appliance Image Tests

Cursor should automate this with QEMU.

Build image:

```bash
./scripts/build_appliance_image.sh
```

Boot image:

```bash
./scripts/qemu_boot_image.sh ./images/privateai-box.img
```

Run full image test:

```bash
./scripts/qemu_test_image.sh ./images/privateai-box.img
```

The QEMU test should:

1. Launch VM
2. Forward host port `8080` to guest port `80`
3. Wait for web server
4. Check `/health`
5. Run setup wizard through API or Playwright
6. Upload sample document
7. Ask test question
8. Verify citation
9. Reboot VM
10. Verify data persists

---

## 10. Manual Bare-Metal Acceptance Tests

Use a spare SSD or USB SSD.

Steps:

1. Flash `privateai-box.img`
2. Boot real PC from it
3. Complete setup wizard
4. Verify `nvidia-smi`
5. Verify Docker GPU access
6. Verify Ollama GPU mode
7. Upload documents
8. Ask questions from another laptop on LAN
9. Reboot
10. Verify persistence

---

## 11. Sample Test Documents

Create a folder:

```text
tests/fixtures/documents/
```

Include:

```text
employee_handbook.txt
clinic_policy.txt
legal_contract_sample.txt
engineering_sop.md
```

Example known answer test:

Document contains:

```text
The emergency contact procedure requires staff to notify the office manager within 15 minutes.
```

Question:

```text
How fast do staff need to notify the office manager?
```

Expected:

```text
within 15 minutes
```

Citation required.

---

## 12. CI Strategy

GitHub Actions should run:

- backend lint
- frontend lint
- unit tests
- integration tests with mock providers
- frontend build
- Docker build

Do not run GPU tests in normal CI.
Do not run full QEMU image tests in normal CI initially unless fast enough.

---

## 13. Test Acceptance Summary

A phase is not done unless:

- app runs
- tests pass
- README updated
- Docker Compose still works
- mock provider path works
- no GPU required for normal dev
