"""Purpose: Fetch SEC Form 4 insider-trade filings from EDGAR (daily form index -> filing XML).
Input: --date YYYY-MM-DD (filing date), --limit N (sample cap), --output-dir (default data/raw).
Output: Raw ownershipDocument XML files in data/raw/form4/ + a fetch manifest JSON with provenance.
Side effects: HTTP GETs against sec.gov (rate-limited <10 req/s per SEC fair-access policy).
Idempotent: Yes; re-fetching the same date overwrites identical content, manifest records each run.
Recipe: recipes/insider-cluster-signal-agent.md

This is the ONLY file in insider-cluster-signals/ that touches the network (P2).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# SEC fair-access policy requires a declared User-Agent with contact info.
USER_AGENT = "Mycroft insider-cluster-signals research baskar.sa@northeastern.edu"
RATE_LIMIT_SECONDS = 0.15  # ~6.6 req/s, under the 10 req/s SEC ceiling
EDGAR_BASE = "https://www.sec.gov/Archives"


def _get(url: str, timeout: int = 30) -> bytes:
    """One rate-limited HTTP GET with the SEC-required User-Agent."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = response.read()
    time.sleep(RATE_LIMIT_SECONDS)
    return data


def quarter_of(date: datetime) -> int:
    return (date.month - 1) // 3 + 1


def fetch_daily_form_index(date: datetime) -> list[dict[str, str]]:
    """Fetch EDGAR's daily form index and return the Form 4 entries.

    Index line format (fixed columns, header ends at the '---' rule):
      Form Type | Company Name | CIK | Date Filed | File Name
    """
    url = (
        f"{EDGAR_BASE}/edgar/daily-index/{date.year}/QTR{quarter_of(date)}/"
        f"form.{date.strftime('%Y%m%d')}.idx"
    )
    text = _get(url).decode("latin-1")
    entries: list[dict[str, str]] = []
    past_header = False
    for line in text.splitlines():
        if line.startswith("---"):
            past_header = True
            continue
        if not past_header or not line.strip():
            continue
        # Form type is the first whitespace-delimited token; "4" must match exactly
        # (not 4/A amendments, not 424B..., not 4-something).
        parts = line.split()
        if parts and parts[0] == "4":
            file_name = parts[-1]                     # edgar/data/CIK/accession.txt
            date_filed = parts[-2]
            cik = parts[-3]
            company = " ".join(parts[1:-3])
            entries.append(
                {"cik": cik, "company": company, "date_filed": date_filed, "file_name": file_name}
            )
    return entries


def filing_xml_url(file_name: str) -> str | None:
    """Resolve a daily-index file name to the filing's ownershipDocument XML URL.

    edgar/data/1234567/0001234567-26-000123.txt
      -> directory edgar/data/1234567/000123456726000123/
      -> index.json lists directory contents; pick the ownership XML.
    """
    accession = file_name.rsplit("/", 1)[-1].removesuffix(".txt")
    directory = f"{file_name.rsplit('/', 1)[0]}/{accession.replace('-', '')}"
    index_url = f"{EDGAR_BASE}/{directory}/index.json"
    try:
        listing = json.loads(_get(index_url))
    except Exception:
        return None
    xml_names = [
        item["name"]
        for item in listing.get("directory", {}).get("item", [])
        if item["name"].endswith(".xml") and not item["name"].endswith("_htm.xml")
    ]
    if not xml_names:
        return None
    # Form 4 primary document is conventionally the only bare .xml in the directory.
    return f"{EDGAR_BASE}/{directory}/{xml_names[0]}"


def dedupe_by_accession(entries: list[dict]) -> list[dict]:
    """Collapse duplicate index lines to one entry per accession.

    The daily form index repeats a filing once per joint filer — on 2026-03-02, 2,973
    lines were only 1,460 unique accessions (see logs/RUN_LOG.md). One fetch per
    accession halves request volume; first-seen entry wins (all carry the same file)."""
    seen: set[str] = set()
    unique = []
    for entry in entries:
        accession = entry["file_name"].rsplit("/", 1)[-1].removesuffix(".txt")
        if accession not in seen:
            seen.add(accession)
            unique.append(entry)
    return unique


def fetch_form4_filings(date: datetime, limit: int, output_dir: Path) -> dict:
    """Fetch up to `limit` Form 4 XMLs filed on `date` into output_dir/form4/."""
    form4_dir = output_dir / "form4"
    form4_dir.mkdir(parents=True, exist_ok=True)

    index_entries = fetch_daily_form_index(date)
    entries = dedupe_by_accession(index_entries)
    manifest = {
        "source": "SEC EDGAR daily form index",
        "index_date": date.strftime("%Y-%m-%d"),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "user_agent": USER_AGENT,
        "form4_index_lines": len(index_entries),
        "form4_filings_in_index": len(entries),
        "limit_applied": limit,
        "fetched": [],
        "errors": [],
    }

    for entry in entries[:limit]:
        try:
            xml_url = filing_xml_url(entry["file_name"])
            if xml_url is None:
                manifest["errors"].append({**entry, "error": "no ownership XML found in filing dir"})
                continue
            xml_bytes = _get(xml_url)
            accession = entry["file_name"].rsplit("/", 1)[-1].removesuffix(".txt")
            out_path = form4_dir / f"{accession}.xml"
            out_path.write_bytes(xml_bytes)
            manifest["fetched"].append(
                {
                    **entry,
                    "xml_url": xml_url,
                    "saved_to": str(out_path).replace("\\", "/"),
                    "sha256": hashlib.sha256(xml_bytes).hexdigest(),
                    "bytes": len(xml_bytes),
                }
            )
        except Exception as exc:  # record, don't halt: partial fetches are still evidence
            manifest["errors"].append({**entry, "error": f"{type(exc).__name__}: {exc}"})

    manifest_path = output_dir / f"fetch-manifest-{date.strftime('%Y%m%d')}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch SEC Form 4 filings for one filing date.")
    parser.add_argument("--date", required=True, help="Filing date, YYYY-MM-DD (a business day).")
    parser.add_argument("--limit", type=int, default=25, help="Max filings to fetch (sample mode default 25).")
    parser.add_argument("--output-dir", default=str(Path(__file__).parent / "data" / "raw"))
    args = parser.parse_args()

    date = datetime.strptime(args.date, "%Y-%m-%d")
    manifest = fetch_form4_filings(date, args.limit, Path(args.output_dir))
    print(
        json.dumps(
            {
                "index_date": manifest["index_date"],
                "form4_filings_in_index": manifest["form4_filings_in_index"],
                "fetched": len(manifest["fetched"]),
                "errors": len(manifest["errors"]),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
