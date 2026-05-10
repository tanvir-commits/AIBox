# PrivateAI Box — Phased Build Plan

## Phase 0 — Bootstrap

Goal:
Create a runnable skeleton.

Deliverables:

- Repo structure
- Docker Compose
- Backend container
- Frontend container
- PostgreSQL container
- Qdrant container
- `.env.example`
- README
- `/health`

Command:

```bash
docker compose up --build
```

Acceptance:

- Backend responds at `http://localhost:8000/health`
- Frontend loads at `http://localhost:3000`
- PostgreSQL healthy
- Qdrant healthy

---

## Phase 1 — Web App Shell

Pages:

- Login
- Dashboard
- Chat
- Documents
- Sources
- Models
- System
- Settings

Use dark mode by default.

Keep UI serious and office-friendly.

---

## Phase 2 — Auth and Roles

Implement local auth.

Roles:

```text
owner
admin
user
read_only
```

Do not add SSO yet.

---

## Phase 3 — Document Upload

Support:

- PDF
- DOCX
- TXT
- MD
- CSV

Flow:

```text
upload
 -> save original
 -> calculate sha256
 -> create document row
 -> parse
 -> chunk
 -> embed
 -> store vectors
 -> update status=indexed
```

Status states:

```text
uploaded
parsing
parsed
embedding
indexed
failed
```

---

## Phase 4 — Mock RAG Chat

Use mock providers first.

Goal:
Full RAG flow works without real GPU.

Mock LLM behavior:

- returns deterministic answer
- includes citations
- says not found when no chunks

Acceptance:

- upload sample document
- ask known question
- get answer with citation

---

## Phase 5 — Ollama Integration

Add:

- Ollama LLM provider
- Ollama embedding provider
- model list
- model pull
- default model setting

GPU tests optional.

Must work CPU-only, though slower.

---

## Phase 6 — Watched Folders

Admin can add local/mounted folders.

Supported first:

- local path
- mounted SMB/NAS path
- synced OneDrive/Dropbox/Google Drive folder

Do not build OAuth connectors yet.

Scan logic:

- initial full scan
- hash files
- skip unchanged
- reindex changed
- mark missing files unavailable

---

## Phase 7 — Citations and Source Viewer

Answers must show clickable citations.

Citation panel shows:

- filename
- page number if available
- chunk text
- surrounding text
- source path if allowed

---

## Phase 8 — Admin System Dashboard

Show:

- CPU
- RAM
- disk
- GPU if available
- VRAM if available
- Docker services
- Ollama status
- Qdrant status
- Postgres status
- document count
- failed indexing jobs
- active users
- recent errors

---

## Phase 9 — Backup and Restore

Scripts:

```bash
./scripts/backup.sh /backup/privateai
./scripts/restore.sh /backup/privateai/latest
```

Backup:

- PostgreSQL
- Qdrant
- configs
- users
- uploaded files if selected

---

## Phase 10 — Ubuntu Installer

Build:

```bash
scripts/install_ubuntu.sh
```

It should:

1. Check Ubuntu version
2. Check internet
3. Check NVIDIA GPU
4. Install Docker
5. Install NVIDIA Container Toolkit when GPU exists
6. Pull images
7. Generate secrets
8. Install systemd service
9. Configure nginx
10. Configure firewall defaults
11. Start services
12. Print setup URL

---

## Phase 11 — Appliance Image

Build:

```bash
scripts/build_appliance_image.sh
```

Output:

```text
privateai-box.img
```

Image must boot into first-run setup wizard.

Do not embed secrets.

Generate secrets on first boot.

---

## Phase 12 — QEMU Appliance Testing

Add:

```bash
scripts/qemu_boot_image.sh
scripts/qemu_test_image.sh
```

Cursor should be able to:

1. Build image
2. Boot it in QEMU
3. Wait for health endpoint
4. Run Playwright tests
5. Reboot image
6. Verify persistence

---

## Phase 13 — Security Hardening

Add:

- HTTPS local cert option
- audit logs
- rate limiting
- session timeout
- password policy
- LAN-only default
- firewall defaults
- support bundle export

Do not claim HIPAA/SOC2/legal compliance.

---

## Phase 14 — Better Retrieval

Add:

- hybrid search
- reranking
- query rewrite
- folder filters
- date filters
- document filters
- evaluation tests

---

## Phase 15 — Commercial Packaging

Add:

- license key
- offline activation
- update channel
- support bundle
- branding
- onboarding wizard

Support bundle must not include customer documents.
