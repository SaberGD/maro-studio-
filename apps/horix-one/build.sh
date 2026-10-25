#!/usr/bin/env bash
# Build HORIX One for the web: one site with the persona bar (web/index.html) and its two
# personas, Vector (Horix Vectors, under vector/) and Pixel (HORIX, under pixel/). All three are
# on one origin, so the bar hands documents from one persona to the other.
#
# Usage: apps/horix-one/build.sh
# Env:   HORIX_ONE_PIXEL / HORIX_ONE_VECTOR: sites already built (HORIX with
#        HORIX_PUBLIC_URL=/pixel/, Horix Vectors as is) to use instead of building them here.
# Needs: what apps/sg-ps/build.sh and apps/horix-vectors/build.sh need.
# Output: deploy/horix-one/horix-one-<version>-web.zip, with the site in horix-one/.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
WORK="${HORIX_ONE_WORK:-$REPO/.horix-build/one}"
OUT="$REPO/deploy/horix-one"
VERSION="$(tr -d '[:space:]' < "$HERE/VERSION")${HORIX_BUILD_NUMBER:+.$HORIX_BUILD_NUMBER}"
mkdir -p "$WORK" "$OUT"

PIXEL="${HORIX_ONE_PIXEL:-}"
if [ -z "$PIXEL" ]; then
  SGPS_WORK="$WORK/pixel" HORIX_PUBLIC_URL=/pixel/ "$REPO/apps/sg-ps/build.sh"
  PIXEL="$WORK/pixel/site/horix"
fi
VECTOR="${HORIX_ONE_VECTOR:-}"
if [ -z "$VECTOR" ]; then
  HORIX_VECTORS_WORK="$WORK/vector" "$REPO/apps/horix-vectors/build.sh"
  VECTOR="$WORK/vector/site/horix-vectors"
fi
# The Pixel site must be built for /pixel/ (its page loads its files from there).
grep -q '/pixel/' "$PIXEL/index.html" || { echo "error: $PIXEL is not built for /pixel/ (HORIX_PUBLIC_URL)" >&2; exit 1; }
[ -f "$VECTOR/index.html" ] || { echo "error: no Horix Vectors site in $VECTOR" >&2; exit 1; }

SITE="$WORK/site/horix-one"
rm -rf "$WORK/site"
mkdir -p "$SITE/fonts"
BUILD_ID="${HORIX_BUILD_ID:-$(date -u +%Y%m%d%H%M%S)}"
python3 -c 'import sys; p, o, b = sys.argv[1:4]; t = open(p, encoding="utf-8").read(); open(o, "w", encoding="utf-8").write(t.replace("<head>", "<head>\n  <meta name=\"horix-build\" content=\"" + b + "\">", 1))' \
  "$HERE/web/index.html" "$SITE/index.html" "$BUILD_ID"
cp "$REPO/apps/sg-ps/assets/horix-symbol.svg" "$SITE/horix-symbol.svg"
cp "$HERE/assets/app-icon/favicon.svg" "$SITE/horix-one-icon.svg"
for f in barlow-condensed-latin-800-normal inter-latin-500-normal inter-latin-600-normal cairo-arabic-700-normal; do
  cp "$REPO/apps/sg-ps/assets/fonts/$f.woff2" "$SITE/fonts/"
done
cp "$REPO/apps/sg-ps/assets/fonts/OFL-BarlowCondensed.txt" "$REPO/apps/sg-ps/assets/fonts/OFL-Cairo.txt" "$SITE/fonts/"
cp "$HERE/web/.htaccess" "$SITE/.htaccess"
cp -R "$PIXEL" "$SITE/pixel"
cp -R "$VECTOR" "$SITE/vector"
ZIP="$OUT/horix-one-$VERSION-web.zip"
rm -f "$ZIP"
(cd "$WORK/site" && zip -qr9 "$ZIP" horix-one)
echo "wrote $ZIP"
ls -l "$ZIP"
