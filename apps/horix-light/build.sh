#!/usr/bin/env bash
# Build Horix Light (rebranded LightCraft) for the web and zip it for hosting.
#
# Usage: apps/horix-light/build.sh [lightcraft-source.tar.gz]
#   default source: archive/lightcraft/lightcraft-source-0.13.0.tar.gz
# Needs: Rust >= 1.95 with the wasm32-unknown-unknown target, wasm-bindgen-cli (version in Cargo.lock), python3
# (with the onnx and onnxruntime packages, for the AI models), git, zip.
# Output: deploy/horix-light/horix-light-<version>-web.zip (a static site; any URL path works).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SRC_TGZ="${1:-$REPO/archive/lightcraft/lightcraft-source-0.13.0.tar.gz}"
WORK="${HORIX_LIGHT_WORK:-$REPO/.horix-build/light}"
OUT="$REPO/deploy/horix-light"

rm -rf "$WORK/src" "$WORK/site"
mkdir -p "$WORK/src" "$WORK/site" "$OUT"
tar -xzf "$SRC_TGZ" -C "$WORK/src" --strip-components=1
VERSION="$(awk '/^\[/{p=($0=="[workspace.package]");next} p&&$1=="version"{gsub(/[" ]/,"",$3);print $3;exit}' "$WORK/src/Cargo.toml")"

python3 -I "$HERE/rebrand.py" "$WORK/src"

export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$WORK/target}"
(cd "$WORK/src" && cargo xtask web)

SITE="$WORK/site/horix-light"
mkdir -p "$SITE"
cp -R "$CARGO_TARGET_DIR/web-site/." "$SITE/"
BUILD_ID="${HORIX_BUILD_ID:-$(date -u +%Y%m%d%H%M%S)}"
python3 -c 'import sys; p, b = sys.argv[1:3]; t = open(p, encoding="utf-8").read(); open(p, "w", encoding="utf-8").write(t.replace("<head>", "<head>\n  <meta name=\"horix-build\" content=\"" + b + "\">", 1))' "$SITE/index.html" "$BUILD_ID"
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
cp "$HERE/assets/app-icon/favicon.svg" "$SITE/horix-light-icon.svg"
# HORIX AI masks (patches/50-horix-ai.diff): MobileSAM (Object) and IS-Net fp16 (Subject,
# Background), the same files HORIX's web build serves. -E, not -I: converting IS-Net needs onnx
# from the user site-packages (CI installs it with pip --user).
python3 -E "$HERE/../sg-ps/ai/fetch.py" "$SITE/models" web
cp "$HERE/../sg-ps/ai/LICENSE-MobileSAM.txt" "$HERE/../sg-ps/ai/LICENSE-SegmentAnything.txt" "$HERE/../sg-ps/ai/LICENSE-ISNet.txt" "$SITE/models/"
printf '\n# HORIX AI models\nAddType application/octet-stream .onnx\n' >> "$SITE/.htaccess"

ZIP="$OUT/horix-light-$VERSION-web.zip"
rm -f "$ZIP"
(cd "$WORK/site" && zip -qr9 "$ZIP" horix-light)
echo "wrote $ZIP"
ls -l "$ZIP"
