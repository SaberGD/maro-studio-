#!/usr/bin/env bash
# Build HORIX (rebranded PhotoCraft Web) and package it for Hostinger.
#
# Usage: apps/sg-ps/build.sh [photocraft-source.tar.gz]
#   default source: archive/photocraft/photocraft-source-0.3.0.tar.gz
# Needs: Rust >= 1.95, `rustup target add wasm32-unknown-unknown`, `cargo install trunk --locked`, zip.
# Output: deploy/sg-ps/sg-ps-<version>-hostinger.zip, with three folders:
#   horix/      the editor, served at https://sabergroupacademy.com/horix/
#   downloads/  the desktop download page, https://sabergroupacademy.com/downloads/
#   redirect/   the old studio.engsaber.space site: permanent redirects to the two above
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SRC_TGZ="${1:-$REPO/archive/photocraft/photocraft-source-0.3.0.tar.gz}"
WORK="${SGPS_WORK:-$REPO/.sgps-build}"
OUT="$REPO/deploy/sg-ps"

rm -rf "$WORK/src" "$WORK/site"
mkdir -p "$WORK/src" "$WORK/site" "$OUT"
tar -xzf "$SRC_TGZ" -C "$WORK/src" --strip-components=1
VERSION="$(sed -n 's/^version = "\(.*\)"/\1/p' "$WORK/src/Cargo.toml" | head -1)"

python3 -I "$HERE/rebrand.py" "$WORK/src"

# The editor lives in a folder of the academy site. File names carry no hash: the deploy can only
# add and overwrite files there (never delete), so each deploy replaces the same few files, and
# .htaccess makes browsers revalidate them.
(cd "$WORK/src/apps/photocraft-web" && CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$WORK/target}" \
  trunk build --release --public-url /horix/ --filehash false)

APP="$WORK/site/horix"
mkdir -p "$APP"
cp -R "$WORK/src/dist/web/." "$APP/"
# Build id: the deploy waits until the live page carries it.
BUILD_ID="${HORIX_BUILD_ID:-$(date -u +%Y%m%d%H%M%S)}"
sed -i.bak "s|<head>|<head>\n  <meta name=\"horix-build\" content=\"$BUILD_ID\">|" "$APP/index.html" && rm -f "$APP/index.html.bak"
# The loading screen shows real progress against the WebAssembly file's size.
WASM="$APP/sg-ps_bg.wasm"
WASM_SIZE="$(stat -c%s "$WASM" 2>/dev/null || stat -f%z "$WASM")"
sed -i.bak "s/__HORIX_WASM_SIZE__/$WASM_SIZE/" "$APP/index.html" && rm -f "$APP/index.html.bak"
if grep -q __HORIX_WASM_SIZE__ "$APP/index.html"; then echo "error: wasm size not written into index.html" >&2; exit 1; fi
# Pre-compressed copies: the host does not compress .wasm on the fly (25 MB -> ~8 MB with Brotli,
# ~11 MB with gzip); .htaccess serves the best one the browser accepts.
gzip -9 -k -f "$WASM"
if command -v brotli >/dev/null 2>&1; then
  brotli -q 11 -f -k -o "$WASM.br" "$WASM"
elif python3 -c "import brotli" 2>/dev/null; then
  python3 -c 'import brotli,sys; open(sys.argv[1] + ".br", "wb").write(brotli.compress(open(sys.argv[1], "rb").read(), quality=11))' "$WASM"
else
  echo "warning: no brotli encoder; serving gzip only" >&2
fi
ls -l "$WASM"*
cp "$HERE/hosting/.htaccess" "$APP/.htaccess"
# Fallback for deploy.sh: the same rules without the pre-compressed WebAssembly.
sed '/^# >>> compressed-wasm/,/^# <<< compressed-wasm/d' "$HERE/hosting/.htaccess" > "$WORK/site/htaccess-plain"
grep -q "compressed-wasm" "$WORK/site/htaccess-plain" && { echo "error: htaccess-plain still has the compressed block" >&2; exit 1; }
cp "$HERE/hosting/waitlist.php" "$APP/waitlist.php"
# HORIX AI selection: MobileSAM (first Quick / Object Selection) and U²-Netp (first Select Subject).
python3 -I "$HERE/ai/fetch.py" "$APP/models" web
# Desktop download page; the zips themselves live on engsaber.space/sgps-downloads/.
DL="$WORK/site/downloads"
cp -R "$HERE/hosting/download" "$DL"
cp "$HERE/assets/horix-lockup.svg" "$DL/horix-logo.svg"
cp "$HERE/assets/horix-favicon.svg" "$DL/horix-favicon.svg"
mkdir -p "$DL/fonts"
cp "$HERE"/assets/fonts/*.woff2 "$DL/fonts/"
# The old address: everything moves permanently to the academy site.
cp -R "$HERE/hosting/redirect" "$WORK/site/redirect"
# n8n webhook for new leads (GitHub secret SGPS_LEAD_WEBHOOK); server-side only, never in the page.
if [ -n "${SGPS_LEAD_WEBHOOK:-}" ]; then
  python3 -c 'import sys; u = sys.argv[1].replace("\\", "\\\\").replace("\x27", "\\\x27"); open(sys.argv[2], "w").write("<?php return [\x27lead_webhook\x27 => \x27" + u + "\x27];\n")' \
    "$SGPS_LEAD_WEBHOOK" "$APP/sgps-config.php"
fi
# Licence obligations: the MIT licence text (with its copyright line) and the licences of the
# fonts and icons compiled into the app. They are plain files on the server, not shown in the UI.
cp "$WORK/src/LICENSE-MIT" "$APP/LICENSE.txt"
{
  echo "HORIX includes the following third-party material."
  for f in assets/fonts/OFL-Inter.txt assets/fonts/OFL-JetBrainsMono.txt assets/icons/LICENSE-lucide.txt assets/dict/LICENSE-SCOWL.txt; do
    printf '\n==== %s ====\n\n' "$(basename "$f")"
    cat "$WORK/src/$f"
  done
  printf '\n==== OFL-BarlowCondensed.txt ====\n\n'
  cat "$HERE/assets/fonts/OFL-BarlowCondensed.txt"
  printf '\n==== OFL-Cairo.txt (download page) ====\n\n'
  cat "$HERE/assets/fonts/OFL-Cairo.txt"
  printf '\n==== MobileSAM (models/) ====\n\n'
  printf 'MobileSAM, Copyright the MobileSAM authors (github.com/ChaoningZhang/MobileSAM). ONNX export by\nhuggingface.co/Acly/MobileSAM (MIT). Mask decoder from Segment Anything, Copyright Meta Platforms, Inc.\nRuns in the browser with Microsoft onnxruntime-web (MIT), loaded from cdn.jsdelivr.net.\n\n'
  cat "$HERE/ai/LICENSE-MobileSAM.txt"
  printf '\n==== U2-Netp (models/u2netp.onnx) ====\n\n'
  printf 'U^2-Net, Copyright Xuebin Qin et al. (github.com/xuebinqin/U-2-Net). ONNX export by rembg\n(github.com/danielgatis/rembg, MIT).\n\n'
  cat "$HERE/ai/LICENSE-U2Net.txt"
} > "$APP/THIRD-PARTY-NOTICES.txt"

# Nothing from the old name may be left in file names.
if ls "$APP" | grep -qi photocraft; then
  echo "error: output still has photocraft file names:" >&2; ls "$APP" >&2; exit 1
fi

ZIP="$OUT/sg-ps-$VERSION-hostinger.zip"
rm -f "$ZIP"
(cd "$WORK/site" && zip -qr9 "$ZIP" .)
echo "wrote $ZIP"
ls -l "$ZIP"
