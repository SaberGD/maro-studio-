#!/usr/bin/env python3
"""The HORIX Launcher's release feed: release_info.json, in the format craft-launcher reads
(crates/core/src/feed.rs), built from the GitHub releases of SaberGD/maro-studio-.

    GITHUB_TOKEN=... python3 -I apps/horix-launcher/feed/make_feed.py out/release_info.json

Every app releases from the one repository, told apart by tag prefix (`horix-v0.2.57`,
`horix-vectors-v0.11.3`, `horix-light-v0.8.2`, `horix-launcher-v0.4.1`); each gets the newest
published, non-prerelease release with its prefix. The launcher trusts an entry for 24 hours, so
CI rebuilds the file after every release and on a schedule. Announcements and alerts for the
launcher's users come from notices.json next to this script.
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = "SaberGD/maro-studio-"
# id -> (name, tag prefix); ids and names as in rebrand.py's catalog.
APPS = {
    "horix": ("HORIX", "horix-v"),
    "horix-vectors": ("Horix Vectors", "horix-vectors-v"),
    "horix-light": ("Horix Light", "horix-light-v"),
    "horix-one": ("HORIX One", "horix-one-v"),
    "horix-launcher": ("HORIX Launcher", "horix-launcher-v"),
}


def releases() -> list[dict]:
    out, page = [], 1
    while page <= 10:
        req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/releases?per_page=100&page={page}",
                                     headers={"Accept": "application/vnd.github+json", "User-Agent": "horix-feed"})
        if os.environ.get("GITHUB_TOKEN"):
            req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
        with urllib.request.urlopen(req, timeout=60) as r:
            batch = json.load(r)
        out += batch
        if len(batch) < 100:
            break
        page += 1
    return out


def version_key(tag: str, prefix: str) -> tuple:
    parts = tag[len(prefix):].split("-")[0].split(".")
    return tuple(int(p) if p.isdigit() else -1 for p in parts)


def entry(name: str, prefix: str, rels: list[dict], now: str) -> dict:
    mine = [r for r in rels if r["tag_name"].startswith(prefix) and not r["draft"] and not r["prerelease"]
            and r["tag_name"][len(prefix):][:1].isdigit()]
    latest = max(mine, key=lambda r: version_key(r["tag_name"], prefix), default=None)
    e = {"name": name, "repo": f"{REPO}#{prefix}", "app_last_fetched": now, "latest_release": None}
    if latest:
        e["latest_release"] = {
            "tag": latest["tag_name"],
            "version": latest["tag_name"][len(prefix):],
            "name": latest["name"] or latest["tag_name"],
            "published_at": latest["published_at"],
            "html_url": latest["html_url"],
            "prerelease": False,
            "notes_markdown": (latest.get("body") or "")[:60000],
            "assets": [{
                "name": a["name"],
                "size_bytes": a["size"],
                "download_url": a["browser_download_url"],
                "sha256": (a.get("digest") or "").removeprefix("sha256:") or None,
            } for a in latest["assets"]],
        }
    return e


def main() -> None:
    out = Path(sys.argv[1])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rels = releases()
    notices = json.loads((HERE / "notices.json").read_text(encoding="utf-8"))
    feed = {
        "success": True,
        "release_info": {"apps": {i: entry(n, p, rels, now) for i, (n, p) in APPS.items()}, "last_fetched": now},
        "app_renames": [],
        "repo_renames": [],
        "important_notices": notices,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(feed, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for i, e in feed["release_info"]["apps"].items():
        r = e["latest_release"]
        print(f"{i}: {r['tag'] + ' (' + str(len(r['assets'])) + ' files)' if r else 'no release yet'}")


if __name__ == "__main__":
    main()
