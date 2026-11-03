"""
ingest.py — INGEST stage of the insider-signal-agent recipe.

Downloads SEC's Insider Transactions Data Sets (quarterly Form 3/4/5 ZIPs) into
data/raw/form345/, following SEC's fair-access rules, and records provenance.

What it guarantees (recipe: "1. INGEST", "SEC fair-access rules", gate G1)
    - Refuses to run without SEC_USER_AGENT: a name plus a contact email, the form SEC asks
      for ("Sample Company Name AdminContact@<sample company domain>.com").
    - At most `--rate` requests per second (default 1). Any rate >= SEC's 10/s is refused.
    - Download URLs are read from SEC's data-set page, never assembled from a pattern:
      SEC hosts recent quarters under different folders.
    - manifest.json records per quarter: source_url, retrieved_at, sha256, bytes,
      http_status, user_agent_set. The User-Agent value itself is not stored, because it
      holds a personal email address.
    - request_log.jsonl gets one line per HTTP request: ts, url, status, elapsed_ms.
    - Checkpoint/resume: a quarter whose ZIP exists and matches its manifest hash is
      skipped without any request. A download goes to a .part file, is checked (length
      and zip structure), and only then renamed into place. An interrupted or invalid
      download is discarded, never half-kept.
    - 403 / 429 / 5xx: back off (10 s, then 20 s), then HALT. No tight retry loops.
    - Each ZIP is extracted to data/raw/form345/<YYYY>q<N>/. Members with absolute or
      parent-relative paths are refused.

Network: only this script (and the G2 spot-check) touches SEC (P2). Standard library only.

Usage
    export SEC_USER_AGENT="Your Name your-email@example.org"
    python ingest.py --quarters 2023q1:2026q3     # download / resume
    python ingest.py --quarters 2026q3            # one quarter
    python ingest.py --quarters 2026q3 --verify   # G1 check, no network

Exit codes: 0 ok · 1 ingest or verify failure · 2 configuration refused · 3 halted by SEC responses
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import zipfile
import zlib
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable, Iterator, Mapping
from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

DATASET_PAGE_URL = (
    "https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets"
)
SEC_MAX_RATE = 10.0          # SEC: "Current max request rate: 10 requests/second."
DEFAULT_RATE = 1.0
RETRY_STATUSES = frozenset({403, 429, 500, 502, 503, 504})
MAX_RETRIES = 2
BACKOFF_SECONDS = 10.0
TIMEOUT_SECONDS = 120
CHUNK_BYTES = 1 << 16
RATE_TOLERANCE_S = 0.05      # allowed clock jitter when G1 checks request spacing

ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = ROOT / "data" / "raw" / "form345"
MANIFEST_NAME = "manifest.json"
REQUEST_LOG_NAME = "request_log.jsonl"
EXTRACT_MARKER = "_EXTRACTED_FROM.json"

_EMAIL_RE = re.compile(r"[^@\s<>]+@[^@\s<>]+\.[A-Za-z]{2,}")
_QUARTER_RE = re.compile(r"^(\d{4})q([1-4])$")
_ZIP_HREF_RE = re.compile(r"(\d{4})q([1-4])_form345\.zip$", re.IGNORECASE)


# --------------------------------------------------------------------------- errors

class IngestError(Exception):
    """Ingest or verify failed (exit 1)."""
    exit_code = 1


class ConfigError(IngestError):
    """Configuration refused before any request was made (exit 2)."""
    exit_code = 2


class HaltError(IngestError):
    """SEC kept refusing or failing; stop and hand to the human (exit 3)."""
    exit_code = 3


# --------------------------------------------------------------------------- config

def require_user_agent(env: Mapping[str, str]) -> str:
    """Return SEC_USER_AGENT, or refuse if it is missing or has no contact email."""
    ua = (env.get("SEC_USER_AGENT") or "").strip()
    if not ua:
        raise ConfigError(
            "SEC_USER_AGENT is not set. SEC requires a User-Agent with a name and contact "
            'email, e.g. export SEC_USER_AGENT="Your Name your-email@example.org"'
        )
    email = _EMAIL_RE.search(ua)
    if not email:
        raise ConfigError("SEC_USER_AGENT must include a contact email address.")
    if not (ua[: email.start()] + ua[email.end():]).strip():
        raise ConfigError("SEC_USER_AGENT must include a name as well as an email address.")
    return ua


def check_rate(rate: float) -> float:
    if not rate > 0:
        raise ConfigError(f"--rate must be positive (got {rate}).")
    if rate >= SEC_MAX_RATE:
        raise ConfigError(
            f"--rate {rate} refused: SEC's maximum is {SEC_MAX_RATE:g} requests/second; "
            "this pipeline stays below it."
        )
    return float(rate)


def _quarter_key(q: str) -> tuple[int, int]:
    m = _QUARTER_RE.match(q)
    if not m:
        raise ConfigError(f"Bad quarter {q!r}: expected YYYYqN, e.g. 2026q3.")
    return int(m.group(1)), int(m.group(2))


def parse_quarters(spec: str) -> list[str]:
    """'2026q3' | '2025q4,2026q3' | '2023q1:2026q3' (inclusive) → sorted unique quarters."""
    out: set[str] = set()
    for part in (p.strip().lower() for p in spec.split(",")):
        if not part:
            continue
        if ":" in part:
            lo, hi = (s.strip() for s in part.split(":", 1))
            (y, q), end = _quarter_key(lo), _quarter_key(hi)
            if (y, q) > end:
                raise ConfigError(f"Quarter range {part!r} runs backwards.")
            while (y, q) <= end:
                out.add(f"{y}q{q}")
                y, q = (y + 1, 1) if q == 4 else (y, q + 1)
        else:
            _quarter_key(part)
            out.add(part)
    if not out:
        raise ConfigError("No quarters given.")
    return sorted(out, key=_quarter_key)


# --------------------------------------------------------------------------- page parsing

class _HrefCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            for name, value in attrs:
                if name.lower() == "href" and value:
                    self.hrefs.append(value.strip())


def parse_dataset_page(html: str, base_url: str = DATASET_PAGE_URL) -> dict[str, str]:
    """Map quarter → absolute ZIP URL, from the links on SEC's data-set page."""
    collector = _HrefCollector()
    collector.feed(html)
    found: dict[str, str] = {}
    for href in collector.hrefs:
        m = _ZIP_HREF_RE.search(href.split("?", 1)[0])
        if m:
            found.setdefault(f"{m.group(1)}q{m.group(2)}", urljoin(base_url, href))
    return found


# --------------------------------------------------------------------------- HTTP

Opener = Callable[[str, Mapping[str, str], float], object]


def _default_open(url: str, headers: Mapping[str, str], timeout: float):
    try:
        return urlopen(Request(url, headers=dict(headers)), timeout=timeout)
    except HTTPError as err:          # an HTTPError is itself a response; keep its status
        return err


def _status(resp) -> int:
    return int(getattr(resp, "status", None) or getattr(resp, "code", 0) or 0)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class SecClient:
    """Rate-limited, logged GET client. Every request passes through `get`."""

    def __init__(
        self,
        user_agent: str,
        rate: float,
        log_path: Path,
        opener: Opener = _default_open,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ) -> None:
        self.interval = 1.0 / check_rate(rate)
        self.headers = {"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"}
        self.log_path = log_path
        self._open, self._clock, self._sleep, self._now = opener, clock, sleep, now
        self._last_start: float | None = None
        self.requests_made = 0

    def _wait_turn(self) -> None:
        if self._last_start is not None:
            gap = self._clock() - self._last_start
            if gap < self.interval:
                self._sleep(self.interval - gap)
        self._last_start = self._clock()

    def _log(self, record: dict) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")

    def get(self, url: str):
        """Return a 200 response (caller must close it), or raise HaltError."""
        for attempt in range(MAX_RETRIES + 1):
            self._wait_turn()
            started_at, t0 = self._now(), self._clock()
            try:
                resp = self._open(url, self.headers, TIMEOUT_SECONDS)
            except OSError as err:   # DNS, refused connection, timeout
                self._log({"ts": _iso(started_at), "url": url, "status": None,
                           "elapsed_ms": round((self._clock() - t0) * 1000), "error": str(err)})
                raise HaltError(f"Network error fetching {url}: {err}") from err
            self.requests_made += 1
            status = _status(resp)
            self._log({"ts": _iso(started_at), "url": url, "status": status,
                       "elapsed_ms": round((self._clock() - t0) * 1000)})
            if status == 200:
                return resp
            _close(resp)
            if status in RETRY_STATUSES and attempt < MAX_RETRIES:
                self._sleep(BACKOFF_SECONDS * (2 ** attempt))
                continue
            raise HaltError(
                f"SEC returned HTTP {status} for {url} after {attempt + 1} attempt(s). "
                "Stopping. Check SEC_USER_AGENT and the request rate; do not retry in a loop."
            )
        raise AssertionError("unreachable")


def _close(resp) -> None:
    close = getattr(resp, "close", None)
    if callable(close):
        close()


def iter_body(resp) -> Iterator[bytes]:
    """Yield the decoded body in chunks, undoing gzip/deflate content-encoding."""
    encoding = (resp.headers.get("Content-Encoding") or "").strip().lower()
    decomp = zlib.decompressobj(zlib.MAX_WBITS | 32) if encoding in ("gzip", "deflate") else None
    while True:
        chunk = resp.read(CHUNK_BYTES)
        if not chunk:
            break
        yield decomp.decompress(chunk) if decomp else chunk
    if decomp:
        tail = decomp.flush()
        if tail:
            yield tail


# --------------------------------------------------------------------------- files

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_manifest(data_dir: Path) -> dict:
    path = data_dir / MANIFEST_NAME
    if not path.exists():
        return {"source_page": DATASET_PAGE_URL, "quarters": {}}
    with open(path, encoding="utf-8") as fh:
        manifest = json.load(fh)
    manifest.setdefault("quarters", {})
    return manifest


def save_manifest(data_dir: Path, manifest: dict) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    tmp = data_dir / (MANIFEST_NAME + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, data_dir / MANIFEST_NAME)


def zip_path(data_dir: Path, quarter: str) -> Path:
    return data_dir / f"{quarter}_form345.zip"


def is_complete(data_dir: Path, manifest: dict, quarter: str) -> bool:
    entry = manifest["quarters"].get(quarter)
    path = zip_path(data_dir, quarter)
    return bool(entry) and path.exists() and sha256_file(path) == entry.get("sha256")


def download_quarter(client: SecClient, quarter: str, url: str, data_dir: Path,
                     now: Callable[[], datetime] | None = None) -> dict:
    data_dir.mkdir(parents=True, exist_ok=True)
    dest = zip_path(data_dir, quarter)
    part = dest.with_name(dest.name + ".part")
    retrieved_at = _iso((now or client._now)())
    resp = client.get(url)
    digest, size = hashlib.sha256(), 0
    try:
        expected = resp.headers.get("Content-Length")
        encoded = (resp.headers.get("Content-Encoding") or "").strip().lower()
        with open(part, "wb") as fh:
            for chunk in iter_body(resp):
                fh.write(chunk)
                digest.update(chunk)
                size += len(chunk)
        if expected and not encoded and int(expected) != size:
            raise IngestError(f"{quarter}: incomplete download ({size} of {expected} bytes).")
        if not zipfile.is_zipfile(part):
            raise IngestError(f"{quarter}: downloaded file is not a valid ZIP.")
    except BaseException:
        part.unlink(missing_ok=True)       # discard the partial download, never half-keep it
        raise
    finally:
        _close(resp)
    os.replace(part, dest)
    return {
        "quarter": quarter,
        "source_url": url,
        "retrieved_at": retrieved_at,
        "sha256": digest.hexdigest(),
        "bytes": size,
        "http_status": 200,
        "user_agent_set": True,
    }


def _safe_member(name: str) -> bool:
    p = PurePosixPath(name.replace("\\", "/"))
    return bool(name) and not p.is_absolute() and ".." not in p.parts and ":" not in p.parts[0]


def extract_quarter(data_dir: Path, quarter: str, sha256: str) -> Path:
    """Extract the quarter's ZIP into data_dir/<quarter>/ (idempotent per ZIP hash)."""
    out = data_dir / quarter
    marker = out / EXTRACT_MARKER
    if marker.exists():
        try:
            if json.loads(marker.read_text(encoding="utf-8")).get("sha256") == sha256:
                return out
        except json.JSONDecodeError:
            pass
    with zipfile.ZipFile(zip_path(data_dir, quarter)) as zf:
        names = zf.namelist()
        bad = [n for n in names if not _safe_member(n)]
        if bad:
            raise IngestError(f"{quarter}: refusing unsafe ZIP member path(s): {bad}")
        out.mkdir(parents=True, exist_ok=True)
        zf.extractall(out)
    marker.write_text(json.dumps({"sha256": sha256, "members": names}, indent=2) + "\n",
                      encoding="utf-8")
    return out


# --------------------------------------------------------------------------- run / verify

def run(quarters: Iterable[str], data_dir: Path, client: SecClient) -> dict:
    """Download what is missing, skip what is complete, extract everything requested."""
    quarters = list(quarters)
    manifest = load_manifest(data_dir)
    skipped = [q for q in quarters if is_complete(data_dir, manifest, q)]
    todo = [q for q in quarters if q not in skipped]
    downloaded: list[str] = []
    if todo:
        resp = client.get(DATASET_PAGE_URL)
        try:
            html = b"".join(iter_body(resp)).decode("utf-8", errors="replace")
        finally:
            _close(resp)
        links = parse_dataset_page(html)
        missing = [q for q in todo if q not in links]
        if missing:
            latest = max(links, key=_quarter_key) if links else "none found"
            raise IngestError(
                f"Not listed on SEC's data-set page: {', '.join(missing)} (latest listed: {latest})."
            )
        for q in todo:
            manifest["quarters"][q] = download_quarter(client, q, links[q], data_dir)
            save_manifest(data_dir, manifest)          # checkpoint after every quarter
            downloaded.append(q)
    for q in quarters:
        extract_quarter(data_dir, q, manifest["quarters"][q]["sha256"])
    return {"downloaded": downloaded, "skipped": skipped, "requests": client.requests_made}


def _read_log(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def verify(quarters: Iterable[str], data_dir: Path, rate: float = DEFAULT_RATE) -> list[str]:
    """G1: return a list of problems; an empty list means every check passed."""
    interval = 1.0 / check_rate(rate)
    problems: list[str] = []
    manifest = load_manifest(data_dir)
    log = _read_log(data_dir / REQUEST_LOG_NAME)
    required = ("quarter", "source_url", "retrieved_at", "sha256", "bytes", "http_status",
                "user_agent_set")
    for q in quarters:
        entry = manifest["quarters"].get(q)
        path = zip_path(data_dir, q)
        if not entry:
            problems.append(f"{q}: no manifest entry")
            continue
        missing = [k for k in required if k not in entry]
        if missing:
            problems.append(f"{q}: manifest entry missing {missing}")
        if entry.get("user_agent_set") is not True:
            problems.append(f"{q}: manifest does not record a User-Agent")
        if not path.exists():
            problems.append(f"{q}: ZIP missing at {path.name}")
        elif sha256_file(path) != entry.get("sha256"):
            problems.append(f"{q}: SHA-256 of {path.name} does not match the manifest")
        if not any(r.get("url") == entry.get("source_url") and r.get("status") == 200 for r in log):
            problems.append(f"{q}: no logged 200 response for {entry.get('source_url')}")
    starts = sorted(_parse_ts(r["ts"]) for r in log)
    for a, b in zip(starts, starts[1:]):
        gap = (b - a).total_seconds()
        if gap < interval - RATE_TOLERANCE_S:
            problems.append(f"request spacing {gap:.3f}s at {_iso(b)} is below {interval:.3f}s")
    last_status: dict[str, object] = {}
    for r in log:
        last_status[r.get("url")] = r.get("status")
    for url, status in last_status.items():
        if status != 200:
            problems.append(f"unhandled HTTP {status} for {url} (last logged response)")
    return problems


# --------------------------------------------------------------------------- CLI

def main(argv: list[str] | None = None, env: Mapping[str, str] = os.environ) -> int:
    ap = argparse.ArgumentParser(description="INGEST: SEC Insider Transactions Data Sets.")
    ap.add_argument("--quarters", required=True, help="e.g. 2026q3, 2025q4,2026q3, 2023q1:2026q3")
    ap.add_argument("--rate", type=float, default=DEFAULT_RATE,
                    help=f"max requests/second (default {DEFAULT_RATE:g}; must be < {SEC_MAX_RATE:g})")
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    ap.add_argument("--verify", action="store_true", help="G1 check only; makes no requests")
    args = ap.parse_args(argv)
    try:
        quarters = parse_quarters(args.quarters)
        check_rate(args.rate)
        if args.verify:
            problems = verify(quarters, args.data_dir, args.rate)
            for p in problems:
                print(f"FAIL  {p}")
            print(f"G1 verify: {len(quarters)} quarter(s), "
                  f"{'PASS' if not problems else f'{len(problems)} problem(s)'}")
            return 0 if not problems else 1
        client = SecClient(require_user_agent(env), args.rate, args.data_dir / REQUEST_LOG_NAME)
        result = run(quarters, args.data_dir, client)
        print(f"ingest: downloaded {result['downloaded'] or '-'} · skipped (hash matched) "
              f"{result['skipped'] or '-'} · {result['requests']} request(s) to SEC")
        return 0
    except IngestError as err:
        print(f"ingest: {err}", file=sys.stderr)
        return err.exit_code


if __name__ == "__main__":
    sys.exit(main())
