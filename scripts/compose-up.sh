#!/usr/bin/env bash
# Shared compose start: pull prebuilt images (default) or build from source (--build).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

COMPOSE=(docker compose -f docker-compose.yml)
DEV_COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.dev.yml)
MODE=pull

while [[ $# -gt 0 ]]; do
  case "$1" in
    --build)
      MODE=build
      shift
      ;;
    *)
      break
      ;;
  esac
done

if [[ "$MODE" == build ]]; then
  echo "Building and starting from local source (dev mode)…"
  exec "${DEV_COMPOSE[@]}" up -d --build "$@"
fi

echo "Pulling images (Postgres, Qdrant, and prebuilt app images from GHCR)…"
if ! "${COMPOSE[@]}" pull; then
  echo ""
  echo "⚠  Pull from GHCR failed (packages are often private until set to Public)."
  echo "   Fix: https://github.com/users/$(whoami 2>/dev/null || echo YOU)/packages → aibox-backend / aibox-web → Public"
  echo "   Falling back to local build (slower, needs internet)…"
  echo ""
  exec "${DEV_COMPOSE[@]}" up -d --build "$@"
fi

echo "Starting containers…"
exec "${COMPOSE[@]}" up -d "$@"
