#!/usr/bin/env bash
# Prepare HORIX One's native sources in <work>: <work>/pixel (HORIX, which builds the app) and
# <work>/vector (Horix Vectors, the Vector persona), side by side as pixel/apps/photocraft's
# Cargo.toml expects. package.sh runs this; on Linux it is enough to try the app:
#   apps/horix-one/native/prepare.sh /tmp/one && (cd /tmp/one/pixel && cargo run -p photocraft)
set -euo pipefail

WORK="${1:?usage: prepare.sh <work dir>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="$(cd "$HERE/.." && pwd)"
REPO="$(cd "$APP/../.." && pwd)"
PY="$(command -v python3 || command -v python)"
PIXEL_TGZ="$REPO/archive/photocraft/photocraft-source-0.15.1.tar.gz"
VECTOR_TGZ="$REPO/archive/vectorcraft/vectorcraft-source-0.16.0.tar.gz"
TAR_LOCAL=()
if command -v cygpath >/dev/null 2>&1; then
  WORK="$(cygpath -u "$WORK")"; PIXEL_TGZ="$(cygpath -u "$PIXEL_TGZ")"; VECTOR_TGZ="$(cygpath -u "$VECTOR_TGZ")"
  TAR_LOCAL=(--force-local)
fi

rm -rf "$WORK/pixel" "$WORK/vector"
mkdir -p "$WORK/pixel" "$WORK/vector"
tar ${TAR_LOCAL[@]+"${TAR_LOCAL[@]}"} -xzf "$PIXEL_TGZ" -C "$WORK/pixel" --strip-components=1
tar ${TAR_LOCAL[@]+"${TAR_LOCAL[@]}"} -xzf "$VECTOR_TGZ" -C "$WORK/vector" --strip-components=1
# Each app as its own build makes it: names, icons, menus and HORIX's patches (AI, UX, the web API).
"$PY" -I "$REPO/apps/sg-ps/rebrand.py" "$WORK/pixel"
"$PY" -I "$REPO/apps/horix-vectors/rebrand.py" "$WORK/vector"

# HORIX One's changes on top.
for side in vector pixel; do
  "$PY" -I - "$REPO/apps/horix-common" "$WORK/$side" "$HERE/patches/$side" <<'PYEOF'
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import horix_rebrand as hx
hx.apply_patches(Path(sys.argv[2]), Path(sys.argv[3]))
PYEOF
done
cp "$HERE/horix_one.rs" "$WORK/pixel/apps/photocraft/src/horix_one.rs"
cp "$HERE/Cargo.lock" "$WORK/pixel/Cargo.lock"
# HORIX One's icon where HORIX's was (the window, the Windows exe, the Linux desktop entry).
ICONS="$APP/assets/app-icon"
cp "$ICONS/icon.ico" "$WORK/pixel/assets/app-icon/photocraft.ico"
cp "$ICONS/icon.icns" "$WORK/pixel/assets/app-icon/photocraft.icns"
cp "$ICONS/icon-1024.png" "$WORK/pixel/assets/app-icon/photocraft-1024.png"
cp "$ICONS/icon-256.png" "$WORK/pixel/assets/app-icon/hicolor/256x256/apps/ai.storyteller.photocraft.png"
echo "HORIX One sources ready in $WORK (build in $WORK/pixel: cargo build -p photocraft)"
