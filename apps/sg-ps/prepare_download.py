#!/usr/bin/env python3
"""Stamp the staged landing page and give CSS/JS content-addressed URLs.

Run after copying hosting/download into the build directory. Source files are
left untouched. Old URLs may remain on the host because deploy is additive.
"""
import hashlib
import html
import re
import sys
from pathlib import Path


def prepare(directory: Path, build_id: str) -> None:
    index = directory / "index.html"
    markup = index.read_text(encoding="utf-8")
    markup = re.sub(r'\s*<meta name="horix-build" content="[^"]*">', "", markup)
    markup = markup.replace(
        "<head>", '<head>\n  <meta name="horix-build" content="' +
        html.escape(build_id, quote=True) + '">', 1
    )
    for stem, extension in (("styles", "css"), ("script", "js")):
        content = (directory / f"{stem}.{extension}").read_bytes()
        digest = hashlib.sha256(content).hexdigest()[:16]
        filename = f"{stem}.{digest}.{extension}"
        (directory / filename).write_bytes(content)
        pattern = rf'(["\x27]){stem}(?:\.[a-f0-9]{{16}})?\.{extension}(?:\?[^"\x27]*)?\1'
        markup, count = re.subn(pattern, lambda match: match[1] + filename + match[1], markup)
        if count != 1:
            raise ValueError(f"Expected one {stem}.{extension} reference, found {count}")
    index.write_text(markup, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: prepare_download.py STAGED_DIRECTORY BUILD_ID")
    prepare(Path(sys.argv[1]), sys.argv[2])
