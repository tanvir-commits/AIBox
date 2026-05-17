#!/usr/bin/env bash
# Build PrivateAIBox.exe for Windows (amd64). Requires Go 1.22+.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/launcher"

OUT="$ROOT/PrivateAIBox.exe"
GOOS=windows GOARCH=amd64 go build -ldflags="-s -w" -o "$OUT" .

echo "Built: $OUT"
echo "Copy to repo root on Windows (next to docker-compose.yml) or distribute with the full repo."
