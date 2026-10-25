#!/usr/bin/env bash
# Build Horix Layout (rebranded DesignCraft) for the web and zip it for hosting.
#
# Usage: apps/horix-layout/build.sh [designcraft-source.tar.gz]
#   default source: archive/designcraft/designcraft-source-0.12.0.tar.gz
# Needs: Rust >= 1.95 with the wasm32-unknown-unknown target, trunk, python3, zip, git (craft-fonts).
# Output: deploy/horix-layout/horix-layout-<version>-web.zip (a static site; any URL path works).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SRC_TGZ="${1:-$REPO/archive/designcraft/designcraft-source-0.12.0.tar.gz}"
WORK="${HORIX_LAYOUT_WORK:-$REPO/.horix-build/layout}"
OUT="$REPO/deploy/horix-layout"

rm -rf "$WORK/src" "$WORK/site"
mkdir -p "$WORK/src" "$WORK/site" "$OUT"
tar -xzf "$SRC_TGZ" -C "$WORK/src" --strip-components=1
VERSION="$(tr -d '[:space:]' < "$HERE/VERSION")"

python3 -I "$HERE/rebrand.py" "$WORK/src"
# craft-fonts at the commit Horix Vectors' upstream pins (DesignCraft 0.12's has no Arabic face):
# the web build embeds its Arabic faces (rebrand.py), so Arabic text shows in the browser, which
# has no system fonts to fall back to.
CRAFT_FONTS_DIR="${CRAFT_FONTS_DIR:-$(CRAFT_FONTS_REF="${CRAFT_FONTS_REF:-a71c20e30af613287c504f7e685ca8fad77752bc}" "$HERE/../horix-common/craft-fonts.sh" "$WORK/src" "$WORK")}"
export CRAFT_FONTS_DIR

(cd "$WORK/src/apps/designcraft-web" && CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$WORK/target}" trunk build --release)

SITE="$WORK/site/horix-layout"
mkdir -p "$SITE"
cp -R "$WORK/src/dist/web/." "$SITE/"
BUILD_ID="${HORIX_BUILD_ID:-$(date -u +%Y%m%d%H%M%S)}"
python3 -c 'import sys; p, b = sys.argv[1:3]; t = open(p, encoding="utf-8").read(); open(p, "w", encoding="utf-8").write(t.replace("<head>", "<head>\n  <meta name=\"horix-build\" content=\"" + b + "\">", 1))' "$SITE/index.html" "$BUILD_ID"
# HORIX's loading screen: its fonts, and the WebAssembly size for its progress.
"$HERE/../horix-common/loader-site.sh" "$SITE"
[ -f "$SITE/index.html.gz" ] && gzip -9 -k -f "$SITE/index.html"
if [ -f "$SITE/index.html.br" ]; then
  if command -v brotli >/dev/null 2>&1; then brotli -q 11 -f -k "$SITE/index.html"; else rm -f "$SITE/index.html.br"; fi
fi
cp "$WORK/src/packaging/web/.htaccess" "$WORK/src/packaging/web/_headers" "$SITE/"
# Pre-compressed WebAssembly (the host does not compress it on the fly), served by .htaccess to
# browsers that accept it; deploy-static.sh checks each encoding and drops the block if needed.
for w in "$SITE"/*.wasm; do
  [ -f "$w.gz" ] || gzip -9 -k -f "$w"
  if [ ! -f "$w.br" ] && command -v brotli >/dev/null 2>&1; then brotli -q 11 -f -k "$w"; fi
done
{ echo; cat "$HERE/../horix-common/htaccess-compressed-wasm"; } >> "$SITE/.htaccess"
# Licence obligations: the licence texts and the third-party notices, as plain files.
cp "$WORK/src/LICENSE-MIT" "$WORK/src/LICENSE-APACHE" "$WORK/src/NOTICE" "$SITE/"
cp "$WORK/src/assets/fonts/"OFL-*.txt "$SITE/"
for ofl in "$CRAFT_FONTS_DIR"/fonts/*/OFL.txt; do
  [ -f "$ofl" ] && cp "$ofl" "$SITE/OFL-$(basename "$(dirname "$ofl")").txt"
done
cp "$HERE/assets/app-icon/favicon.svg" "$SITE/horix-layout-icon.svg"

ZIP="$OUT/horix-layout-$VERSION-web.zip"
rm -f "$ZIP"
(cd "$WORK/site" && zip -qr9 "$ZIP" horix-layout)
echo "wrote $ZIP"
ls -l "$ZIP"
