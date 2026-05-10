#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: dev_start.sh [options]

Start the PrivateAI Box stack with Docker Compose (same as Phase 0 default).

Options:
  --build     Pass --build to docker compose up
  -h, --help  Show this help

Examples:
  ./scripts/dev_start.sh
  ./scripts/dev_start.sh --build
EOF
}

BUILD_FLAG=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --build)
      BUILD_FLAG=(--build)
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
exec docker compose up "${BUILD_FLAG[@]}"
