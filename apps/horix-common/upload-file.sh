#!/usr/bin/env bash
# Upload one file to a Hostinger website through the API (TUS), replacing what is there.
#
# Usage: HOSTINGER_API_TOKEN=... apps/horix-common/upload-file.sh <local file> <domain> <path in public_html>
# Env:   HOSTINGER_USERNAME (default u570689065)
set -euo pipefail

FILE="$1"; DOMAIN="$2"; DEST="$3"
API="https://developers.hostinger.com/api/hosting/v1"
USERNAME="${HOSTINGER_USERNAME:-u570689065}"
: "${HOSTINGER_API_TOKEN:?set HOSTINGER_API_TOKEN (hPanel > Account > API)}"
[ -f "$FILE" ] || { echo "error: $FILE not found" >&2; exit 1; }

c="$(curl -fsS -X POST -H "Authorization: Bearer $HOSTINGER_API_TOKEN" -H "Content-Type: application/json" \
  -H "Accept: application/json" "$API/files/upload-urls" -d "{\"username\":\"$USERNAME\",\"domain\":\"$DOMAIN\"}")"
URL="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["url"])' "$c")"
AUTH="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["auth_key"])' "$c")"
REST="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["rest_auth_key"])' "$c")"
size() { stat -c%s "$1" 2>/dev/null || stat -f%z "$1"; }
n="$(size "$FILE")"
curl -fsS -o /dev/null -X POST "${URL%/}/$DEST?override=true" \
  -H "X-Auth: $AUTH" -H "X-Auth-Rest: $REST" -H "Tus-Resumable: 1.0.0" -H "Upload-Length: $n" -H "Upload-Offset: 0"
# The bytes in 64 MB PATCH requests: one request the size of a whole download may be refused.
off=0; part="$(mktemp)"
trap 'rm -f "$part"' EXIT
while [ "$off" -lt "$n" ]; do
  dd if="$FILE" of="$part" bs=1048576 skip=$((off / 1048576)) count=64 status=none
  got="$(curl -fsS -D - -o /dev/null -X PATCH "${URL%/}/$DEST?override=true" \
    -H "X-Auth: $AUTH" -H "X-Auth-Rest: $REST" -H "Tus-Resumable: 1.0.0" \
    -H "Content-Type: application/offset+octet-stream" -H "Upload-Offset: $off" \
    --data-binary "@$part" | tr -d '\r' | awk 'tolower($1)=="upload-offset:" {print $2}')"
  [ -n "$got" ] && [ "$got" -gt "$off" ] || { echo "error: $DEST upload stalled at $off of $n bytes" >&2; exit 1; }
  off="$got"
done
[ "$off" = "$n" ] || { echo "error: $DEST upload incomplete ($off of $n bytes)" >&2; exit 1; }
echo "uploaded $DEST to $DOMAIN ($n bytes)"
