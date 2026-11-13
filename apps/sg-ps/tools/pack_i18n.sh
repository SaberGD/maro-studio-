#!/usr/bin/env bash
# Pack the Arabic catalogs of storytold/craft-i18n at one commit, for rebrand.py (i18n()).
# Usage: apps/sg-ps/tools/pack_i18n.sh <craft-i18n commit, the one in PhotoCraft's craft-i18n.rev>
# Output: archive/photocraft/craft-i18n-<first 8 of the commit>-ar.tar.gz
set -euo pipefail
REV="${1:?usage: pack_i18n.sh <commit>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$HERE/../../../archive/photocraft/craft-i18n-${REV:0:8}-ar.tar.gz"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git clone -q --filter=blob:none --no-checkout https://github.com/storytold/craft-i18n "$TMP/c"
git -C "$TMP/c" checkout -q "$REV"
(cd "$TMP/c" && tar --sort=name --mtime='2026-01-01' --owner=0 --group=0 -czf "$OUT" \
  LICENSE-MIT LICENSE-APACHE locales/ar/common.tsv locales/ar/photocraft.tsv)
sha256sum "$OUT"
