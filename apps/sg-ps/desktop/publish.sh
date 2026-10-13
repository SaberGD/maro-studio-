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

# Any platform may be missing (e.g. Windows when GitHub's hosted minutes ran out): its previous
# files and latest.json entry stay as they are.
pick() { ls "$DIR"/$1 2>/dev/null | head -1 || true; }
WIN="$(pick 'HORIX-*-windows-x64-portable.zip')"
MAC="$(pick 'HORIX-*-macos-universal.zip')"
WINF="$(pick 'HORIX-*-windows-x64-full.zip')"
MACF="$(pick 'HORIX-*-macos-universal-full.zip')"
[ -n "$WIN$MAC" ] || { echo "error: no desktop zip in $DIR" >&2; exit 1; }
VERSION="$(basename "${WIN:-$MAC}" | sed -En 's/^HORIX-(.*)-(windows-x64-portable|macos-universal)\.zip$/\1/p')"
size() { stat -c%s "$1" 2>/dev/null || stat -f%z "$1"; }

CREDS="$(curl -fsS -X POST -H "Authorization: Bearer $HOSTINGER_API_TOKEN" -H "Content-Type: application/json" \
  -H "Accept: application/json" "$API/files/upload-urls" -d "{\"username\":\"$USERNAME\",\"domain\":\"$DOMAIN\"}")"
field() { python3 -c 'import json,sys; print(json.loads(sys.argv[1])[sys.argv[2]])' "$CREDS" "$1"; }
URL="$(field url)"; AUTH="$(field auth_key)"; REST="$(field rest_auth_key)"

# upload <local file> <name in the folder>: TUS create, then the bytes in 64 MB PATCH chunks (the
# full downloads are over 1 GB; one request that size may be refused).
upload() {
  local n; n="$(size "$1")"
  curl -fsS -o /dev/null -X POST "${URL%/}/$FOLDER/$2?override=true" \
    -H "X-Auth: $AUTH" -H "X-Auth-Rest: $REST" -H "Tus-Resumable: 1.0.0" \
    -H "Upload-Length: $n" -H "Upload-Offset: 0"
  local off=0 got part; part="$(mktemp)"
  while [ "$off" -lt "$n" ]; do
    dd if="$1" of="$part" bs=1048576 skip=$((off / 1048576)) count=64 status=none
    got="$(curl -fsS -D - -o /dev/null -X PATCH "${URL%/}/$FOLDER/$2?override=true" \
      -H "X-Auth: $AUTH" -H "X-Auth-Rest: $REST" -H "Tus-Resumable: 1.0.0" \
      -H "Content-Type: application/offset+octet-stream" -H "Upload-Offset: $off" \
      --data-binary "@$part" | tr -d '\r' | awk 'tolower($1)=="upload-offset:" {print $2}')"
    [ -n "$got" ] && [ "$got" -gt "$off" ] || { echo "error: $2 upload stalled at $off of $n bytes" >&2; rm -f "$part"; exit 1; }
    off="$got"
  done
  rm -f "$part"
  [ "$off" = "$n" ] || { echo "error: $2 upload incomplete ($off of $n bytes)" >&2; exit 1; }
  echo "uploaded $2 ($n bytes)"
}

upload "$HERE/../hosting/downloads/.htaccess" .htaccess
[ -n "$WIN" ] && upload "$WIN" HORIX-windows-x64.zip
[ -n "$MAC" ] && upload "$MAC" HORIX-macos-universal.zip
[ -n "$WINF" ] && upload "$WINF" HORIX-windows-x64-full.zip
[ -n "$MACF" ] && upload "$MACF" HORIX-macos-universal-full.zip
JSON="$(mktemp)"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
PREV="$(curl -fsS -A "$UA" "https://$DOMAIN/$FOLDER/latest.json?v=$RANDOM" 2>/dev/null || echo '{}')"
python3 - "$JSON" "$VERSION" "$BUILD" "$PREV" \
  "windows=HORIX-windows-x64.zip=$WIN" "macos=HORIX-macos-universal.zip=$MAC" \
  "windows-full=HORIX-windows-x64-full.zip=$WINF" "macos-full=HORIX-macos-universal-full.zip=$MACF" <<'PY'
import json, os, sys, datetime
out, version, build, prev = sys.argv[1:5]
try:
    data = json.loads(prev)
except ValueError:
    data = {}
data.update({"version": version, "build": build, "date": datetime.date.today().isoformat()})
for spec in sys.argv[5:]:
    key, name, path = spec.split("=", 2)
    if path:
        data[key] = {"file": name, "size": os.path.getsize(path)}
json.dump(data, open(out, "w"))
PY
upload "$JSON" latest.json

# Check what visitors get (browser user agent: Hostinger's bot protection answers curl with 403).
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
for f in HORIX-windows-x64.zip:"$WIN" HORIX-macos-universal.zip:"$MAC" HORIX-windows-x64-full.zip:"$WINF" HORIX-macos-universal-full.zip:"$MACF"; do
  [ -n "${f#*:}" ] || continue
  name="${f%%:*}"; want="$(size "${f#*:}")"
  got="$(curl -fsSI -A "$UA" "https://$DOMAIN/$FOLDER/$name?v=$BUILD" | tr -d '\r' | awk 'tolower($1)=="content-length:" {print $2}' | tail -1)"
  [ "$got" = "$want" ] || { echo "error: https://$DOMAIN/$FOLDER/$name serves $got bytes, expected $want" >&2; exit 1; }
  echo "live: https://$DOMAIN/$FOLDER/$name ($got bytes)"
done
curl -fsS -A "$UA" "https://$DOMAIN/$FOLDER/latest.json?v=$RANDOM"; echo
