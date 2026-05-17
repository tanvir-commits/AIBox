#!/usr/bin/env bash
# Shared compose start: pull prebuilt images (default) or build from source (--build).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

COMPOSE=(docker compose -f docker-compose.yml)
MODE=pull

while [[ $# -gt 0 ]]; do
  case "$1" in
    --build)
      MODE=build
      COMPOSE+=( -f docker-compose.dev.yml )
      shift
      ;;
    *)
      break
      ;;
  esac
done

if [[ "$MODE" == pull ]]; then
  echo "Pulling images (Postgres, Qdrant, and prebuilt app images from GHCR)…"
  "${COMPOSE[@]}" pull
  echo "Starting containers…"
  exec "${COMPOSE[@]}" up -d "$@"
fi

echo "Building and starting from local source (dev mode)…"
exec "${COMPOSE[@]}" up -d --build "$@"
