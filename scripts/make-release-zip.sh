#!/usr/bin/env bash
# Local release ZIP (same layout as CI). Requires: git, zip, Go for exe.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VERSION="${1:-local}"
OUT="privateai-box-${VERSION}-windows.zip"
STAGING="privateai-box-${VERSION}"

rm -rf "$STAGING" "$OUT"
mkdir -p "$STAGING"
git archive HEAD | tar -x -C "$STAGING"

if [[ ! -f PrivateAIBox.exe ]]; then
  "$ROOT/scripts/build-windows-launcher.sh"
fi
cp PrivateAIBox.exe "$STAGING/"
cp SHARE_WITH_FRIENDS.txt "$STAGING/"

( cd "$STAGING" && zip -r "../$OUT" . )
rm -rf "$STAGING"
echo "Created: $ROOT/$OUT"
