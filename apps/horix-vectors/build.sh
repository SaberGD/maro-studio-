#!/usr/bin/env bash
# Build Horix Vectors (rebranded VectorCraft) for the web and zip it for hosting.
#
# Usage: apps/horix-vectors/build.sh [vectorcraft-source.tar.gz]
#   default source: archive/vectorcraft/vectorcraft-source-0.11.0.tar.gz
# Needs: Rust >= 1.95 with the wasm32-unknown-unknown target, trunk, python3 with Pillow, zip.
# Output: deploy/horix-vectors/horix-vectors-<version>-web.zip (a static site; any URL path works).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SRC_TGZ="${1:-$REPO/archive/vectorcraft/vectorcraft-source-0.11.0.tar.gz}"
WORK="${HORIX_VECTORS_WORK:-$REPO/.horix-build/vectors}"
OUT="$REPO/deploy/horix-vectors"

rm -rf "$WORK/src" "$WORK/site"
mkdir -p "$WORK/src" "$WORK/site" "$OUT"
tar -xzf "$SRC_TGZ" -C "$WORK/src" --strip-components=1
VERSION="$(awk '/^\[/{p=($0=="[workspace.package]");next} p&&$1=="version"{gsub(/[" ]/,"",$3);print $3;exit}' "$WORK/src/Cargo.toml")"

python3 -I "$HERE/rebrand.py" "$WORK/src"

(cd "$WORK/src/apps/vectorcraft-web" && CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$WORK/target}" trunk build --release)

SITE="$WORK/site/horix-vectors"
mkdir -p "$SITE"
cp -R "$WORK/src/dist/web/." "$SITE/"
BUILD_ID="${HORIX_BUILD_ID:-$(date -u +%Y%m%d%H%M%S)}"
python3 -c 'import sys; p, b = sys.argv[1:3]; t = open(p, encoding="utf-8").read(); open(p, "w", encoding="utf-8").write(t.replace("<head>", "<head>\n  <meta name=\"horix-build\" content=\"" + b + "\">", 1))' "$SITE/index.html" "$BUILD_ID"
cp "$WORK/src/packaging/web/.htaccess" "$WORK/src/packaging/web/_headers" "$SITE/"
# Licence obligations: the licence texts and the third-party notices, as plain files.
cp "$WORK/src/LICENSE-MIT" "$WORK/src/LICENSE-APACHE" "$WORK/src/NOTICE" "$SITE/"
cp "$HERE/assets/app-icon/favicon.svg" "$SITE/horix-vectors-icon.svg"

ZIP="$OUT/horix-vectors-$VERSION-web.zip"
rm -f "$ZIP"
(cd "$WORK/site" && zip -qr9 "$ZIP" horix-vectors)
echo "wrote $ZIP"
ls -l "$ZIP"
