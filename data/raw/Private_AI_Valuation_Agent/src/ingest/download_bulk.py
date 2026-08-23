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


def verify_zip(path: Path) -> None:
    """Read the archive's central directory. Raises BadZipFile if truncated.

    Cheap -- it seeks to the end rather than decompressing 1.5 GB -- but it is
    the check that catches the failure mode resuming actually has: a file that
    is the right size on disk and structurally incomplete.
    """
    with zipfile.ZipFile(path) as zf:
        if not zf.namelist():
            raise zipfile.BadZipFile("archive contains no members")


def _fetch(url: str, partial: Path, have: int) -> int:
    """One attempt. Returns bytes on disk afterwards.

    Guards the resume path: a server may ignore `Range` and answer 200 with the
    whole body. Appending that onto existing bytes yields a corrupt archive that
    still looks complete, so a non-206 answer restarts the file instead.
    """
    headers = {"User-Agent": user_agent()}
    if have:
        headers["Range"] = f"bytes={have}-"

    throttle()
    with requests.get(url, headers=headers, stream=True, timeout=120) as r:
        r.raise_for_status()

        if have and r.status_code != 206:
            print(f"\n  server ignored Range (HTTP {r.status_code}) -- restarting file")
            have = 0
        mode = "ab" if have else "wb"
        total = int(r.headers.get("Content-Length", 0)) + have

        done = have
        with open(partial, mode) as fh:
            for chunk in r.iter_content(chunk_size=1 << 20):
                fh.write(chunk)
                done += len(chunk)
                if total:
                    print(f"\r  {done/1e6:7.1f} / {total/1e6:.1f} MB  "
                          f"({done/total*100:5.1f}%)", end="", flush=True)
        print()

    if total and done != total:
        raise IOError(f"short read: {done} of {total} bytes")
    return done


def download(quarter: str, attempts: int = 4) -> Path:
    """Fetch {quarter}_nport.zip, resuming and retrying on partial downloads.

    Retries are what make a 14-quarter run survivable: one transient reset
    partway through 5.9 GB should cost a few seconds, not the whole batch. Each
    retry resumes from what is already on disk rather than starting over.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    url = f"{BASE}/{quarter}_nport.zip"
    target = DATA_DIR / f"{quarter}_nport.zip"
    partial = target.with_suffix(".zip.part")

    if target.exists():
        print(f"{target.name} already present ({target.stat().st_size/1e6:.1f} MB) -- skipping")
        return target

    for attempt in range(1, attempts + 1):
        have = partial.stat().st_size if partial.exists() else 0
        if have:
            print(f"resuming at {have/1e6:.1f} MB")
        try:
            _fetch(url, partial, have)
            verify_zip(partial)
            break
        except requests.HTTPError as exc:
            # 4xx is the SEC telling us something true -- a quarter that is not
            # published yet does not become published by asking again.
            status = exc.response.status_code if exc.response is not None else None
            if status and 400 <= status < 500:
                raise
            failure = exc
        except (requests.RequestException, IOError, zipfile.BadZipFile) as exc:
            failure = exc

        if isinstance(failure, zipfile.BadZipFile):
            # Resuming onto a corrupt file just grows the corruption.
            print(f"  {quarter}: archive did not verify ({failure}) -- discarding partial")
            partial.unlink(missing_ok=True)

        if attempt == attempts:
            raise SystemExit(f"{quarter}: giving up after {attempts} attempts -- {failure}")
        backoff = 2 ** attempt
        print(f"  {quarter}: attempt {attempt} failed ({failure}); retrying in {backoff}s")
        time.sleep(backoff)

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
