#!/usr/bin/env bash
# Verify host can run PrivateAI Box via Docker Compose. Exit 0 if OK, 1 otherwise.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail=0

_os_hint() {
  case "$(uname -s 2>/dev/null || echo unknown)" in
    Darwin)
      echo "  macOS: install Docker Desktop — https://docs.docker.com/desktop/setup/install/mac-install/"
      ;;
    Linux)
      echo "  Linux: Docker Engine + Compose plugin — https://docs.docker.com/engine/install/"
      ;;
    MINGW*|MSYS*|CYGWIN*)
      echo "  Windows: install Docker Desktop — https://docs.docker.com/desktop/setup/install/windows-install/"
      ;;
    *)
      echo "  Install Docker Engine and the Compose v2 plugin from https://docs.docker.com/get-docker/"
      ;;
  esac
}

echo "PrivateAI Box — environment check"
echo

if ! command -v docker >/dev/null 2>&1; then
  echo "FAIL: docker not found in PATH."
  _os_hint
  echo
  echo "This app does not install Docker for you. After installing, re-run:"
  echo "  ./scripts/start.sh --build"
  fail=1
else
  echo "OK:   docker $(docker --version 2>/dev/null | head -1)"
fi

if [[ "$fail" -eq 0 ]] && ! docker compose version >/dev/null 2>&1; then
  echo "FAIL: docker compose (v2 plugin) not available."
  echo "  Install the Compose plugin: https://docs.docker.com/compose/install/linux/"
  fail=1
elif [[ "$fail" -eq 0 ]]; then
  echo "OK:   $(docker compose version --short 2>/dev/null || docker compose version)"
fi

if [[ "$fail" -eq 0 ]] && ! docker info >/dev/null 2>&1; then
  echo "FAIL: Docker daemon is not running (or you lack permission)."
  echo "  Start Docker Desktop, or: sudo systemctl start docker"
  fail=1
elif [[ "$fail" -eq 0 ]]; then
  echo "OK:   Docker daemon is running"
fi

_port_in_use() {
  local port="$1"
  if command -v ss >/dev/null 2>&1; then
    ss -tln 2>/dev/null | grep -q ":${port} "
  elif command -v lsof >/dev/null 2>&1; then
    lsof -iTCP:"${port}" -sTCP:LISTEN -t >/dev/null 2>&1
  else
    return 1
  fi
}

for port in 3000 8000; do
  if _port_in_use "$port"; then
    echo "WARN: port ${port} is already in use — compose may fail to bind."
  else
    echo "OK:   port ${port} appears free"
  fi
done

if [[ ! -f "$ROOT/.env" ]]; then
  echo "NOTE: no .env file — start.sh will copy .env.example on first launch."
else
  echo "OK:   .env present"
fi

echo
if [[ "$fail" -ne 0 ]]; then
  echo "Fix the issues above, then run: ./scripts/start.sh --build"
  exit 1
fi

echo "Ready. Start with: ./scripts/start.sh --build"
exit 0
