#!/usr/bin/env bash
# Download a bundle of public PDFs and upload them to a running PrivateAI Box API.
# Usage:
#   export API_BASE=http://127.0.0.1:8000
#   export ADMIN_EMAIL=admin@example.com
#   export ADMIN_PASSWORD=changeme
#   ./scripts/seed_demo_pdfs.sh

set -euo pipefail
API_BASE="${API_BASE:-http://127.0.0.1:8000}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@example.com}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-changeme}"
DIR="$(cd "$(dirname "$0")/.." && pwd)/sample-pdfs"
mkdir -p "$DIR"

echo "Logging in to ${API_BASE}..."
TOKEN="$(curl -fsS -X POST "${API_BASE}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASSWORD}\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")"

fetch() {
  local url="$1" out="$2"
  if [[ -f "$out" ]]; then
    echo "  skip (exists): $out"
    return
  fi
  echo "  fetch $out"
  curl -fsSL -o "$out" "$url"
}

echo "Downloading PDFs into $DIR ..."
fetch "https://arxiv.org/pdf/1706.03762.pdf" "$DIR/attention.pdf"
fetch "https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.197.pdf" "$DIR/nist-crypto.pdf"
fetch "https://mozilla.github.io/pdf.js/web/compressed.tracemonkey-pldi-09.pdf" "$DIR/tracemonkey.pdf"
fetch "https://arxiv.org/pdf/1409.0473.pdf" "$DIR/seq2seq-bahdanau.pdf"

echo "Uploading..."
for f in "$DIR"/*.pdf; do
  [[ -e "$f" ]] || continue
  echo "  upload $(basename "$f")"
  curl -fsS -X POST "${API_BASE}/api/documents/upload" \
    -H "Authorization: Bearer ${TOKEN}" \
    -F "file=@${f};filename=$(basename "$f")" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status'), d.get('filename'), d.get('chunk_count'))"
done

echo "Done. List: curl -s -H \"Authorization: Bearer \$TOKEN\" ${API_BASE}/api/documents"
