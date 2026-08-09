"""Download a DERA bulk N-PORT data set for one calendar quarter.

The SEC requires a declared User-Agent carrying a real name and email; requests
without one return HTTP 403. Set EDGAR_NAME and EDGAR_EMAIL in .env.

Rate limited to 10 requests/second per SEC policy. Downloads stream to a
.part file and resume via HTTP Range, so an interrupted 440 MB transfer does
not start over.

    python -m src.ingest.download_bulk 2026q2
    python -m src.ingest.download_bulk 2026q2 --extract
"""

import argparse
import os
import sys
import time
import zipfile
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE = "https://www.sec.gov/files/dera/data/form-n-port-data-sets"
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
MIN_INTERVAL = 0.1  # 10 req/s ceiling

_last_request = 0.0


def user_agent() -> str:
    load_dotenv()
    name = os.getenv("EDGAR_NAME")
    email = os.getenv("EDGAR_EMAIL")
    if not name or not email:
        sys.exit(
            "EDGAR_NAME and EDGAR_EMAIL must be set in .env.\n"
            "The SEC returns HTTP 403 for requests without a declared User-Agent."
        )
    return f"{name} {email}"


def throttle() -> None:
    global _last_request
    elapsed = time.monotonic() - _last_request
    if elapsed < MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - elapsed)
    _last_request = time.monotonic()


def download(quarter: str) -> Path:
    """Fetch {quarter}_nport.zip, resuming a partial download if one exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    url = f"{BASE}/{quarter}_nport.zip"
    target = DATA_DIR / f"{quarter}_nport.zip"
    partial = target.with_suffix(".zip.part")

    if target.exists():
        print(f"{target.name} already present ({target.stat().st_size/1e6:.1f} MB) -- skipping")
        return target

    headers = {"User-Agent": user_agent()}
    have = partial.stat().st_size if partial.exists() else 0
    if have:
        headers["Range"] = f"bytes={have}-"
        print(f"resuming at {have/1e6:.1f} MB")

    throttle()
    with requests.get(url, headers=headers, stream=True, timeout=120) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0)) + have
        mode = "ab" if have else "wb"
        done = have
        with open(partial, mode) as fh:
            for chunk in r.iter_content(chunk_size=1 << 20):
                fh.write(chunk)
                done += len(chunk)
                if total:
                    pct = done / total * 100
                    print(f"\r  {done/1e6:7.1f} / {total/1e6:.1f} MB  ({pct:5.1f}%)",
                          end="", flush=True)
    print()

    partial.rename(target)
    print(f"saved {target} ({target.stat().st_size/1e6:.1f} MB)")
    return target


def extract(archive: Path) -> Path:
    """Unzip into data/<quarter>/ and list what arrived."""
    dest = archive.with_suffix("")
    dest.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        members = zf.namelist()
        zf.extractall(dest)

    print(f"\nextracted {len(members)} files to {dest}")
    rows = sorted(
        ((m, (dest / m).stat().st_size) for m in members),
        key=lambda t: -t[1],
    )
    for name, size in rows:
        print(f"  {size/1e6:9.1f} MB  {name}")
    return dest


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("quarter", help="e.g. 2026q2")
    ap.add_argument("--extract", action="store_true", help="unzip after download")
    args = ap.parse_args()

    archive = download(args.quarter)
    if args.extract:
        extract(archive)


if __name__ == "__main__":
    main()
