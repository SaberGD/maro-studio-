#!/usr/bin/env bash
# Deploy a built SG - PS package to Hostinger through the Hostinger API, then check it is live.
#
# Usage: HOSTINGER_API_TOKEN=... apps/sg-ps/deploy.sh [deploy/sg-ps/sg-ps-<version>-hostinger.zip]
# Env:   HOSTINGER_API_TOKEN (required)  hPanel > Account > API
#        HOSTINGER_USERNAME  (default u570689065)
#        SGPS_DOMAIN         (default studio.engsaber.space)
#
# Steps: 1) ask Hostinger for a file-upload URL, 2) upload the zip with TUS, 3) "Deploy static site
# archive" (unpacks it over the site's folder), 4) poll the site until it serves the new build.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
ZIP="${1:-$(ls -t "$REPO"/deploy/sg-ps/sg-ps-*-hostinger.zip | head -1)}"
API="https://developers.hostinger.com/api/hosting/v1"
USERNAME="${HOSTINGER_USERNAME:-u570689065}"
DOMAIN="${SGPS_DOMAIN:-studio.engsaber.space}"
: "${HOSTINGER_API_TOKEN:?set HOSTINGER_API_TOKEN (hPanel > Account > API)}"

[ -f "$ZIP" ] || { echo "error: $ZIP not found; run apps/sg-ps/build.sh first" >&2; exit 1; }
NAME="$(basename "$ZIP")"
SIZE="$(stat -c%s "$ZIP" 2>/dev/null || stat -f%z "$ZIP")"
# The build's JS file name carries a content hash: the live page must reference it when done.
EXPECT="$(unzip -p "$ZIP" index.html | grep -o 'sg-ps-[0-9a-f]*\.js' | head -1)"
echo "deploying $NAME ($SIZE bytes, $EXPECT) to $DOMAIN"

api() {
  curl -fsS -X POST -H "Authorization: Bearer $HOSTINGER_API_TOKEN" -H "Content-Type: application/json" \
    -H "Accept: application/json" "$@"
}

# 1) Upload URL and one-time credentials for the site's file storage.
CREDS="$(api "$API/files/upload-urls" -d "{\"username\":\"$USERNAME\",\"domain\":\"$DOMAIN\"}")"
field() { python3 -c 'import json,sys; print(json.loads(sys.argv[1])[sys.argv[2]])' "$CREDS" "$1"; }
URL="$(field url)"; AUTH="$(field auth_key)"; REST="$(field rest_auth_key)"

# 2) TUS upload: create, then send the bytes in one PATCH.
curl -fsS -o /dev/null -X POST "${URL%/}/$NAME?override=true" \
  -H "X-Auth: $AUTH" -H "X-Auth-Rest: $REST" -H "Tus-Resumable: 1.0.0" \
  -H "Upload-Length: $SIZE" -H "Upload-Offset: 0"
OFFSET="$(curl -fsS -D - -o /dev/null -X PATCH "${URL%/}/$NAME?override=true" \
  -H "X-Auth: $AUTH" -H "X-Auth-Rest: $REST" -H "Tus-Resumable: 1.0.0" \
  -H "Content-Type: application/offset+octet-stream" -H "Upload-Offset: 0" \
  --data-binary "@$ZIP" | tr -d '\r' | awk 'tolower($1)=="upload-offset:" {print $2}')"
[ "$OFFSET" = "$SIZE" ] || { echo "error: upload incomplete ($OFFSET of $SIZE bytes)" >&2; exit 1; }
echo "uploaded"

# 3) Unpack over the site (replaces its previous files).
api "$API/accounts/$USERNAME/websites/$DOMAIN/deploy" -d "{\"archive_path\":\"$NAME\"}"
echo

# 4) Wait until the live page serves this build. A browser user agent: Hostinger's bot
#    protection answers plain curl with 403.
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
for _ in $(seq 1 24); do
  # Read the whole page first: `curl | grep -q` fails under pipefail when grep stops early.
  PAGE="$(curl -fsS -A "$UA" -H "Cache-Control: no-cache" "https://$DOMAIN/?v=$RANDOM" || true)"
  if [[ "$PAGE" == *"$EXPECT"* ]]; then
    echo "live: https://$DOMAIN/ serves $EXPECT"
    exit 0
  fi
  sleep 5
done
echo "error: https://$DOMAIN/ does not serve $EXPECT after 2 minutes" >&2
exit 1
