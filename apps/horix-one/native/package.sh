#!/usr/bin/env bash
# Build HORIX One for the desktop: HORIX (Pixel), Horix Vectors (Vector) and Horix Layout (Layout)
# natively in one window,
# named the way HORIX Launcher reads releases.
#
# Usage: apps/horix-one/native/package.sh windows|macos
#   windows -> deploy/horix-one-desktop/horix-one-<v>-windows-x64-portable.zip
#              (horix-one.exe at the top, the AI runtime beside it, the models in models/)
#   macos   -> deploy/horix-one-desktop/horix-one-<v>-macos-universal.dmg ("HORIX One.app")
#
# prepare.sh makes the three apps' sources as their own builds do (rebrand.py and its patches), side
# by side in <work>/pixel, <work>/vector and <work>/layout; then:
#   - patches/vector and patches/layout make Horix Vectors' and Horix Layout's apps libraries too
#     (`horix_one_persona`, the Vector and Layout personas);
#   - patches/pixel makes HORIX's window host them (horix_one.rs: the persona bar and the hand-offs),
#     with HORIX One's names, and Cargo.lock is the three apps' dependencies together.
# The version is apps/horix-one/VERSION plus HORIX_BUILD_NUMBER (CI's run number).
# Needs: Rust >= 1.95 (macOS: the aarch64 and x86_64 apple-darwin targets), python3, git, 7z (Windows).
set -euo pipefail

OS="${1:?usage: package.sh windows|macos}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="$(cd "$HERE/.." && pwd)"
REPO="$(cd "$APP/../.." && pwd)"
PY="$(command -v python3 || command -v python)"
ID=horix-one
NAME="HORIX One"
VERSION="$(tr -d '[:space:]' < "$APP/VERSION")${HORIX_BUILD_NUMBER:+.$HORIX_BUILD_NUMBER}"
WORK="${HORIX_ONE_NATIVE_WORK:-$REPO/.horix-build/one-native}"
OUT="$REPO/deploy/$ID-desktop"
if [ "$OS" = windows ] && command -v cygpath >/dev/null 2>&1; then
  WORK="$(cygpath -u "$WORK")"; OUT="$(cygpath -u "$OUT")"
fi
export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$WORK/target}"
TARGET_DIR="$CARGO_TARGET_DIR"
command -v cygpath >/dev/null 2>&1 && TARGET_DIR="$(cygpath -u "$CARGO_TARGET_DIR")"

"$HERE/prepare.sh" "$WORK"
PIXEL="$WORK/pixel"
VECTOR="$WORK/vector"
LAYOUT="$WORK/layout"

licences() {
  cp "$PIXEL/LICENSE-MIT" "$1/LICENSE.txt"
  cp "$PIXEL/LICENSE-APACHE" "$1/LICENSE-APACHE.txt"
  {
    echo "HORIX One includes the following third-party material."
    for f in assets/fonts/OFL-Inter.txt assets/fonts/OFL-JetBrainsMono.txt assets/icons/LICENSE-lucide.txt assets/dict/LICENSE-SCOWL.txt; do
      printf '\n==== %s ====\n\n' "$(basename "$f")"
      cat "$PIXEL/$f"
    done
    printf '\n==== OFL-BarlowCondensed.txt ====\n\n'
    cat "$REPO/apps/sg-ps/assets/fonts/OFL-BarlowCondensed.txt"
    printf '\n==== Horix Vectors (the Vector persona) ====\n\n'
    cat "$VECTOR/NOTICE"
    printf '\n==== Horix Layout (the Layout persona) ====\n\n'
    cat "$LAYOUT/NOTICE"
    printf '\n==== MobileSAM (models/mobile_sam_image_encoder.onnx, models/sam_mask_decoder_multi.onnx) ====\n\n'
    printf 'MobileSAM, Copyright the MobileSAM authors (github.com/ChaoningZhang/MobileSAM). ONNX export by\nhuggingface.co/Acly/MobileSAM (MIT). Mask decoder from Segment Anything, Copyright Meta Platforms, Inc.\n\n'
    cat "$REPO/apps/sg-ps/ai/LICENSE-MobileSAM.txt"
    printf '\n==== Segment Anything ====\n\n'
    cat "$REPO/apps/sg-ps/ai/LICENSE-SegmentAnything.txt"
    printf '\n==== IS-Net (models/isnet-general-use.onnx) ====\n\n'
    printf 'IS-Net / DIS, Copyright Xuebin Qin et al. (github.com/xuebinqin/DIS). ONNX export by rembg\n(github.com/danielgatis/rembg, MIT).\n\n'
    cat "$REPO/apps/sg-ps/ai/LICENSE-ISNet.txt"
  } >"$1/THIRD-PARTY-NOTICES.txt"
}

rm -rf "$WORK/pkg"
mkdir -p "$WORK/pkg" "$OUT"
case "$OS" in
  windows)
    T=x86_64-pc-windows-msvc
    # As HORIX: static C runtime, no symbols, the icon and version info embedded.
    export CARGO_TARGET_X86_64_PC_WINDOWS_MSVC_RUSTFLAGS="-C target-feature=+crt-static"
    export CARGO_PROFILE_RELEASE_STRIP=symbols
    export CARGO_PROFILE_RELEASE_DEBUG=0
    export PHOTOCRAFT_REQUIRE_WINRES=1
    # Portable: Pixel keeps its settings in HORIX-Data beside the exe, Vector in VectorCraftData
    # (portable.txt), so HORIX One never shares settings (or the one-window lock) with HORIX.
    export HORIX_PORTABLE=1
    # The exe reports this version, which HORIX Launcher checks after unpacking.
    export HORIX_VERSION="$VERSION"
    (cd "$PIXEL" && cargo build --release --locked -p photocraft --target "$T")
    PKG="$WORK/pkg/win"
    mkdir -p "$PKG"
    cp "$TARGET_DIR/$T/release/photocraft.exe" "$PKG/$ID.exe"
    cp "$VECTOR/packaging/windows/portable.txt" "$PKG/portable.txt"
    printf 'HORIX One %s by Saber Group Academy\r\n\r\nRun horix-one.exe: Vector (Horix Vectors) and Pixel (HORIX) in one window; the bar at the top\r\nswitches between them and opens your work in the other one. It is portable: its settings stay\r\nin the HORIX-Data and VectorCraftData folders beside it.\r\n\r\nhttps://one.horix.live/ is HORIX One in the browser.\r\n' "$VERSION" > "$PKG/README.txt"
    # HORIX AI selection: the runtime beside the exe, the models (MobileSAM, IS-Net) in models/.
    "$PY" -I "$REPO/apps/sg-ps/ai/fetch.py" "$PKG" windows
    "$PY" -I "$REPO/apps/sg-ps/ai/fetch.py" "$PKG/models" models
    licences "$PKG"
    ZIP="$OUT/$ID-$VERSION-windows-x64-portable.zip"
    rm -f "$ZIP"
    (cd "$PKG" && 7z a -tzip -mx=9 "$ZIP" . >/dev/null)
    "$PY" -I - "$ZIP" <<'PYEOF'
import sys, zipfile
names = set(zipfile.ZipFile(sys.argv[1]).namelist())
need = {"horix-one.exe", "portable.txt", "README.txt", "onnxruntime.dll", "DirectML.dll", "LICENSE.txt",
        "THIRD-PARTY-NOTICES.txt", "models/mobile_sam_image_encoder.onnx", "models/sam_mask_decoder_multi.onnx",
        "models/isnet-general-use.onnx"}
missing = need - names
if missing:
    raise SystemExit(f"the Windows package lacks {sorted(missing)}")
PYEOF
    ;;
  macos)
    export MACOSX_DEPLOYMENT_TARGET=11.0
    (cd "$PIXEL" && cargo build --release --locked -p photocraft --target aarch64-apple-darwin --target x86_64-apple-darwin)
    BUNDLE="$WORK/pkg/$NAME.app"
    mkdir -p "$BUNDLE/Contents/MacOS" "$BUNDLE/Contents/Resources" "$BUNDLE/Contents/Frameworks"
    lipo -create -output "$BUNDLE/Contents/MacOS/$NAME" \
      "$TARGET_DIR/aarch64-apple-darwin/release/photocraft" "$TARGET_DIR/x86_64-apple-darwin/release/photocraft"
    lipo -info "$BUNDLE/Contents/MacOS/$NAME"
    cp "$APP/assets/app-icon/icon.icns" "$BUNDLE/Contents/Resources/$NAME.icns"
    licences "$BUNDLE/Contents/Resources"
    # HORIX AI selection: the runtime in Frameworks, the models in Resources/models (as HORIX).
    "$PY" -I "$REPO/apps/sg-ps/ai/fetch.py" "$BUNDLE/Contents/Frameworks" macos
    mv "$BUNDLE/Contents/Frameworks/"*-onnxruntime.txt "$BUNDLE/Contents/Resources/"
    "$PY" -I "$REPO/apps/sg-ps/ai/fetch.py" "$BUNDLE/Contents/Resources/models" models
    # HORIX's Info.plist (document types, Retina, minimum macOS) with HORIX One's names.
    "$PY" -I - "$PIXEL/packaging/macos/Info.plist.in" "$BUNDLE/Contents/Info.plist" "$VERSION" "$NAME" <<'PYEOF'
import plistlib, re, sys
src, dst, version, name = sys.argv[1:5]
text = open(src, encoding="utf-8").read()
text = text.replace("@VERSION@", version).replace("@SHORT_VERSION@", version.split("-")[0]).replace("@BUILD_SHA@", "horix-one")
text = text.replace("ai.storyteller.photocraft", "com.sabergroup.horix-one")
text = re.sub(r"PhotoCraft Document", "HORIX Document", text)
text = text.replace("<string>PhotoCraft</string>", f"<string>{name}</string>").replace("x-photocraft", "x-horix-one")
p = plistlib.loads(text.encode())
p.update({
    "CFBundleName": name, "CFBundleDisplayName": name, "CFBundleExecutable": name, "CFBundleIconFile": name,
    "LSApplicationCategoryType": "public.app-category.graphics-design",
    "NSHumanReadableCopyright": "Saber Group Academy. Built on open-source software (MIT OR Apache-2.0).",
})
for k in [k for k in p if k.startswith("PhotoCraft")]:
    p["HORIXOne" + k[len("PhotoCraft"):]] = p.pop(k)
assert "photocraft" not in plistlib.dumps(p).decode().lower(), "old name left in Info.plist"
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
    ZIP="$OUT/$ID-$VERSION-macos-universal.dmg"
    rm -f "$ZIP"
    for attempt in 1 2 3; do
      hdiutil create -quiet -fs HFS+ -format UDZO -volname "$NAME $VERSION" -srcfolder "$STAGE" "$ZIP" && break
      sleep $((attempt * 5))
    done
    [ -f "$ZIP" ] || { echo "error: hdiutil could not build $ZIP" >&2; exit 1; }
    ;;
  *)
    echo "usage: package.sh windows|macos" >&2
    exit 2
    ;;
esac
echo "wrote $ZIP"
ls -l "$ZIP"
