#!/usr/bin/env bash
# Build HORIX (rebranded PhotoCraft Web) and package it for Hostinger.
#
# Usage: apps/sg-ps/build.sh [photocraft-source.tar.gz]
#   default source: archive/photocraft/photocraft-source-0.3.0.tar.gz
# Needs: Rust >= 1.95, `rustup target add wasm32-unknown-unknown`, `cargo install trunk --locked`, zip.
# Output: deploy/sg-ps/sg-ps-<version>-hostinger.zip
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

(cd "$WORK/src/apps/photocraft-web" && CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$WORK/target}" trunk build --release)

cp -R "$WORK/src/dist/web/." "$WORK/site/"
cp "$HERE/hosting/.htaccess" "$WORK/site/.htaccess"
cp "$HERE/hosting/waitlist.php" "$WORK/site/waitlist.php"
# Desktop download page (studio.engsaber.space/download/); the zips live on engsaber.space.
cp -R "$HERE/hosting/download" "$WORK/site/download"
cp "$HERE/assets/horix-lockup.svg" "$WORK/site/download/logo.svg"
cp "$HERE/assets/horix-favicon.svg" "$WORK/site/download/favicon.svg"
mkdir -p "$WORK/site/download/fonts"
cp "$HERE"/assets/fonts/*.woff2 "$WORK/site/download/fonts/"
# n8n webhook for new leads (GitHub secret SGPS_LEAD_WEBHOOK); server-side only, never in the page.
if [ -n "${SGPS_LEAD_WEBHOOK:-}" ]; then
  python3 -c 'import sys; u = sys.argv[1].replace("\\", "\\\\").replace("\x27", "\\\x27"); open(sys.argv[2], "w").write("<?php return [\x27lead_webhook\x27 => \x27" + u + "\x27];\n")' \
    "$SGPS_LEAD_WEBHOOK" "$WORK/site/sgps-config.php"
fi
# Licence obligations: the MIT licence text (with its copyright line) and the licences of the
# fonts and icons compiled into the app. They are plain files on the server, not shown in the UI.
cp "$WORK/src/LICENSE-MIT" "$WORK/site/LICENSE.txt"
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
} > "$WORK/site/THIRD-PARTY-NOTICES.txt"

# Nothing from the old name may be left in file names.
if ls "$WORK/site" | grep -qi photocraft; then
  echo "error: output still has photocraft file names:" >&2; ls "$WORK/site" >&2; exit 1
fi

ZIP="$OUT/sg-ps-$VERSION-hostinger.zip"
rm -f "$ZIP"
(cd "$WORK/site" && zip -qr9 "$ZIP" .)
echo "wrote $ZIP"
ls -l "$ZIP"
