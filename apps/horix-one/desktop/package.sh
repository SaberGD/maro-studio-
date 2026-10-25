#!/usr/bin/env bash
# Build HORIX One for the desktop, named the way HORIX Launcher reads releases.
#
# Usage: apps/horix-one/desktop/package.sh windows|macos <site dir or HORIX One web zip>
#   windows -> deploy/horix-one-desktop/horix-one-<v>-windows-x64-portable.zip
#              (horix-one.exe at the top, the site in site/)
#   macos   -> deploy/horix-one-desktop/horix-one-<v>-macos-universal.dmg ("HORIX One.app")
# The site is the HORIX One web build (apps/horix-one/build.sh), served by the app to the system
# web view. The version is apps/horix-one/VERSION plus HORIX_BUILD_NUMBER (CI's run number).
# Needs: Rust >= 1.95 (macOS: the aarch64 and x86_64 apple-darwin targets), python3, unzip.
set -euo pipefail

OS="${1:?usage: package.sh windows|macos <site dir or zip>}"
SITE_IN="${2:?usage: package.sh windows|macos <site dir or zip>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="$(cd "$HERE/.." && pwd)"
REPO="$(cd "$APP/../.." && pwd)"
PY="$(command -v python3 || command -v python)"
ID=horix-one
NAME="HORIX One"
VERSION="$(tr -d '[:space:]' < "$APP/VERSION")${HORIX_BUILD_NUMBER:+.$HORIX_BUILD_NUMBER}"
WORK="${HORIX_ONE_DESKTOP_WORK:-$REPO/.horix-build/one-desktop}"
OUT="$REPO/deploy/$ID-desktop"
if [ "$OS" = windows ] && command -v cygpath >/dev/null 2>&1; then
  WORK="$(cygpath -u "$WORK")"; OUT="$(cygpath -u "$OUT")"; SITE_IN="$(cygpath -u "$SITE_IN")"
fi
export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$WORK/target}"
TARGET_DIR="$CARGO_TARGET_DIR"
command -v cygpath >/dev/null 2>&1 && TARGET_DIR="$(cygpath -u "$CARGO_TARGET_DIR")"

rm -rf "$WORK/pkg" "$WORK/site"
mkdir -p "$WORK/pkg" "$WORK/site" "$OUT"
# The site: a folder, or the web zip (its horix-one/ folder).
if [ -d "$SITE_IN" ]; then
  cp -R "$SITE_IN/." "$WORK/site/"
else
  "$PY" -I -c 'import sys, zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])' "$SITE_IN" "$WORK/unzipped"
  cp -R "$WORK/unzipped/horix-one/." "$WORK/site/"
  rm -rf "$WORK/unzipped"
fi
[ -f "$WORK/site/index.html" ] && [ -f "$WORK/site/pixel/index.html" ] && [ -f "$WORK/site/vector/index.html" ] ||
  { echo "error: $SITE_IN is not a HORIX One site (index.html, pixel/, vector/)" >&2; exit 1; }
# The app serves the files as they are: no pre-compressed copies, no web-host files.
find "$WORK/site" \( -name '*.br' -o -name '*.gz' -o -name '.htaccess' -o -name '_headers' -o -name '*.php' \) -delete

case "$OS" in
  windows)
    T=x86_64-pc-windows-msvc
    # Static C runtime: runs without the Visual C++ redistributable.
    export CARGO_TARGET_X86_64_PC_WINDOWS_MSVC_RUSTFLAGS="-C target-feature=+crt-static"
    # The exe reports this version, which HORIX Launcher checks after unpacking.
    export HORIX_VERSION="$VERSION"
    (cd "$HERE" && cargo build --release --locked --target "$T")
    DIR="$WORK/pkg/win"
    mkdir -p "$DIR"
    cp "$TARGET_DIR/$T/release/$ID.exe" "$DIR/$ID.exe"
    cp -R "$WORK/site" "$DIR/site"
    printf 'HORIX One %s by Saber Group Academy\r\n\r\nRun horix-one.exe. It needs Microsoft Edge WebView2 Runtime, which Windows 10 and 11 include.\r\nhttps://one.horix.live/ is the same app in the browser.\r\n\r\nBuilt on open-source software (MIT OR Apache-2.0); the licence texts are in site/.\r\n' "$VERSION" > "$DIR/README.txt"
    ZIP="$OUT/$ID-$VERSION-windows-x64-portable.zip"
    rm -f "$ZIP"
    "$PY" -I - "$DIR" "$ZIP" <<'PYEOF'
import os, sys, zipfile
src, dst = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for base, dirs, files in os.walk(src):
        dirs.sort()
        for f in sorted(files):
            p = os.path.join(base, f)
            z.write(p, os.path.relpath(p, src).replace(os.sep, "/"))
PYEOF
    ls -l "$ZIP"
    ;;
  macos)
    export MACOSX_DEPLOYMENT_TARGET=11.0
    (cd "$HERE" && cargo build --release --locked --target aarch64-apple-darwin --target x86_64-apple-darwin)
    BUNDLE="$WORK/pkg/$NAME.app"
    mkdir -p "$BUNDLE/Contents/MacOS" "$BUNDLE/Contents/Resources"
    lipo -create -output "$BUNDLE/Contents/MacOS/$NAME" \
      "$TARGET_DIR/aarch64-apple-darwin/release/$ID" "$TARGET_DIR/x86_64-apple-darwin/release/$ID"
    lipo -info "$BUNDLE/Contents/MacOS/$NAME"
    cp "$APP/assets/app-icon/icon.icns" "$BUNDLE/Contents/Resources/$NAME.icns"
    cp -R "$WORK/site" "$BUNDLE/Contents/Resources/site"
    "$PY" -I - "$BUNDLE/Contents/Info.plist" "$VERSION" "$NAME" "$ID" <<'PYEOF'
import plistlib, sys
dst, version, name, ident = sys.argv[1:5]
plistlib.dump({
    "CFBundleName": name, "CFBundleDisplayName": name, "CFBundleExecutable": name, "CFBundleIconFile": name,
    "CFBundleIdentifier": f"ai.storyteller.{ident}", "CFBundlePackageType": "APPL", "CFBundleInfoDictionaryVersion": "6.0",
    "CFBundleShortVersionString": version, "CFBundleVersion": version, "LSMinimumSystemVersion": "11.0",
    "NSHighResolutionCapable": True, "LSApplicationCategoryType": "public.app-category.graphics-design",
    "NSHumanReadableCopyright": "Saber Group Academy. Built on open-source software (MIT OR Apache-2.0).",
}, open(dst, "wb"))
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
    echo "usage: package.sh windows|macos <site dir or zip>" >&2
    exit 2
    ;;
esac
