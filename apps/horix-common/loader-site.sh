#!/usr/bin/env bash
# The HORIX web loading screen's needs in a built site (horix_rebrand.horix_loader): Inter and Cairo
# for its lettering in <site>/fonts/, and the WebAssembly file's size written over __HORIX_WASM_SIZE__
# in <site>/index.html, so its progress is the real share of the download.
# Usage: apps/horix-common/loader-site.sh <site dir>
set -euo pipefail
SITE="${1:?usage: loader-site.sh <site dir>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FONTS="$HERE/../sg-ps/assets/fonts"
mkdir -p "$SITE/fonts"
cp "$FONTS/inter-latin-500-normal.woff2" "$FONTS/cairo-arabic-700-normal.woff2" "$SITE/fonts/"
[ -f "$SITE/fonts/OFL-Cairo.txt" ] || cp "$FONTS/OFL-Cairo.txt" "$SITE/fonts/"
WASM="$(find "$SITE" -maxdepth 3 -name '*_bg.wasm' | head -1)"
[ -n "$WASM" ] || { echo "error: no *_bg.wasm in $SITE" >&2; exit 1; }
SIZE="$(stat -c%s "$WASM" 2>/dev/null || stat -f%z "$WASM")"
sed -i.bak "s/__HORIX_WASM_SIZE__/$SIZE/" "$SITE/index.html" && rm -f "$SITE/index.html.bak"
if grep -q __HORIX_WASM_SIZE__ "$SITE/index.html"; then echo "error: wasm size not written into $SITE/index.html" >&2; exit 1; fi
echo "loader: $(basename "$WASM") is $SIZE bytes"
