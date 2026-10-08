#!/usr/bin/env bash
# Build the SG - PS desktop app and package it.
#
# Usage: apps/sg-ps/desktop/package.sh windows|macos
#   windows -> deploy/sg-ps-desktop/SG-PS-<version>-windows-x64-portable.zip  (unzip and run SG-PS.exe)
#   macos   -> deploy/sg-ps-desktop/SG-PS-<version>-macos-universal.zip       ("SG - PS.app", Apple Silicon + Intel)
# Runs on the matching OS (Git Bash on Windows). Needs Rust; on macOS the aarch64-apple-darwin and
# x86_64-apple-darwin targets. Not code-signed: Windows SmartScreen and macOS Gatekeeper warn on
# first launch (see apps/sg-ps/README.md).
set -euo pipefail

OS="${1:?usage: package.sh windows|macos}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
SRC_TGZ="${SRC_TGZ:-$REPO/archive/photocraft/photocraft-source-0.3.0.tar.gz}"
WORK="${SGPS_WORK:-$REPO/.sgps-build}"
OUT="$REPO/deploy/sg-ps-desktop"
export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$WORK/target}"
PY="$(command -v python3 || command -v python)"

rm -rf "$WORK/src" "$WORK/pkg"
mkdir -p "$WORK/src" "$WORK/pkg" "$OUT"
tar -xzf "$SRC_TGZ" -C "$WORK/src" --strip-components=1
VERSION="$(sed -n 's/^version = "\(.*\)"/\1/p' "$WORK/src/Cargo.toml" | head -1)"
"$PY" -I "$HERE/../rebrand.py" "$WORK/src"

licences() {
  cp "$WORK/src/LICENSE-MIT" "$1/LICENSE.txt"
  {
    echo "SG - PS includes the following third-party material."
    for f in assets/fonts/OFL-Inter.txt assets/fonts/OFL-JetBrainsMono.txt assets/icons/LICENSE-lucide.txt assets/dict/LICENSE-SCOWL.txt; do
      printf '\n==== %s ====\n\n' "$(basename "$f")"
      cat "$WORK/src/$f"
    done
  } >"$1/THIRD-PARTY-NOTICES.txt"
}

case "$OS" in
  windows)
    T=x86_64-pc-windows-msvc
    # Static C runtime: runs without the Visual C++ redistributable. Icon and version info must embed.
    export CARGO_TARGET_X86_64_PC_WINDOWS_MSVC_RUSTFLAGS="-C target-feature=+crt-static"
    export PHOTOCRAFT_REQUIRE_WINRES=1
    (cd "$WORK/src" && cargo build --release --locked -p photocraft --target "$T")
    PKG="$WORK/pkg/SG-PS"
    mkdir -p "$PKG"
    cp "$CARGO_TARGET_DIR/$T/release/photocraft.exe" "$PKG/SG-PS.exe"
    cat >"$PKG/portable.txt" <<'TXT'
SG - PS portable mode

While this file sits next to SG-PS.exe, SG - PS keeps its preferences, brushes and recovery
autosaves in the SG-PS-Data folder beside it and writes nothing to %APPDATA%. Copy the whole
folder to move SG - PS with its settings. Delete this file to use %APPDATA%\SG - PS instead.

Saber Group Academy - https://www.facebook.com/SABERGROUP.Courses/
TXT
    licences "$PKG"
    ZIP="$OUT/SG-PS-$VERSION-windows-x64-portable.zip"
    rm -f "$ZIP"
    (cd "$WORK/pkg" && 7z a -tzip -mx=9 "$ZIP" SG-PS >/dev/null)
    ;;
  macos)
    export MACOSX_DEPLOYMENT_TARGET=11.0
    (cd "$WORK/src" && cargo build --release --locked -p photocraft --target aarch64-apple-darwin --target x86_64-apple-darwin)
    APP="$WORK/pkg/SG - PS.app"
    mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
    lipo -create -output "$APP/Contents/MacOS/SG-PS" \
      "$CARGO_TARGET_DIR/aarch64-apple-darwin/release/photocraft" \
      "$CARGO_TARGET_DIR/x86_64-apple-darwin/release/photocraft"
    lipo -info "$APP/Contents/MacOS/SG-PS"
    cp "$WORK/src/assets/app-icon/photocraft.icns" "$APP/Contents/Resources/SG-PS.icns"
    licences "$APP/Contents/Resources"
    # Upstream's Info.plist (document types, Retina, minimum macOS) with SG - PS names.
    "$PY" -I - "$WORK/src/packaging/macos/Info.plist.in" "$APP/Contents/Info.plist" "$VERSION" <<'PYEOF'
import plistlib, re, sys
src, dst, version = sys.argv[1:4]
text = open(src, encoding="utf-8").read()
short = version.split("-")[0]
text = text.replace("@VERSION@", version).replace("@SHORT_VERSION@", short).replace("@BUILD_SHA@", "sg-ps")
text = text.replace("ai.storyteller.photocraft", "com.sabergroup.sgps")
text = re.sub(r"PhotoCraft Document", "SG - PS Document", text)
text = text.replace("<string>PhotoCraft</string>", "<string>SG-PS</string>").replace("x-photocraft", "x-sgps")
p = plistlib.loads(text.encode())
p.update({
    "CFBundleName": "SG - PS",
    "CFBundleDisplayName": "SG - PS",
    "CFBundleExecutable": "SG-PS",
    "CFBundleIconFile": "SG-PS",
    "NSHumanReadableCopyright": "Saber Group Academy. Built on open-source software (MIT).",
})
for k in [k for k in p if k.startswith("PhotoCraft")]:
    p["SGPS" + k[len("PhotoCraft"):]] = p.pop(k)
assert "photocraft" not in plistlib.dumps(p).decode().lower(), "old name left in Info.plist"
plistlib.dump(p, open(dst, "wb"))
PYEOF
    plutil -lint "$APP/Contents/Info.plist"
    printf 'APPL????' >"$APP/Contents/PkgInfo"
    # Ad-hoc signature: required for Apple Silicon to run it at all; not a Developer ID.
    codesign --force --deep --sign - "$APP"
    codesign --verify --deep --strict --verbose=2 "$APP"
    ZIP="$OUT/SG-PS-$VERSION-macos-universal.zip"
    rm -f "$ZIP"
    (cd "$WORK/pkg" && ditto -c -k --keepParent "SG - PS.app" "$ZIP")
    ;;
  *)
    echo "usage: package.sh windows|macos" >&2
    exit 2
    ;;
esac

echo "wrote $ZIP"
ls -l "$ZIP"
