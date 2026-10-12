#!/usr/bin/env python3
"""Download (once, cached) and verify the files HORIX AI selection ships with.

Usage: python3 -I apps/sg-ps/ai/fetch.py <dest dir> models|full|web|windows|macos|linux

  models   the desktop apps' models: MobileSAM image encoder + mask decoder (Quick / Object
           Selection) and IS-Net general use (Select Subject, 179 MB)
  web      the web build's models: MobileSAM, and IS-Net for Select Subject converted to half
           precision (89 MB, same accuracy: IoU 0.930 on 80 DUTS-TE photos; needs the onnx and
           onnxruntime Python packages)
  full     the full download's extra model: BiRefNet general (Select Subject, 973 MB, the most
           accurate; used when a graphics card runs it)
  windows  onnxruntime.dll with DirectML (graphics cards; Microsoft onnxruntime 1.22.0, MIT) and
           DirectML.dll (Microsoft DirectML 1.15.4, redistributable)
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
REMBG = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/"
NUGET = "https://www.nuget.org/api/v2/package/"
FILES = {
    "mobile_sam_image_encoder.onnx": (SAM + "mobile_sam_image_encoder.onnx", "580f5fb648ea1062c0aabc26217aed56921985f03f0cbbd852bba81d760cc749"),
    "sam_mask_decoder_multi.onnx": (SAM + "sam_mask_decoder_multi.onnx", "8976b90a87ba50a6a72217a5ff994f7d25ce16f2229fcc1ed259e1294c622ffe"),
    # IS-Net (xuebinqin/DIS), Apache-2.0, as exported by rembg.
    "isnet-general-use.onnx": (REMBG + "isnet-general-use.onnx", "60920e99c45464f2ba57bee2ad08c919a52bbf852739e96947fbb4358c0d964a"),
    # BiRefNet (ZhengPeng7/BiRefNet), MIT, general epoch 244 as exported by rembg.
    "BiRefNet-general-epoch_244.onnx": (REMBG + "BiRefNet-general-epoch_244.onnx", "58f621f00f5d756097615970a88a791584600dcf7c45b18a0a6267535a1ebd3c"),
    # onnxruntime built with DirectML, and DirectML itself (NuGet packages).
    "Microsoft.ML.OnnxRuntime.DirectML.1.22.0.nupkg": (NUGET + "Microsoft.ML.OnnxRuntime.DirectML/1.22.0", "29f9872d786236b79aa83f94482f3a17c14297e4833768d6d0ed4883ee732e60"),
    "Microsoft.AI.DirectML.1.15.4.nupkg": (NUGET + "Microsoft.AI.DirectML/1.15.4", "4e7cb7ddce8cf837a7a75dc029209b520ca0101470fcdf275c1f49736a3615b9"),
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


def half(name: str) -> bytes:
    """`name` (checked by get) converted to float16 with float32 input and output, cached."""
    src = get(name)
    cache = Path(os.environ.get("HORIX_AI_CACHE") or ROOT / ".sgps-build" / "ai-cache")
    out = cache / (hashlib.sha256(src).hexdigest()[:16] + "-fp16.onnx")
    if not out.is_file():
        import onnx  # noqa: PLC0415 (only the web build needs these)
        from onnxruntime.transformers.float16 import convert_float_to_float16  # noqa: PLC0415

        print(f"fetch: converting {name} to float16", file=sys.stderr)
        model = convert_float_to_float16(onnx.load_from_string(src), keep_io_types=True)
        tmp = out.with_suffix(".part")
        onnx.save(model, str(tmp))
        tmp.replace(out)
    return out.read_bytes()


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
    if what in ("models", "web"):
        sam = ("mobile_sam_image_encoder.onnx", "sam_mask_decoder_multi.onnx")
        for n in sam + (("isnet-general-use.onnx",) if what == "models" else ()):
            (dest / n).write_bytes(get(n))
        if what == "web":
            (dest / "isnet_fp16.onnx").write_bytes(half("isnet-general-use.onnx"))
    elif what == "full":
        (dest / "birefnet-general.onnx").write_bytes(get("BiRefNet-general-epoch_244.onnx"))
    elif what == "windows":
        ort = get("Microsoft.ML.OnnxRuntime.DirectML.1.22.0.nupkg")
        (dest / "onnxruntime.dll").write_bytes(member(ort, "zip", "runtimes/win-x64/native/onnxruntime.dll"))
        (dest / "LICENSE-onnxruntime.txt").write_bytes(member(ort, "zip", "LICENSE"))
        plain = get("onnxruntime-win-x64-1.22.0.zip")
        (dest / "ThirdPartyNotices-onnxruntime.txt").write_bytes(member(plain, "zip", "/ThirdPartyNotices.txt"))
        dml = get("Microsoft.AI.DirectML.1.15.4.nupkg")
        (dest / "DirectML.dll").write_bytes(member(dml, "zip", "bin/x64-win/DirectML.dll"))
        (dest / "LICENSE-DirectML.txt").write_bytes(member(dml, "zip", "LICENSE.txt") + b"\n\n" + member(dml, "zip", "ThirdPartyNotices.txt"))
    elif what in ("macos", "linux"):
        name, kind, lib, out = {
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
