#!/usr/bin/env bash
# Fetch storytold/craft-fonts at the commit the upstream source's own release pins, and print
# its path (for CRAFT_FONTS_DIR). Upstream's releases always build with it; it gives the web
# build Noto Sans Arabic (and the other listed faces) beside the wasm, so Arabic text shows in
# the browser, where there are no system fonts to fall back to.
#
# Usage: CRAFT_FONTS_DIR="$(apps/horix-common/craft-fonts.sh <unpacked-source> <work-dir>)"
# The ref is the `craft-fonts-ref:` in <source>/.github/workflows/release.yml.
set -euo pipefail

SRC="${1:?usage: craft-fonts.sh <unpacked-source> <work-dir>}"
DEST="${2:?usage: craft-fonts.sh <unpacked-source> <work-dir>}/craft-fonts"
REF="$(sed -n 's/^ *craft-fonts-ref: *\([0-9a-f]\{40\}\) *$/\1/p' "$SRC/.github/workflows/release.yml" | head -1)"
if [ -z "$REF" ]; then
  echo "craft-fonts.sh: no craft-fonts-ref in $SRC/.github/workflows/release.yml" >&2
  exit 1
fi
if [ "$(git -C "$DEST" rev-parse HEAD 2>/dev/null || true)" != "$REF" ]; then
  rm -rf "$DEST"
  mkdir -p "$DEST"
  git -C "$DEST" init -q
  git -C "$DEST" fetch -q --depth 1 https://github.com/storytold/craft-fonts "$REF"
  git -C "$DEST" checkout -q FETCH_HEAD
fi
# An absolute path: cargo and trunk read it from other directories.
(cd "$DEST" && pwd)
