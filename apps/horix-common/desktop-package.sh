#!/usr/bin/env bash
# Build Horix Vectors or Horix Light for the desktop, named the way HORIX Launcher reads releases.
#
# Usage: apps/horix-common/desktop-package.sh vectors|light windows|macos
#   windows -> deploy/horix-<app>-desktop/horix-<app>-<v>-windows-x64-portable.zip
#              (horix-<app>.exe at the top, portable.txt beside it)
#   macos   -> deploy/horix-<app>-desktop/horix-<app>-<v>-macos-universal.dmg ("Horix <App>.app")
# The version is apps/horix-<app>/VERSION plus HORIX_BUILD_NUMBER (CI's run number): 0.1.12.
# Needs: Rust >= 1.95 (macOS: the aarch64 and x86_64 apple-darwin targets), python3.
set -euo pipefail

APP="${1:?usage: desktop-package.sh vectors|light windows|macos}"
OS="${2:?usage: desktop-package.sh vectors|light windows|macos}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
PY="$(command -v python3 || command -v python)"
case "$APP" in
  vectors) UP=vectorcraft; UPNAME=VectorCraft; NAME="Horix Vectors"; SRC_TGZ="$REPO/archive/vectorcraft/vectorcraft-source-0.16.0.tar.gz" ;;
  light) UP=lightcraft; UPNAME=LightCraft; NAME="Horix Light"; SRC_TGZ="$REPO/archive/lightcraft/lightcraft-source-0.13.0.tar.gz" ;;
  *) echo "unknown app $APP" >&2; exit 2 ;;
esac
ID="horix-$APP"
VERSION="$(tr -d '[:space:]' < "$REPO/apps/$ID/VERSION")${HORIX_BUILD_NUMBER:+.$HORIX_BUILD_NUMBER}"
WORK="${HORIX_DESKTOP_WORK:-$REPO/.horix-build/$ID-desktop}"
OUT="$REPO/deploy/$ID-desktop"
TAR_LOCAL=()
if [ "$OS" = windows ] && command -v cygpath >/dev/null 2>&1; then
  WORK="$(cygpath -u "$WORK")"; OUT="$(cygpath -u "$OUT")"; SRC_TGZ="$(cygpath -u "$SRC_TGZ")"
  TAR_LOCAL=(--force-local)
fi
export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$WORK/target}"
TARGET_DIR="$CARGO_TARGET_DIR"
command -v cygpath >/dev/null 2>&1 && TARGET_DIR="$(cygpath -u "$CARGO_TARGET_DIR")"

rm -rf "$WORK/src" "$WORK/pkg"
mkdir -p "$WORK/src" "$WORK/pkg" "$OUT"
tar ${TAR_LOCAL[@]+"${TAR_LOCAL[@]}"} -xzf "$SRC_TGZ" -C "$WORK/src" --strip-components=1
"$PY" -I "$REPO/apps/$ID/rebrand.py" "$WORK/src"

licences() {
  for f in LICENSE-MIT LICENSE-APACHE NOTICE; do cp "$WORK/src/$f" "$1/"; done
}

case "$OS" in
  windows)
    T=x86_64-pc-windows-msvc
    # Static C runtime, as upstream: runs without the Visual C++ redistributable.
    export CARGO_TARGET_X86_64_PC_WINDOWS_MSVC_RUSTFLAGS="-C target-feature=+crt-static"
    # The exe reports this version, which HORIX Launcher checks after unpacking (horix_rebrand.exe_version).
    export HORIX_VERSION="$VERSION"
    (cd "$WORK/src" && cargo build --release --locked -p "$UP" --target "$T")
    DIR="$WORK/pkg/win"
    mkdir -p "$DIR"
    # The launcher runs <id>.exe from the top of the zip.
    cp "$TARGET_DIR/$T/release/$UP.exe" "$DIR/$ID.exe"
    if [ -f "$WORK/src/packaging/windows/portable.txt" ]; then cp "$WORK/src/packaging/windows/portable.txt" "$DIR/"; fi
    licences "$DIR"
    ZIP="$OUT/$ID-$VERSION-windows-x64-portable.zip"
    rm -f "$ZIP"
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
    (cd "$WORK/src" && cargo build --release --locked -p "$UP" --target aarch64-apple-darwin --target x86_64-apple-darwin)
    BUNDLE="$WORK/pkg/$NAME.app"
    mkdir -p "$BUNDLE/Contents/MacOS" "$BUNDLE/Contents/Resources"
    lipo -create -output "$BUNDLE/Contents/MacOS/$NAME" \
      "$TARGET_DIR/aarch64-apple-darwin/release/$UP" "$TARGET_DIR/x86_64-apple-darwin/release/$UP"
    lipo -info "$BUNDLE/Contents/MacOS/$NAME"
    cp "$WORK/src/assets/app-icon/$UP.icns" "$BUNDLE/Contents/Resources/$NAME.icns"
    licences "$BUNDLE/Contents/Resources"
    # Upstream's Info.plist (document types, minimum macOS) with the HORIX name and version: the
    # launcher reads the installed version back from it.
    "$PY" -I - "$WORK/src/packaging/macos/Info.plist.in" "$BUNDLE/Contents/Info.plist" "$VERSION" "$UPNAME" "$NAME" "$UP" "$ID" <<'PYEOF'
import plistlib, re, sys
src, dst, version, upname, name, up, ident = sys.argv[1:8]
t = open(src, encoding="utf-8").read()
t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
for k in ("@VERSION@", "@SHORT_VERSION@"):
    t = t.replace(k, version if k == "@VERSION@" else version.split("-")[0])
t = re.sub(r"@[A-Z_]+@", "horix", t)
t = t.replace(f"ai.storyteller.{up}", f"ai.storyteller.{ident}").replace(upname, name)
p = plistlib.loads(t.encode())
p.update({"CFBundleName": name, "CFBundleDisplayName": name, "CFBundleExecutable": name, "CFBundleIconFile": name,
          "NSHumanReadableCopyright": "Saber Group Academy. Built on open-source software (MIT OR Apache-2.0)."})
plistlib.dump(p, open(dst, "wb"))
PYEOF
    plutil -lint "$BUNDLE/Contents/Info.plist"
    printf 'APPL????' >"$BUNDLE/Contents/PkgInfo"
    xattr -cr "$BUNDLE"
    # Ad-hoc signature: Apple Silicon runs nothing unsigned; not a Developer ID.
    codesign --force --deep --sign - "$BUNDLE"
    codesign --verify --deep --strict --verbose=2 "$BUNDLE"
    STAGE="$WORK/pkg/dmg"
    mkdir -p "$STAGE"
    ditto "$BUNDLE" "$STAGE/$NAME.app"
    ln -s /Applications "$STAGE/Applications"
    DMG="$OUT/$ID-$VERSION-macos-universal.dmg"
    rm -f "$DMG"
    for attempt in 1 2 3; do
      hdiutil create -quiet -fs HFS+ -format UDZO -volname "$NAME $VERSION" -srcfolder "$STAGE" "$DMG" && break
      sleep $((attempt * 5))
    done
    [ -f "$DMG" ] || { echo "error: hdiutil could not build $DMG" >&2; exit 1; }
    ls -l "$DMG"
    ;;
  *)
    echo "usage: desktop-package.sh vectors|light windows|macos" >&2
    exit 2
    ;;
esac
