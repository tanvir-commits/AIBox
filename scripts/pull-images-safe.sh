#!/usr/bin/env bash
# Pull images one service at a time (easier on RAM/disk than "docker compose pull" at once).
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! docker info >/dev/null 2>&1; then
  echo "Docker is not running. Start Docker Desktop first."
  exit 1
fi

SERVICES=(postgres qdrant backend web)

echo "Pulling images one at a time (reduces freezes on first install)…"
echo "Need ~6–10 GB free disk and 8 GB+ RAM for Docker Desktop."
echo

for svc in "${SERVICES[@]}"; do
  echo "── $svc ──"
  if ! docker compose pull "$svc"; then
    echo "Warning: pull failed for $svc (will retry on start or use local build)."
  fi
  echo
done

echo "Done (some layers may retry on start). Next: docker compose up -d"
exit 0
