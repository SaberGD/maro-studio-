#!/usr/bin/env bash
# Deploy a built Horix Vectors / Horix Light web zip through the Hostinger API, then check it is live.
#
# Usage: HOSTINGER_API_TOKEN=... apps/horix-common/deploy-static.sh <zip> <folder in zip> <public domain>
# Env:   HOSTINGER_API_TOKEN (required)  hPanel > Account > API
#        HOSTINGER_USERNAME  (default u570689065)
#        UPLOAD_DOMAIN       the website whose public_html receives the files (default: the public
#                            domain itself). hPanel often puts a subdomain in a folder of its main
#                            domain: then set UPLOAD_DOMAIN=horix.live and UPLOAD_DIR=vectors.
#        UPLOAD_DIR          folder inside that public_html (default: its root)
#
# Files are added or overwritten, never deleted; index.html goes last, so a visitor never gets a
# page whose files are missing.
set -euo pipefail

ZIP="$1"; FOLDER="$2"; DOMAIN="$3"
API="https://developers.hostinger.com/api/hosting/v1"
USERNAME="${HOSTINGER_USERNAME:-u570689065}"
UPLOAD_DOMAIN="${UPLOAD_DOMAIN:-$DOMAIN}"
UPLOAD_DIR="${UPLOAD_DIR:-}"
: "${HOSTINGER_API_TOKEN:?set HOSTINGER_API_TOKEN (hPanel > Account > API)}"
# Hostinger's bot protection answers plain curl with 403: checks use a browser user agent.
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"

[ -f "$ZIP" ] || { echo "error: $ZIP not found; build it first" >&2; exit 1; }
SITE="$(mktemp -d)"
trap 'rm -rf "$SITE"' EXIT
unzip -q "$ZIP" -d "$SITE"
[ -f "$SITE/$FOLDER/index.html" ] || { echo "error: $ZIP has no $FOLDER/index.html" >&2; exit 1; }
BUILD="$(grep -o 'name="horix-build" content="[^"]*"' "$SITE/$FOLDER/index.html" | sed 's/.*content="\([^"]*\)"/\1/')"
[ -n "$BUILD" ] || { echo "error: $FOLDER/index.html has no horix-build id" >&2; exit 1; }
echo "deploying build $BUILD to https://$DOMAIN/ (files: $UPLOAD_DOMAIN/public_html/$UPLOAD_DIR)"

size() { stat -c%s "$1" 2>/dev/null || stat -f%z "$1"; }

c="$(curl -sS -X POST -H "Authorization: Bearer $HOSTINGER_API_TOKEN" -H "Content-Type: application/json" \
  -H "Accept: application/json" "$API/files/upload-urls" -d "{\"username\":\"$USERNAME\",\"domain\":\"$UPLOAD_DOMAIN\"}")"
URL="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1]).get("url", ""))' "$c" 2>/dev/null || true)"
if [ -z "$URL" ]; then
  echo "error: Hostinger has no website $UPLOAD_DOMAIN for user $USERNAME: $c" >&2
  echo "       Add $DOMAIN in hPanel (Websites > Add website, or Domains > Subdomains). If it lives in a" >&2
  echo "       folder of another site, set UPLOAD_DOMAIN and UPLOAD_DIR (repository variables)." >&2
  exit 1
fi
AUTH="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["auth_key"])' "$c")"
REST="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["rest_auth_key"])' "$c")"

# upload <local file> <path inside public_html>: TUS create, then the bytes in one PATCH.
upload() {
  local n off
  n="$(size "$1")"
  curl -fsS -o /dev/null -X POST "${URL%/}/$2?override=true" \
    -H "X-Auth: $AUTH" -H "X-Auth-Rest: $REST" -H "Tus-Resumable: 1.0.0" \
    -H "Upload-Length: $n" -H "Upload-Offset: 0"
  off="$(curl -fsS -D - -o /dev/null -X PATCH "${URL%/}/$2?override=true" \
    -H "X-Auth: $AUTH" -H "X-Auth-Rest: $REST" -H "Tus-Resumable: 1.0.0" \
    -H "Content-Type: application/offset+octet-stream" -H "Upload-Offset: 0" \
    --data-binary "@$1" | tr -d '\r' | awk 'tolower($1)=="upload-offset:" {print $2}')"
  [ "$off" = "$n" ] || { echo "error: $2 upload incomplete ($off of $n bytes)" >&2; exit 1; }
  echo "  $2 ($n bytes)"
}

prefix="${UPLOAD_DIR:+$UPLOAD_DIR/}"
while IFS= read -r -d '' f; do
  upload "$f" "$prefix${f#"$SITE/$FOLDER/"}"
done < <(find "$SITE/$FOLDER" -type f ! -path "$SITE/$FOLDER/index.html" -print0)
upload "$SITE/$FOLDER/index.html" "${prefix}index.html"

# The page must serve this build, and the WebAssembly must arrive whole as application/wasm.
ok=""
for _ in $(seq 1 24); do
  if [[ "$(curl -fsS -A "$UA" -H "Cache-Control: no-cache" "https://$DOMAIN/?v=$RANDOM" 2>/dev/null || true)" == *"$BUILD"* ]]; then ok=1; break; fi
  sleep 5
done
[ -n "$ok" ] || { echo "error: https://$DOMAIN/ did not serve build $BUILD after 2 minutes" >&2; exit 1; }
for w in $(cd "$SITE/$FOLDER" && find . -name '*.wasm' | sed 's#^\./##'); do
  tmp="$(mktemp)"
  ct="$(curl -fsS -A "$UA" -H "Accept-Encoding: identity" -o "$tmp" -w '%{content_type}' "https://$DOMAIN/$w?v=$RANDOM")"
  [[ "$ct" == application/wasm* ]] || { echo "error: $w is served as '$ct', not application/wasm" >&2; exit 1; }
  cmp -s "$tmp" "$SITE/$FOLDER/$w" || { echo "error: $w on the server differs from the build" >&2; exit 1; }
  rm -f "$tmp"
  echo "  wasm ok: $w"
done
echo "live: https://$DOMAIN/ (build $BUILD)"
