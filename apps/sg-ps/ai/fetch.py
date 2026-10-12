#!/usr/bin/env python3
"""Download (once, cached) and verify the files HORIX AI selection ships with.

Usage: python3 -I apps/sg-ps/ai/fetch.py <dest dir> models|windows|macos|linux

  models   MobileSAM image encoder + mask decoder (ONNX), for the web build and the desktop apps
  windows  onnxruntime.dll                       (Microsoft onnxruntime 1.22.0, MIT)
  macos    libonnxruntime.dylib (universal2)
  linux    libonnxruntime.so

Every download is checked against the SHA-256 below, so a changed or tampered file fails the
build. The cache is $HORIX_AI_CACHE (default .sgps-build/ai-cache in the repository).
"""

import hashlib
import io
import os
import shutil
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

ORT = "https://github.com/microsoft/onnxruntime/releases/download/v1.22.0/"
SAM = "https://huggingface.co/Acly/MobileSAM/resolve/main/"
FILES = {
    "mobile_sam_image_encoder.onnx": (SAM + "mobile_sam_image_encoder.onnx", "580f5fb648ea1062c0aabc26217aed56921985f03f0cbbd852bba81d760cc749"),
    "sam_mask_decoder_multi.onnx": (SAM + "sam_mask_decoder_multi.onnx", "8976b90a87ba50a6a72217a5ff994f7d25ce16f2229fcc1ed259e1294c622ffe"),
    "onnxruntime-win-x64-1.22.0.zip": (ORT + "onnxruntime-win-x64-1.22.0.zip", "174c616efc0271194488642a72f1a514e01487da4dfe84c49296d66e40ebe0da"),
    "onnxruntime-osx-universal2-1.22.0.tgz": (ORT + "onnxruntime-osx-universal2-1.22.0.tgz", "cfa6f6584d87555ed9f6e7e8a000d3947554d589efe3723b8bfa358cd263d03c"),
    "onnxruntime-linux-x64-1.22.0.tgz": (ORT + "onnxruntime-linux-x64-1.22.0.tgz", None),
}
ROOT = Path(__file__).resolve().parents[3]


def get(name: str) -> bytes:
    url, sha = FILES[name]
    cache = Path(os.environ.get("HORIX_AI_CACHE") or ROOT / ".sgps-build" / "ai-cache")
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / name
    if not path.is_file():
        print(f"fetch: downloading {url}", file=sys.stderr)
        tmp = path.with_suffix(".part")
        with urllib.request.urlopen(url, timeout=600) as r, open(tmp, "wb") as f:
            shutil.copyfileobj(r, f)
        tmp.replace(path)
    data = path.read_bytes()
    got = hashlib.sha256(data).hexdigest()
    if sha and got != sha:
        path.unlink()
        sys.exit(f"fetch: {name}: SHA-256 {got} does not match {sha}")
    return data


def member(archive: bytes, kind: str, suffix: str) -> bytes:
    if kind == "zip":
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            n = next(n for n in z.namelist() if n.endswith(suffix))
            return z.read(n)
    with tarfile.open(fileobj=io.BytesIO(archive)) as t:
        m = next(m for m in t.getmembers() if m.name.endswith(suffix) and m.isfile())
        f = t.extractfile(m)
        assert f is not None
        return f.read()


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    dest, what = Path(sys.argv[1]), sys.argv[2]
    dest.mkdir(parents=True, exist_ok=True)
    if what == "models":
        for n in ("mobile_sam_image_encoder.onnx", "sam_mask_decoder_multi.onnx"):
            (dest / n).write_bytes(get(n))
    elif what in ("windows", "macos", "linux"):
        name, kind, lib, out = {
            "windows": ("onnxruntime-win-x64-1.22.0.zip", "zip", "lib/onnxruntime.dll", "onnxruntime.dll"),
            "macos": ("onnxruntime-osx-universal2-1.22.0.tgz", "tgz", "lib/libonnxruntime.1.22.0.dylib", "libonnxruntime.dylib"),
            "linux": ("onnxruntime-linux-x64-1.22.0.tgz", "tgz", "lib/libonnxruntime.so.1.22.0", "libonnxruntime.so"),
        }[what]
        a = get(name)
        (dest / out).write_bytes(member(a, kind, lib))
        (dest / "LICENSE-onnxruntime.txt").write_bytes(member(a, kind, "/LICENSE"))
        (dest / "ThirdPartyNotices-onnxruntime.txt").write_bytes(member(a, kind, "/ThirdPartyNotices.txt"))
    else:
        sys.exit(__doc__)
    print(f"fetch: {what} -> {dest}", file=sys.stderr)


if __name__ == "__main__":
    main()
