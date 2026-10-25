#!/usr/bin/env bash
# Build Horix Vectors (rebranded VectorCraft) for the web and zip it for hosting.
#
# Usage: apps/horix-vectors/build.sh [vectorcraft-source.tar.gz]
#   default source: archive/vectorcraft/vectorcraft-source-0.16.0.tar.gz
# Needs: Rust >= 1.95 with the wasm32-unknown-unknown target, trunk, python3, zip, git (craft-fonts).
# Output: deploy/horix-vectors/horix-vectors-<version>-web.zip (a static site; any URL path works).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SRC_TGZ="${1:-$REPO/archive/vectorcraft/vectorcraft-source-0.16.0.tar.gz}"
WORK="${HORIX_VECTORS_WORK:-$REPO/.horix-build/vectors}"
OUT="$REPO/deploy/horix-vectors"

rm -rf "$WORK/src" "$WORK/site"
mkdir -p "$WORK/src" "$WORK/site" "$OUT"
tar -xzf "$SRC_TGZ" -C "$WORK/src" --strip-components=1
VERSION="$(awk '/^\[/{p=($0=="[workspace.package]");next} p&&$1=="version"{gsub(/[" ]/,"",$3);print $3;exit}' "$WORK/src/Cargo.toml")"

python3 -I "$HERE/rebrand.py" "$WORK/src"
# Fonts the browser has no system copy of (Noto Sans Arabic first), served beside the wasm, as
# upstream's releases do; trunk's post-build hook copies them into fonts/.
CRAFT_FONTS_DIR="${CRAFT_FONTS_DIR:-$("$HERE/../horix-common/craft-fonts.sh" "$WORK/src" "$WORK")}"
# Without the Japanese and Chinese faces: a web build embeds BIZ UDPGothic (the Japanese UI font,
# ~4.7 MB) in the wasm whenever the manifest lists it. The Arabic, Thai and Georgian faces stay.
WEB_FONTS="$WORK/craft-fonts-web"
rm -rf "$WEB_FONTS" && mkdir -p "$WEB_FONTS/fonts"
grep -vE '\| *[^|]*(Jpan|Hans|Hant|Kore)[^|]* *\| *OFL' "$CRAFT_FONTS_DIR/fonts/manifest.txt" > "$WEB_FONTS/fonts/manifest.txt"
for d in $(sed -n 's/^[^#][^|]*|[^|]*| *fonts\/\([^/]*\)\/.*/\1/p' "$WEB_FONTS/fonts/manifest.txt" | sort -u); do
  cp -R "$CRAFT_FONTS_DIR/fonts/$d" "$WEB_FONTS/fonts/$d"
done
export CRAFT_FONTS_DIR="$WEB_FONTS"

(cd "$WORK/src/apps/vectorcraft-web" && CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$WORK/target}" trunk build --release)

SITE="$WORK/site/horix-vectors"
mkdir -p "$SITE"
cp -R "$WORK/src/dist/web/." "$SITE/"
BUILD_ID="${HORIX_BUILD_ID:-$(date -u +%Y%m%d%H%M%S)}"
python3 -c 'import sys; p, b = sys.argv[1:3]; t = open(p, encoding="utf-8").read(); open(p, "w", encoding="utf-8").write(t.replace("<head>", "<head>\n  <meta name=\"horix-build\" content=\"" + b + "\">", 1))' "$SITE/index.html" "$BUILD_ID"
# HORIX's loading screen: its fonts, and the WebAssembly size for its progress.
"$HERE/../horix-common/loader-site.sh" "$SITE"
# Upstream's pre-compressed copies of the page would still hold the old page: redo them.
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
# The craft-fonts faces are OFL: their licences go with them, as OFL-<family dir>.txt.
for ofl in "$CRAFT_FONTS_DIR"/fonts/*/OFL.txt; do
  [ -f "$ofl" ] && cp "$ofl" "$SITE/OFL-$(basename "$(dirname "$ofl")").txt"
done
cp "$HERE/assets/app-icon/favicon.svg" "$SITE/horix-vectors-icon.svg"

ZIP="$OUT/horix-vectors-$VERSION-web.zip"
rm -f "$ZIP"
(cd "$WORK/site" && zip -qr9 "$ZIP" horix-vectors)
echo "wrote $ZIP"
ls -l "$ZIP"
