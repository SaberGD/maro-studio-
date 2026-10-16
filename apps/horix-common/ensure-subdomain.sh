#!/usr/bin/env bash
# Make sure a subdomain of a Hostinger website exists (creating it if needed), ask for its SSL
# certificate, and print where its files go, for deploy-static.sh.
#
# Usage: HOSTINGER_API_TOKEN=... apps/horix-common/ensure-subdomain.sh <subdomain.parent.tld> <parent.tld>
# Env:   HOSTINGER_API_TOKEN (required), HOSTINGER_USERNAME (default u570689065)
# Prints: UPLOAD_DOMAIN=<website> and UPLOAD_DIR=<folder in its public_html> (append to $GITHUB_ENV).
#
# A new subdomain gets the folder <prefix> inside the parent's public_html, so its files upload
# through the parent website, which the API always knows.
set -euo pipefail

FULL="$1"; PARENT="$2"
PREFIX="${FULL%."$PARENT"}"
[ "$PREFIX" != "$FULL" ] && [ -n "$PREFIX" ] || { echo "error: $FULL is not a subdomain of $PARENT" >&2; exit 1; }
API="https://developers.hostinger.com/api/hosting/v1"
USERNAME="${HOSTINGER_USERNAME:-u570689065}"
: "${HOSTINGER_API_TOKEN:?set HOSTINGER_API_TOKEN (hPanel > Account > API)}"
BASE="$API/accounts/$USERNAME/websites/$PARENT"

call() {  # call <method> <url> [json]
  curl -sS -X "$1" -H "Authorization: Bearer $HOSTINGER_API_TOKEN" -H "Accept: application/json" \
    -H "Content-Type: application/json" "$2" ${3:+-d "$3"} -w '\n%{http_code}'
}

root_of() {  # the subdomain's root directory, empty if it doesn't exist
  local out code
  out="$(call GET "$BASE/subdomains")"; code="${out##*$'\n'}"; out="${out%$'\n'*}"
  [ "$code" = 200 ] || { echo "error: listing the subdomains of $PARENT failed ($code): $out" >&2; exit 1; }
  python3 -c 'import json,sys; print(next((s.get("root_directory","") for s in json.loads(sys.argv[1]) if s.get("domain")==sys.argv[2]), ""))' "$out" "$FULL"
}

ROOT="$(root_of)"
if [ -z "$ROOT" ]; then
  echo "creating $FULL (folder $PREFIX in $PARENT)" >&2
  out="$(call POST "$BASE/subdomains" "{\"subdomain\":\"$PREFIX\",\"directory\":\"$PREFIX\"}")"; code="${out##*$'\n'}"
  [ "$code" = 200 ] || { echo "error: creating $FULL failed ($code): ${out%$'\n'*}" >&2; exit 1; }
  for _ in $(seq 1 30); do ROOT="$(root_of)"; [ -n "$ROOT" ] && break; sleep 5; done
  [ -n "$ROOT" ] || { echo "error: $FULL was accepted but did not appear after 150 s" >&2; exit 1; }
  # A lifetime certificate, issued in the background. Not fatal: Hostinger may already cover it.
  out="$(call POST "$API/accounts/$USERNAME/websites/$FULL/ssl/setup")"
  echo "ssl setup for $FULL: HTTP ${out##*$'\n'}" >&2
fi
echo "$FULL serves $ROOT" >&2

# /home/<user>/domains/<website>/public_html[/<dir>]
rest="${ROOT#*/domains/}"
website="${rest%%/*}"
dir="${rest#"$website"/public_html}"; dir="${dir#/}"
case "$rest" in */public_html|*/public_html/*) ;; *) echo "error: unexpected root directory $ROOT" >&2; exit 1 ;; esac
echo "UPLOAD_DOMAIN=$website"
echo "UPLOAD_DIR=$dir"
