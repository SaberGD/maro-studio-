#!/usr/bin/env bash
# Build the HORIX desktop app and package it.
#
# Usage: apps/sg-ps/desktop/package.sh windows|macos
#   windows -> deploy/sg-ps-desktop/HORIX-<version>-windows-x64.zip           (unzip and run HORIX.exe)
#   macos   -> deploy/sg-ps-desktop/HORIX-<version>-macos-universal.zip       ("HORIX.app", Apple Silicon + Intel)
# Runs on the matching OS (Git Bash on Windows). Needs Rust; on macOS the aarch64-apple-darwin and
# x86_64-apple-darwin targets. Not code-signed: Windows SmartScreen and macOS Gatekeeper warn on
# first launch (see apps/sg-ps/README.md).
set -euo pipefail

OS="${1:?usage: package.sh windows|macos}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
SRC_TGZ="${SRC_TGZ:-$REPO/archive/photocraft/photocraft-source-0.15.1.tar.gz}"
WORK="${SGPS_WORK:-$REPO/.sgps-build}"
OUT="$REPO/deploy/sg-ps-desktop"
export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$WORK/target}"
PY="$(command -v python3 || command -v python)"
# Git Bash on Windows: "D:\a\..." paths confuse tar (the colon reads as a remote host) and bash
# file commands; use /d/a/... for the shell. cargo keeps reading CARGO_TARGET_DIR as given.
TARGET_DIR="$CARGO_TARGET_DIR"
TAR_LOCAL=()
if command -v cygpath >/dev/null 2>&1; then
  WORK="$(cygpath -u "$WORK")"; OUT="$(cygpath -u "$OUT")"; SRC_TGZ="$(cygpath -u "$SRC_TGZ")"
  TARGET_DIR="$(cygpath -u "$CARGO_TARGET_DIR")"
  TAR_LOCAL=(--force-local) # GNU tar (Git Bash); macOS bsdtar has no such flag
fi

rm -rf "$WORK/src" "$WORK/pkg"
mkdir -p "$WORK/src" "$WORK/pkg" "$OUT"
tar ${TAR_LOCAL[@]+"${TAR_LOCAL[@]}"} -xzf "$SRC_TGZ" -C "$WORK/src" --strip-components=1
VERSION="$(tr -d "[:space:]" < "$HERE/../VERSION")${HORIX_BUILD_NUMBER:+.$HORIX_BUILD_NUMBER}"
"$PY" -I "$HERE/../rebrand.py" "$WORK/src"

licences() {
  cp "$WORK/src/LICENSE-MIT" "$1/LICENSE.txt"
  {
    echo "HORIX includes the following third-party material."
    for f in assets/fonts/OFL-Inter.txt assets/fonts/OFL-JetBrainsMono.txt assets/icons/LICENSE-lucide.txt assets/dict/LICENSE-SCOWL.txt; do
      printf '\n==== %s ====\n\n' "$(basename "$f")"
      cat "$WORK/src/$f"
    done
    printf '\n==== OFL-BarlowCondensed.txt ====\n\n'
    cat "$HERE/../assets/fonts/OFL-BarlowCondensed.txt"
    ai_notices
  } >"$1/THIRD-PARTY-NOTICES.txt"
}

# HORIX AI selection: MobileSAM (Apache-2.0), its ONNX export (MIT, huggingface.co/Acly/MobileSAM),
# Segment Anything (Apache-2.0), IS-Net (Apache-2.0), Microsoft onnxruntime (MIT, its own notices
# file beside it) and, on Windows, Microsoft DirectML (redistributable, its licence beside it).
ai_notices() {
  printf '\n==== MobileSAM (models/mobile_sam_image_encoder.onnx, models/sam_mask_decoder_multi.onnx) ====\n\n'
  printf 'MobileSAM, Copyright the MobileSAM authors (github.com/ChaoningZhang/MobileSAM). ONNX export by\nhuggingface.co/Acly/MobileSAM (MIT). Mask decoder from Segment Anything, Copyright Meta Platforms, Inc.\n\n'
  cat "$HERE/../ai/LICENSE-MobileSAM.txt"
  printf '\n==== Segment Anything ====\n\n'
  cat "$HERE/../ai/LICENSE-SegmentAnything.txt"
  printf '\n==== IS-Net (models/isnet-general-use.onnx) ====\n\n'
  printf 'IS-Net / DIS, Copyright Xuebin Qin et al. (github.com/xuebinqin/DIS). ONNX export by rembg\n(github.com/danielgatis/rembg, MIT).\n\n'
  cat "$HERE/../ai/LICENSE-ISNet.txt"
}

windows_readme() {
  cp "$HERE/README.txt" "$1/README.txt"
  "$PY" -I - "$1/README.txt" "$VERSION" <<'PYEOF'
from pathlib import Path
import sys

path, version = Path(sys.argv[1]), sys.argv[2]
path.write_text(path.read_text(encoding="utf-8").replace("@VERSION@", version), encoding="utf-8")
PYEOF
}

case "$OS" in
  windows)
    T=x86_64-pc-windows-msvc
    # Static C runtime: runs without the Visual C++ redistributable. Icon and version info must embed.
    export CARGO_TARGET_X86_64_PC_WINDOWS_MSVC_RUSTFLAGS="-C target-feature=+crt-static"
    # Keep release internals out of the portable binary. This raises the cost of reverse
    # engineering without pretending that a desktop executable can be made opaque.
    export CARGO_PROFILE_RELEASE_STRIP=symbols
    export CARGO_PROFILE_RELEASE_DEBUG=0
    export PHOTOCRAFT_REQUIRE_WINRES=1
    # This build is portable by design. The app creates HORIX-Data beside the executable without
    # needing a visible marker file in the download package.
    export HORIX_PORTABLE=1
    # HORIX.exe reports this version, which HORIX Launcher checks after unpacking (rebrand.py).
    export HORIX_VERSION="$VERSION"
    (cd "$WORK/src" && cargo build --release --locked -p photocraft --target "$T")
    PKG="$WORK/pkg/HORIX"
    mkdir -p "$PKG"
    cp "$TARGET_DIR/$T/release/photocraft.exe" "$PKG/HORIX.exe"
    windows_readme "$PKG"
    # HORIX AI selection: the runtime beside the exe, the models (MobileSAM, IS-Net) in models/.
    "$PY" -I "$HERE/../ai/fetch.py" "$PKG" windows
    "$PY" -I "$HERE/../ai/fetch.py" "$PKG/models" models
    licences "$PKG"
    # Not "-portable.zip": on Windows (and macOS) file names ignore case, so this one and the
    # launcher's horix-<version>-windows-x64-portable.zip below would be the same file.
    ZIP="$OUT/HORIX-$VERSION-windows-x64.zip"
    rm -f "$ZIP"
    (cd "$WORK/pkg" && 7z a -tzip -mx=9 "$ZIP" HORIX >/dev/null)
    # HORIX Launcher's package: the same files at the top of the zip (it runs horix.exe from there).
    LZIP="$OUT/horix-$VERSION-windows-x64-portable.zip"
    rm -f "$LZIP"
    (cd "$PKG" && 7z a -tzip -mx=9 "$LZIP" . >/dev/null)
    "$PY" -I - "$ZIP" <<'PYEOF'
import sys
import zipfile

expected = {
    "HORIX/HORIX.exe", "HORIX/README.txt", "HORIX/onnxruntime.dll", "HORIX/LICENSE-onnxruntime.txt",
    "HORIX/ThirdPartyNotices-onnxruntime.txt", "HORIX/DirectML.dll", "HORIX/LICENSE-DirectML.txt",
    "HORIX/LICENSE.txt", "HORIX/THIRD-PARTY-NOTICES.txt",
    "HORIX/models/mobile_sam_image_encoder.onnx", "HORIX/models/sam_mask_decoder_multi.onnx",
    "HORIX/models/isnet-general-use.onnx",
}
with zipfile.ZipFile(sys.argv[1]) as archive:
    files = {name for name in archive.namelist() if not name.endswith("/")}
if files != expected:
    raise SystemExit(f"unexpected Windows package contents: {sorted(files)}")
PYEOF
    ;;
  macos)
    export MACOSX_DEPLOYMENT_TARGET=11.0
    (cd "$WORK/src" && cargo build --release --locked -p photocraft --target aarch64-apple-darwin --target x86_64-apple-darwin)
    APP="$WORK/pkg/HORIX.app"
    mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
    lipo -create -output "$APP/Contents/MacOS/HORIX" \
      "$TARGET_DIR/aarch64-apple-darwin/release/photocraft" \
      "$TARGET_DIR/x86_64-apple-darwin/release/photocraft"
    lipo -info "$APP/Contents/MacOS/HORIX"
    cp "$WORK/src/assets/app-icon/photocraft.icns" "$APP/Contents/Resources/HORIX.icns"
    licences "$APP/Contents/Resources"
    # HORIX AI selection: the runtime in Frameworks, the models in Resources/models.
    mkdir -p "$APP/Contents/Frameworks"
    "$PY" -I "$HERE/../ai/fetch.py" "$APP/Contents/Frameworks" macos
    mv "$APP/Contents/Frameworks/"*-onnxruntime.txt "$APP/Contents/Resources/"
    "$PY" -I "$HERE/../ai/fetch.py" "$APP/Contents/Resources/models" models
    # Upstream's Info.plist (document types, Retina, minimum macOS) with HORIX names.
    "$PY" -I - "$WORK/src/packaging/macos/Info.plist.in" "$APP/Contents/Info.plist" "$VERSION" <<'PYEOF'
import plistlib, re, sys
src, dst, version = sys.argv[1:4]
text = open(src, encoding="utf-8").read()
short = version.split("-")[0]
text = text.replace("@VERSION@", version).replace("@SHORT_VERSION@", short).replace("@BUILD_SHA@", "sg-ps")
text = text.replace("ai.storyteller.photocraft", "com.sabergroup.sgps")
text = re.sub(r"PhotoCraft Document", "HORIX Document", text)
text = text.replace("<string>PhotoCraft</string>", "<string>HORIX</string>").replace("x-photocraft", "x-sgps")
p = plistlib.loads(text.encode())
p.update({
    "CFBundleName": "HORIX",
    "CFBundleDisplayName": "HORIX",
    "CFBundleExecutable": "HORIX",
    "CFBundleIconFile": "HORIX",
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
    ZIP="$OUT/HORIX-$VERSION-macos-universal.zip"
    rm -f "$ZIP"
    (cd "$WORK/pkg" && ditto -c -k --keepParent "HORIX.app" "$ZIP")
    # HORIX Launcher's package: a disk image with HORIX.app (and an Applications shortcut).
    STAGE="$WORK/pkg/dmg"
    rm -rf "$STAGE" && mkdir -p "$STAGE"
    ditto "$WORK/pkg/HORIX.app" "$STAGE/HORIX.app"
    ln -s /Applications "$STAGE/Applications"
    DMG="$OUT/horix-$VERSION-macos-universal.dmg"
    rm -f "$DMG"
    for attempt in 1 2 3; do
      hdiutil create -quiet -fs HFS+ -format UDZO -volname "HORIX $VERSION" -srcfolder "$STAGE" "$DMG" && break
      sleep $((attempt * 5))
    done
    [ -f "$DMG" ] || { echo "error: hdiutil could not build $DMG" >&2; exit 1; }
    ;;
  *)
    echo "usage: package.sh windows|macos" >&2
    exit 2
    ;;
esac

echo "wrote $ZIP"
ls -l "$ZIP"
