"""The Mac downloads on horix.si/mac/: each HORIX app's newest disk image under a name that stays.

HORIX Launcher is Windows only (on the Mac it installs only Developer ID-signed apps), so Mac users
download each app from horix.si. This picks the newest release of every app (the same releases the
launcher feed lists), downloads the disk images whose version changed since the last run, and
writes latest.json (version, file, size per app) for the download page.

Usage: GITHUB_TOKEN=... python3 -I apps/horix-common/mac_downloads.py <out dir> [<live latest.json URL>]
Writes <out dir>/<File>.dmg for each changed app and <out dir>/latest.json; prints the files to upload.
"""

import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "horix-launcher/feed"))
import make_feed  # noqa: E402

# (launcher id, tag prefix, file name on horix.si/mac/)
APPS = [
    ("horix", "horix-v", "HORIX.dmg"),
    ("horix-vectors", "horix-vectors-v", "Horix-Vectors.dmg"),
    ("horix-light", "horix-light-v", "Horix-Light.dmg"),
    ("horix-one", "horix-one-v", "HORIX-One.dmg"),
]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"


def live(url: str) -> dict:
    """What horix.si serves now ({} when there is nothing yet)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except (OSError, ValueError):
        return {}


def main() -> None:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    data = live(sys.argv[2]) if len(sys.argv) > 2 else {}
    rels = make_feed.releases()
    changed = []
    for ident, prefix, name in APPS:
        e = make_feed.entry(ident, prefix, rels, "")["latest_release"]
        dmg = next((a for a in (e or {}).get("assets", []) if a["name"].startswith(f"{ident}-") and a["name"].endswith("-macos-universal.dmg")), None)
        if not dmg:
            print(f"{ident}: no Mac disk image released yet", file=sys.stderr)
            continue
        if data.get(ident, {}).get("version") == e["version"] and data[ident].get("size") == dmg["size_bytes"]:
            print(f"{ident}: {e['version']} is already on horix.si", file=sys.stderr)
            continue
        print(f"{ident}: downloading {dmg['name']} ({dmg['size_bytes']} bytes)", file=sys.stderr)
        urllib.request.urlretrieve(dmg["download_url"], out / name)
        if (out / name).stat().st_size != dmg["size_bytes"]:
            sys.exit(f"{ident}: {dmg['name']} downloaded incomplete")
        data[ident] = {"version": e["version"], "file": name, "size": dmg["size_bytes"], "date": e["published_at"][:10]}
        changed.append(name)
    (out / "latest.json").write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print("\n".join(changed))


if __name__ == "__main__":
    main()
