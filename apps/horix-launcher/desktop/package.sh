#!/usr/bin/env bash
# Build HORIX Launcher for the desktop, named the way the launcher itself reads releases
# (`<id>-<version>-<os>-<arch>[-portable].<ext>`), so it can update itself from them.
#
# Usage: apps/horix-launcher/desktop/package.sh windows|macos [craft-launcher-source.tar.gz]
#   windows -> deploy/horix-launcher-desktop/horix-launcher-<v>-windows-x64-portable.zip
#              (horix-launcher.exe at the top, portable.txt beside it: settings stay next to it)
#   macos   -> deploy/horix-launcher-desktop/horix-launcher-<v>-macos-universal.dmg
#              ("HORIX Launcher.app", Apple Silicon + Intel, ad-hoc signed)
# Needs: Rust >= 1.95 (macOS: the aarch64 and x86_64 apple-darwin targets), python3, zip/hdiutil.
set -euo pipefail

TARGET="${1:?usage: package.sh windows|macos [source.tar.gz]}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
SRC_TGZ="${2:-$REPO/archive/craft-launcher/craft-launcher-source-0.4.1.tar.gz}"
WORK="${HORIX_LAUNCHER_WORK:-$REPO/.horix-build/launcher-desktop}"
OUT="$REPO/deploy/horix-launcher-desktop"
PY="$(command -v python3 || command -v python)"
VERSION="$(tr -d '[:space:]' < "$HERE/../VERSION")"
NAME="HORIX Launcher"

rm -rf "$WORK/src" "$WORK/pkg"
mkdir -p "$WORK/src" "$WORK/pkg" "$OUT"
tar -xzf "$SRC_TGZ" -C "$WORK/src" --strip-components=1
"$PY" -I "$HERE/../rebrand.py" "$WORK/src"
export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$WORK/target}"
export ARTCRAFT_LAUNCHER_BUILD_SHA="${GITHUB_SHA:-local}"

licences() {
  cp "$WORK/src/LICENSE-MIT" "$WORK/src/LICENSE-APACHE" "$WORK/src/NOTICE" "$1/"
}

case "$TARGET" in
  windows)
    (cd "$WORK/src" && cargo build --release --locked -p artcraft-launcher)
    DIR="$WORK/pkg/win"
    mkdir -p "$DIR"
    cp "$CARGO_TARGET_DIR/release/horix-launcher.exe" "$DIR/"
    cp "$WORK/src/packaging/windows/portable.txt" "$DIR/portable.txt"
    licences "$DIR"
    ZIP="$OUT/horix-launcher-$VERSION-windows-x64-portable.zip"
    rm -f "$ZIP"
    # Files at the top of the zip: the launcher looks for <id>.exe there when it updates itself.
    "$PY" -I - "$DIR" "$ZIP" <<'PYEOF'
import sys, zipfile
from pathlib import Path
src, dst = Path(sys.argv[1]), sys.argv[2]
with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for f in sorted(src.iterdir()):
        z.write(f, f.name)
PYEOF
    ls -l "$ZIP"
    ;;
  macos)
    export MACOSX_DEPLOYMENT_TARGET=11.0
    (cd "$WORK/src" && cargo build --release --locked -p artcraft-launcher --target aarch64-apple-darwin --target x86_64-apple-darwin)
    APP="$WORK/pkg/$NAME.app"
    mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
    lipo -create -output "$APP/Contents/MacOS/$NAME" \
      "$CARGO_TARGET_DIR/aarch64-apple-darwin/release/horix-launcher" \
      "$CARGO_TARGET_DIR/x86_64-apple-darwin/release/horix-launcher"
    lipo -info "$APP/Contents/MacOS/$NAME"
    cp "$WORK/src/assets/app-icon/artcraft-launcher.icns" "$APP/Contents/Resources/$NAME.icns"
    licences "$APP/Contents/Resources"
    # Upstream's Info.plist with HORIX names (the launcher reads the bundle's version back).
    "$PY" -I - "$WORK/src/packaging/macos/Info.plist.in" "$APP/Contents/Info.plist" "$VERSION" <<'PYEOF'
import sys
src, dst, version = sys.argv[1:4]
t = open(src, encoding="utf-8").read()
t = t.replace("@VERSION@", version).replace("@SHORT_VERSION@", version.split("-")[0]).replace("@BUILD_SHA@", "horix")
t = t.replace("ArtCraft Launcher", "HORIX Launcher").replace("ai.storyteller.artcraft-launcher", "ai.storyteller.horix-launcher")
t = t.replace("ArtCraftLauncher", "HORIXLauncher")
t = t.replace("Copyright © 2026 ArtCraft Team and the HORIX Launcher contributors. MIT OR Apache-2.0.",
              "Saber Group Academy. Built on open-source software (MIT OR Apache-2.0).")
assert "artcraft" not in t.lower().split("-->", 1)[-1], "old name left in Info.plist"
open(dst, "w", encoding="utf-8").write(t)
PYEOF
    plutil -lint "$APP/Contents/Info.plist"
    printf 'APPL????' >"$APP/Contents/PkgInfo"
    xattr -cr "$APP"
    # Ad-hoc signature: Apple Silicon runs nothing unsigned; not a Developer ID (no notarization yet).
    codesign --force --deep --sign - "$APP"
    codesign --verify --deep --strict --verbose=2 "$APP"
    STAGE="$WORK/pkg/dmg"
    mkdir -p "$STAGE"
    ditto "$APP" "$STAGE/$NAME.app"
    ln -s /Applications "$STAGE/Applications"
    DMG="$OUT/horix-launcher-$VERSION-macos-universal.dmg"
    rm -f "$DMG"
    for attempt in 1 2 3; do
      hdiutil create -quiet -fs HFS+ -format UDZO -volname "$NAME $VERSION" -srcfolder "$STAGE" "$DMG" && break
      sleep $((attempt * 5))
    done
    [ -f "$DMG" ] || { echo "error: hdiutil could not build $DMG" >&2; exit 1; }
    ls -l "$DMG"
    ;;
  *)
    echo "usage: package.sh windows|macos" >&2
    exit 2
    ;;
esac
