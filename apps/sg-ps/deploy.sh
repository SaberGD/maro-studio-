#!/usr/bin/env bash
# Deploy a built HORIX package (apps/sg-ps/build.sh) through the Hostinger API, then check it is live.
#
# Usage: HOSTINGER_API_TOKEN=... apps/sg-ps/deploy.sh [deploy/sg-ps/sg-ps-<version>-hostinger.zip]
# Env:   HOSTINGER_API_TOKEN (required)  hPanel > Account > API
#        HOSTINGER_USERNAME  (default u570689065)
#        HORIX_EDITOR_DOMAIN (default horix.live)  editor at the domain root
#        HORIX_DOWNLOAD_DOMAIN (default horix.si)  downloads at the domain root
#        HORIX_LEGACY_DOMAIN (default sabergroupacademy.com)  old paths, redirected after verification
#        HORIX_OLD_DOMAIN    (default studio.engsaber.space)  old address, turned into redirects;
#                            set it empty to skip that step
#
# Each domain receives its own folder's files through TUS; index.html goes last.
# The academy site keeps its WordPress, subdomains, assets and original lead store. Only the two
# old page routes are redirected, after both new sites and the editor's binaries are verified.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
ZIP="${1:-$(ls -t "$REPO"/deploy/sg-ps/sg-ps-*-hostinger.zip | head -1)}"
API="https://developers.hostinger.com/api/hosting/v1"
USERNAME="${HOSTINGER_USERNAME:-u570689065}"
DOMAIN="${HORIX_EDITOR_DOMAIN:-horix.live}"
DOWNLOAD_DOMAIN="${HORIX_DOWNLOAD_DOMAIN:-horix.si}"
LEGACY_DOMAIN="${HORIX_LEGACY_DOMAIN:-sabergroupacademy.com}"
OLD_DOMAIN="${HORIX_OLD_DOMAIN-studio.engsaber.space}"
: "${HOSTINGER_API_TOKEN:?set HOSTINGER_API_TOKEN (hPanel > Account > API)}"
# Hostinger's bot protection answers plain curl with 403: checks use a browser user agent.
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"

[ -f "$ZIP" ] || { echo "error: $ZIP not found; run apps/sg-ps/build.sh first" >&2; exit 1; }
SITE="$(mktemp -d)"
trap 'rm -rf "$SITE"' EXIT
unzip -q "$ZIP" -d "$SITE"
for d in horix downloads; do [ -f "$SITE/$d/index.html" ] || { echo "error: $ZIP has no $d/index.html" >&2; exit 1; }; done
BUILD="$(grep -o 'name="horix-build" content="[^"]*"' "$SITE/horix/index.html" | sed 's/.*content="\([^"]*\)"/\1/')"
[ -n "$BUILD" ] || { echo "error: horix/index.html has no horix-build id" >&2; exit 1; }
echo "deploying build $BUILD to https://$DOMAIN/ and https://$DOWNLOAD_DOMAIN/"

api() {
  curl -fsS -X POST -H "Authorization: Bearer $HOSTINGER_API_TOKEN" -H "Content-Type: application/json" \
    -H "Accept: application/json" "$@"
}
size() { stat -c%s "$1" 2>/dev/null || stat -f%z "$1"; }

# Upload credentials for a domain's public_html (one-time keys).
creds() {
  local c
  c="$(api "$API/files/upload-urls" -d "{\"username\":\"$USERNAME\",\"domain\":\"$1\"}")"
  URL="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["url"])' "$c")"
  AUTH="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["auth_key"])' "$c")"
  REST="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["rest_auth_key"])' "$c")"
}

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

# upload_dir <source folder> <destination prefix>: index.html last.
upload_dir() {
  local f prefix="${2:+$2/}"
  while IFS= read -r -d '' f; do
    upload "$f" "$prefix${f#"$SITE/$1/"}"
  done < <(find "$SITE/$1" -type f ! -path "$SITE/$1/index.html" -print0)
  upload "$SITE/$1/index.html" "${prefix}index.html"
}

# 1) Independent domains: add/overwrite their files only.
creds "$DOMAIN"
upload_dir horix
creds "$DOWNLOAD_DOMAIN"
upload_dir downloads

# 2) Wait until both pages serve this build.
live() { curl -fsS -A "$UA" -H "Cache-Control: no-cache" "$1?v=$RANDOM" 2>/dev/null || true; }
ok=""
for _ in $(seq 1 24); do
  if [[ "$(live "https://$DOMAIN/")" == *"$BUILD"* ]] && [[ "$(live "https://$DOWNLOAD_DOMAIN/")" == *"$BUILD"* ]]; then ok=1; break; fi
  sleep 5
done
[ -n "$ok" ] || { echo "error: the new domains did not serve the expected pages after 2 minutes; old URLs were not redirected" >&2; exit 1; }
echo "live: https://$DOMAIN/ (build $BUILD) and https://$DOWNLOAD_DOMAIN/"
creds "$DOMAIN"

# 3) The WebAssembly must reach every kind of browser intact: fetch it as a Brotli browser, a
#    gzip-only one and one without compression, decode, and compare with the built file. If the
#    host mangles the pre-compressed copies, put back .htaccess without them (uncompressed, but
#    working) and fail the deploy.
WASM_LOCAL="$SITE/horix/sg-ps_bg.wasm"
wasm_ok() {
  local tmp hdr ce ct
  tmp="$(mktemp -d)"
  curl -fsS -A "$UA" -H "Accept-Encoding: $1" -D "$tmp/h" -o "$tmp/body" "https://$DOMAIN/sg-ps_bg.wasm?v=$RANDOM" || return 1
  ce="$(tr -d '\r' < "$tmp/h" | awk 'tolower($1)=="content-encoding:" {print tolower($2)}' | tail -1)"
  ct="$(tr -d '\r' < "$tmp/h" | awk 'tolower($1)=="content-type:" {print tolower($2)}' | tail -1)"
  case "$ce" in
    br) brotli -d -c "$tmp/body" > "$tmp/wasm" || return 1 ;;
    gzip) gzip -d -c "$tmp/body" > "$tmp/wasm" || return 1 ;;
    ""|identity) cp "$tmp/body" "$tmp/wasm" ;;
    *) return 1 ;;
  esac
  [[ "$ct" == application/wasm* ]] || return 1
  cmp -s "$tmp/wasm" "$WASM_LOCAL" || return 1
  echo "  wasm ok for Accept-Encoding '$1': ${ce:-none}, $(size "$tmp/body") bytes on the wire"
}
bad=""
for enc in "gzip, deflate, br" "gzip" "identity"; do wasm_ok "$enc" || { bad="$enc"; break; }; done
if [ -n "$bad" ]; then
  echo "error: the WebAssembly is not served correctly for Accept-Encoding '$bad'; restoring .htaccess without pre-compression" >&2
  upload "$SITE/htaccess-plain" .htaccess
  exit 1
fi

# 3b) The AI selection models are served whole (the page fetches them on first use).
for m in mobile_sam_image_encoder.onnx sam_mask_decoder_multi.onnx isnet_fp16.onnx; do
  want="$(size "$SITE/horix/models/$m")"
  got="$(curl -fsS -A "$UA" -H "Accept-Encoding: identity" -o /dev/null -w '%{size_download}' "https://$DOMAIN/models/$m?v=$RANDOM" || echo 0)"
  [ "$got" = "$want" ] || { echo "error: https://$DOMAIN/models/$m is $got bytes, expected $want" >&2; exit 1; }
  echo "  model ok: $m ($got bytes)"
done

# 4) Redirect only the academy's old page routes. Its assets, waitlist endpoint and data remain.
if [ -n "$LEGACY_DOMAIN" ]; then
  creds "$LEGACY_DOMAIN"
  for pair in "horix:$DOMAIN" "downloads:$DOWNLOAD_DOMAIN"; do
    folder="${pair%%:*}"; target="${pair#*:}"
    rules="$SITE/$folder-redirect.htaccess"
    printf '<IfModule mod_rewrite.c>\nRewriteEngine On\nRewriteCond %%{QUERY_STRING} !(^|&)legacy=1(&|$)\nRewriteRule ^(index\\.html)?$ https://%s/ [R=301,L]\n</IfModule>\n' "$target" > "$rules"
    cat "$SITE/$folder/.htaccess" >> "$rules"
    upload "$rules" "$folder/.htaccess"
    loc="$(curl -sS -o /dev/null -A "$UA" -w '%{redirect_url}' "https://$LEGACY_DOMAIN/$folder/?v=$RANDOM")"
    [[ "$loc" == "https://$target/"* ]] || { echo "error: $LEGACY_DOMAIN/$folder/ redirect verification failed" >&2; exit 1; }
  done
fi

# 5) Update the older studio address by uploading only its redirect files.
if [ -n "$OLD_DOMAIN" ]; then
  creds "$OLD_DOMAIN"
  upload_dir redirect
  echo
  for _ in $(seq 1 24); do
    LOC="$(curl -sS -o /dev/null -A "$UA" -w '%{redirect_url}' "https://$OLD_DOMAIN/?v=$RANDOM" || true)"
    if [[ "$LOC" == "https://$DOMAIN/"* ]]; then echo "redirect: https://$OLD_DOMAIN/ -> $LOC"; exit 0; fi
    sleep 5
  done
  echo "error: https://$OLD_DOMAIN/ does not redirect to https://$DOMAIN/ after 2 minutes" >&2
  exit 1
fi
