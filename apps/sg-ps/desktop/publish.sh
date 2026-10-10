#!/usr/bin/env bash
# Publish the HORIX desktop zips on engsaber.space/sgps-downloads/ (the download page at
# sabergroupacademy.com/downloads/ links there), through the Hostinger file-upload API.
#
# Usage: HOSTINGER_API_TOKEN=... apps/sg-ps/desktop/publish.sh <dir with the zips> <build label>
# Env:   HOSTINGER_USERNAME (default u570689065), SGPS_DOWNLOAD_DOMAIN (default engsaber.space)
#
# Stable names (HORIX-windows-x64.zip, HORIX-macos-universal.zip) are overwritten each release;
# latest.json (version, build, date, sizes) goes last, so the page never points at a half upload.
set -euo pipefail

DIR="${1:?usage: publish.sh <dir> <build>}"
BUILD="${2:?usage: publish.sh <dir> <build>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USERNAME="${HOSTINGER_USERNAME:-u570689065}"
DOMAIN="${SGPS_DOWNLOAD_DOMAIN:-engsaber.space}"
FOLDER="${SGPS_DOWNLOAD_FOLDER:-sgps-downloads}"
API="https://developers.hostinger.com/api/hosting/v1"
: "${HOSTINGER_API_TOKEN:?set HOSTINGER_API_TOKEN}"

WIN="$(ls "$DIR"/HORIX-*-windows-x64-portable.zip | head -1)"
MAC="$(ls "$DIR"/HORIX-*-macos-universal.zip | head -1)"
VERSION="$(basename "$WIN" | sed -n 's/^HORIX-\(.*\)-windows-x64-portable\.zip$/\1/p')"
size() { stat -c%s "$1" 2>/dev/null || stat -f%z "$1"; }

CREDS="$(curl -fsS -X POST -H "Authorization: Bearer $HOSTINGER_API_TOKEN" -H "Content-Type: application/json" \
  -H "Accept: application/json" "$API/files/upload-urls" -d "{\"username\":\"$USERNAME\",\"domain\":\"$DOMAIN\"}")"
field() { python3 -c 'import json,sys; print(json.loads(sys.argv[1])[sys.argv[2]])' "$CREDS" "$1"; }
URL="$(field url)"; AUTH="$(field auth_key)"; REST="$(field rest_auth_key)"

# upload <local file> <name in the folder>: TUS create, then the bytes in one PATCH.
upload() {
  local n; n="$(size "$1")"
  curl -fsS -o /dev/null -X POST "${URL%/}/$FOLDER/$2?override=true" \
    -H "X-Auth: $AUTH" -H "X-Auth-Rest: $REST" -H "Tus-Resumable: 1.0.0" \
    -H "Upload-Length: $n" -H "Upload-Offset: 0"
  local off; off="$(curl -fsS -D - -o /dev/null -X PATCH "${URL%/}/$FOLDER/$2?override=true" \
    -H "X-Auth: $AUTH" -H "X-Auth-Rest: $REST" -H "Tus-Resumable: 1.0.0" \
    -H "Content-Type: application/offset+octet-stream" -H "Upload-Offset: 0" \
    --data-binary "@$1" | tr -d '\r' | awk 'tolower($1)=="upload-offset:" {print $2}')"
  [ "$off" = "$n" ] || { echo "error: $2 upload incomplete ($off of $n bytes)" >&2; exit 1; }
  echo "uploaded $2 ($n bytes)"
}

upload "$HERE/../hosting/downloads/.htaccess" .htaccess
upload "$WIN" HORIX-windows-x64.zip
upload "$MAC" HORIX-macos-universal.zip
JSON="$(mktemp)"
python3 - "$JSON" "$VERSION" "$BUILD" "$(size "$WIN")" "$(size "$MAC")" <<'PY'
import json, sys, datetime
out, version, build, win, mac = sys.argv[1:6]
json.dump({
    "version": version, "build": build, "date": datetime.date.today().isoformat(),
    "windows": {"file": "HORIX-windows-x64.zip", "size": int(win)},
    "macos": {"file": "HORIX-macos-universal.zip", "size": int(mac)},
}, open(out, "w"))
PY
upload "$JSON" latest.json

# Check what visitors get (browser user agent: Hostinger's bot protection answers curl with 403).
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
for f in HORIX-windows-x64.zip:"$WIN" HORIX-macos-universal.zip:"$MAC"; do
  name="${f%%:*}"; want="$(size "${f#*:}")"
  got="$(curl -fsSI -A "$UA" "https://$DOMAIN/$FOLDER/$name?v=$BUILD" | tr -d '\r' | awk 'tolower($1)=="content-length:" {print $2}' | tail -1)"
  [ "$got" = "$want" ] || { echo "error: https://$DOMAIN/$FOLDER/$name serves $got bytes, expected $want" >&2; exit 1; }
  echo "live: https://$DOMAIN/$FOLDER/$name ($got bytes)"
done
curl -fsS -A "$UA" "https://$DOMAIN/$FOLDER/latest.json?v=$RANDOM"; echo
