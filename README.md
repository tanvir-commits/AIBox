# PrivateAI Box

Local document Q&A for a **single organization** per install — upload files, index them locally, chat with **citations**. Ships as **Docker Compose** (no GPU required for the default demo).

## Download and run (Windows, Docker Desktop installed)

1. **Download** the latest release ZIP:  
   [github.com/tanvir-commits/AIBox/releases](https://github.com/tanvir-commits/AIBox/releases)  
   File: `privateai-box-vX.X.X-windows.zip` (includes `PrivateAIBox.exe` + project files).

   Or clone: `git clone https://github.com/tanvir-commits/AIBox.git`

2. **Unzip** (or `cd AIBox`) so `docker-compose.yml` and `PrivateAIBox.exe` are in the same folder.

3. Start **Docker Desktop** → wait until the engine is **running**.

4. Double-click **`PrivateAIBox.exe`** (or `scripts\start-windows.bat`).

5. First run **downloads images** from the internet (~5–15 min). Browser opens **http://localhost:3000**.

6. Sign in: `admin@example.com` / `changeme` → **Documents** (upload) → **Chat**.

7. Stop: `PrivateAIBox.exe -stop` or `docker compose down` in that folder.

Handout: [`SHARE_WITH_FRIENDS.txt`](SHARE_WITH_FRIENDS.txt)

**Requirements:** Docker Desktop (WSL2), ~8 GB RAM, ports 3000 and 8000 free. **No Ollama required** for testing.

## How it runs (important)

**The app does not install Docker for you.** `./scripts/start.sh` only runs **Docker Compose** on a machine that already has:

- Docker Engine (or Docker Desktop)
- Compose v2 (`docker compose`)
- The Docker **daemon running**

Compose then starts **four containers**: Postgres, Qdrant, the API (`backend`), and the web UI (`web`). Your browser talks to the web container on port **3000**; it proxies API calls to the backend. Uploaded files and databases live in **Docker volumes** on that host.

| If the user… | What happens |
|--------------|----------------|
| Has Docker, runs `./scripts/start.sh --build` | Stack builds (first time) and starts; open http://localhost:3000 |
| Has no Docker | `check_env.sh` / `start.sh` exit with install links — **nothing starts** |
| Docker installed but not running | Check fails with “start Docker Desktop” / `systemctl start docker` |
| Wants zero Docker ever | **Not supported in MVP** — future options: Ubuntu installer (installs Docker), or a **VM/appliance image** with everything preinstalled |

Check prerequisites without starting:

```bash
./scripts/check_env.sh
# or
./scripts/start.sh --check-only
```

## Share with friends (beta)

**Good enough for testing:** Docker Desktop running → start stack → upload one file → chat with citations. No Ollama required.

### Package for a Windows friend (Docker already installed)

**You send them one of:**

1. **Git clone:**  
   `git clone https://github.com/tanvir-commits/AIBox.git` → open folder → start (below).
2. **ZIP of the whole project** (include `docker-compose.yml`, `backend/`, `web/`, `.env.example`, `scripts/`).  
   Optionally include a built **`PrivateAIBox.exe`** in the ZIP root (see build step below).

**They do:**

1. Unzip (or clone) anywhere, e.g. `C:\Users\them\AIBox`
2. Start **Docker Desktop** → wait until the engine is running
3. Start the app — either:
   - Double-click **`PrivateAIBox.exe`** in the project root, **or**
   - Double-click **`scripts\start-windows.bat`**
4. First start: **~5–15 min** is normal (downloading Docker images from GHCR)
5. Browser: **http://localhost:3000** — `admin@example.com` / `changeme`
6. **Documents** → upload `.txt` or `.pdf` → **indexed** → **Chat**

Plain-text handout for friends: [`SHARE_WITH_FRIENDS.txt`](SHARE_WITH_FRIENDS.txt)

**Stop:** `PrivateAIBox.exe -stop` or `docker compose down` in the project folder.

**Build the `.exe` once** (needs [Go](https://go.dev/dl/) on your machine; friends do not need Go):

```bash
./scripts/build-windows-launcher.sh
# → creates PrivateAIBox.exe in repo root; add it to the ZIP you send
```

The exe only **starts Docker Compose and opens the browser** — it is not a standalone app without Docker.

### Prebuilt images (GHCR)

Default `docker compose` **pulls** app images (no local compile):

- `ghcr.io/tanvir-commits/aibox-backend:latest`
- `ghcr.io/tanvir-commits/aibox-web:latest`

Published automatically when **`main`** is pushed (workflow [`.github/workflows/publish-images.yml`](.github/workflows/publish-images.yml)).

**Public repo:** anyone can `docker pull` these without logging in, once the workflow has run at least once. Override tags in `.env` (`PRIVATEAI_BACKEND_IMAGE`, `PRIVATEAI_WEB_IMAGE`).

**Developers** changing code:

```bash
./scripts/start.sh --build
# or: docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

**Mac / Linux:** Docker running, then `./scripts/start.sh --build`.

1. Install **Docker Desktop** ([Windows](https://docs.docker.com/desktop/setup/install/windows-install/) / [Mac](https://docs.docker.com/desktop/setup/install/mac-install/)) or **Docker Engine** on Linux.
2. Open Docker and wait until the engine is **running**.
3. Clone the repo; start as above.
4. Browser: **http://localhost:3000** — `admin@example.com` / `changeme`
5. **Documents** → upload a small `.txt` file → wait for **indexed** → **Chat** → ask something about that file.

### CPU and GPU

| Piece | Default | GPU |
|-------|---------|-----|
| **Embeddings** (indexing) | **CPU** (`fastembed` / ONNX) | Not used in MVP compose |
| **Chat** | **CPU** (`mock_llm` — answers from retrieved chunks) | Optional |
| **Ollama** (real local LLM) | Off unless `DEFAULT_LLM_PROVIDER=ollama` in `.env` | If Ollama runs on the **host** with GPU drivers, it can use the GPU; containers do not get GPU unless you add NVIDIA Container Toolkit config |

**Works without any GPU.** For faster chat, install [Ollama](https://ollama.com) on the host, pull a model, set `DEFAULT_LLM_PROVIDER=ollama`, restart the stack.

**Not ready yet:** a one-file USB you flash and boot without installing Docker — that is on the [roadmap](TODO.md) (bootable image / VM appliance).

## Try it (MVP)

**Requirements:** Docker with Compose v2, ~4 GB free RAM, ports **3000** and **8000** available.

```bash
git clone <your-repo-url> AIBox && cd AIBox
./scripts/start.sh --build
```

Or manually:

```bash
cp .env.example .env   # optional; Compose has safe local defaults
docker compose up --build
```

| | |
|--|--|
| **Web UI** | http://localhost:3000 |
| **API health** | http://localhost:8000/health |
| **Sign-in** | `admin@example.com` / `changeme` |

**5-minute smoke test**

1. Open the web UI and sign in.
2. **Documents** → upload a `.txt` or `.pdf` (also supported: `.docx`, `.md`, `.csv`).
3. Wait until status is **indexed** (first upload may be slower while the embedding model loads).
4. **Chat** → ask a question that is answered by your file → expand **Sources** for citations.

Default chat uses **mock LLM** (extractive answers from retrieved chunks). For a real local model, install [Ollama](https://ollama.com) on the host, pull a model, set `DEFAULT_LLM_PROVIDER=ollama` in `.env`, and restart: `docker compose up --build`.

**Change the admin password** before anything leaves your machine: set `BOOTSTRAP_ADMIN_PASSWORD` and `JWT_SECRET` in `.env`, then `docker compose up --build` on a fresh volume or delete the Postgres volume if you already bootstrapped once.

Stop the stack: `Ctrl+C`, then `docker compose down`. Data persists in Docker volumes until you remove them.

## Supported upload types

| Type | Notes |
|------|--------|
| PDF | Per-page text; scanned/image PDFs may fail with “no extractable text” until OCR exists |
| DOCX | Paragraph text |
| TXT, MD | UTF-8 |
| CSV | Rows flattened to text |

Other extensions are rejected at upload. **One file per upload** today; multi-file/folder upload is on the [backlog](TODO.md).

## Stack

- **Backend** (`backend/`) — FastAPI, JWT auth, Postgres metadata, Qdrant vectors
- **Web** (`web/`) — React + Vite + Tailwind
- **Postgres 16**, **Qdrant 1.12**
- **Embeddings:** `fastembed` (MiniLM ONNX) by default in Compose; `mock_embedding` for fast tests
- **LLM:** `mock_llm` (default) or `ollama` (host Ollama at `OLLAMA_BASE_URL`)

## Configuration

Copy [`.env.example`](.env.example) to `.env`. Common variables:

- `BOOTSTRAP_ADMIN_EMAIL` / `BOOTSTRAP_ADMIN_PASSWORD` — first admin user
- `JWT_SECRET` — change for non-local use
- `DEFAULT_LLM_PROVIDER`, `OLLAMA_*` — local chat model
- `DEFAULT_EMBEDDING_PROVIDER` — `fastembed` or `mock_embedding`

## Tests

```bash
cd backend && pip install -e ".[dev]" && pytest -q -m "not integration"
docker compose -f docker-compose.test.yml run --rm --build backend-test
```

## Roadmap

See [`TODO.md`](TODO.md) and `privateai_cursor_pack/03_PHASED_BUILD_PLAN.md`.

- [x] Auth, documents, RAG chat, citations, system status, Ollama model list (partial)
- [ ] Multi-file upload + async ingest — [TODO.md](TODO.md)
- [ ] Watched folders, installer, appliance image

## License

Proprietary / TBD.
