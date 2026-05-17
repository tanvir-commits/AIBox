#!/usr/bin/env bash
# One-command MVP launcher (Docker Compose).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "${1:-}" == "--check-only" ]]; then
  exec "$ROOT/scripts/check_env.sh"
fi

if ! "$ROOT/scripts/check_env.sh"; then
  exit 1
fi

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example (defaults are fine for local trials)."
fi

EXTRA=()
if [[ "${1:-}" == "--build" ]]; then
  EXTRA=(--build)
  shift
fi

cat <<'EOF'

Starting PrivateAI Box via Docker Compose…
(Postgres, Qdrant, API, and web UI run inside containers on this machine.)

First start downloads images from the internet (GHCR + Docker Hub). Later starts are faster.

  Web UI:  http://localhost:3000
  API:     http://localhost:8000/health

  Sign in: admin@example.com / changeme  (change BOOTSTRAP_* in .env for anything beyond local use)

  Try it:  Documents → upload a .txt or .pdf → Chat → ask about the file

  Stop:    docker compose down

EOF

exec "$ROOT/scripts/compose-up.sh" "${EXTRA[@]}" "$@"
