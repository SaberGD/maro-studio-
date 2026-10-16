#!/usr/bin/env bash
# Build HORIX Launcher (rebranded craft-launcher) for the web and zip it for hosting.
#
# Usage: apps/horix-launcher/build.sh [craft-launcher-source.tar.gz]
#   default source: archive/craft-launcher/craft-launcher-source-0.4.1.tar.gz
# Needs: Rust >= 1.95 with the wasm32-unknown-unknown target, trunk, python3, zip.
# Output: deploy/horix-launcher/horix-launcher-<version>-web.zip (folder horix-launcher/): the
# browser launcher, which lists the HORIX apps with the right download for the visitor's system.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SRC_TGZ="${1:-$REPO/archive/craft-launcher/craft-launcher-source-0.4.1.tar.gz}"
WORK="${HORIX_LAUNCHER_WORK:-$REPO/.horix-build/launcher}"
OUT="$REPO/deploy/horix-launcher"

rm -rf "$WORK/src" "$WORK/site"
mkdir -p "$WORK/src" "$WORK/site" "$OUT"
tar -xzf "$SRC_TGZ" -C "$WORK/src" --strip-components=1
VERSION="$(awk '/^\[/{p=($0=="[workspace.package]");next} p&&$1=="version"{gsub(/[" ]/,"",$3);print $3;exit}' "$WORK/src/Cargo.toml")"

python3 -I "$HERE/rebrand.py" "$WORK/src"

(cd "$WORK/src/apps/artcraft-launcher-web" && CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$WORK/target}" trunk build --release --cargo-profile wasm-release)

SITE="$WORK/site/horix-launcher"
mkdir -p "$SITE"
cp -R "$WORK/src/dist/web/." "$SITE/"
BUILD_ID="${HORIX_BUILD_ID:-$(date -u +%Y%m%d%H%M%S)}"
python3 -c 'import sys; p, b = sys.argv[1:3]; t = open(p, encoding="utf-8").read(); open(p, "w", encoding="utf-8").write(t.replace("<head>", "<head>\n  <meta name=\"horix-build\" content=\"" + b + "\">", 1))' "$SITE/index.html" "$BUILD_ID"
for w in "$SITE"/*.wasm; do
  gzip -9 -k -f "$w"
  if command -v brotli >/dev/null 2>&1; then brotli -q 11 -f -k "$w"; fi
done
# The feed (release_info.json, published beside the page by horix-feed.yml) and the page itself
# must never come from a stale cache.
{ printf 'AddType application/wasm .wasm\nAddType text/javascript .js\n\n<IfModule mod_headers.c>\n  <FilesMatch "\\.(json|html)$">\n    Header set Cache-Control "no-cache"\n  </FilesMatch>\n</IfModule>\n\n'
  cat "$HERE/../horix-common/htaccess-compressed-wasm"; } > "$SITE/.htaccess"
cp "$WORK/src/LICENSE-MIT" "$WORK/src/LICENSE-APACHE" "$WORK/src/NOTICE" "$SITE/"

ZIP="$OUT/horix-launcher-$VERSION-web.zip"
rm -f "$ZIP"
(cd "$WORK/site" && zip -qr9 "$ZIP" horix-launcher)
echo "wrote $ZIP"
ls -l "$ZIP"
