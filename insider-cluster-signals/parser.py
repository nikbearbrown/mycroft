"""Purpose: Parse raw Form 4 ownershipDocument XML into normalized, validated trade records.
Input: data/raw/form4/*.xml (fetched by fetcher.py).
Output: data/verified/trades.json (records passing validation) + data/raw/parse-rejects.json (rejects, with reasons).
Side effects: Local file writes only; no network.
Idempotent: Yes; deterministic re-parse of the same raw files yields the same records.
Recipe: recipes/insider-cluster-signal-agent.md

This file IS the raw->verified gate (P2): nothing reaches data/verified/ without passing
every validation rule below, and every reject is recorded with its reason (P3).
"""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

# SEC Form 4 transaction codes (17 CFR 240.16a; EDGAR Form 4 instructions).
# P = open-market purchase, S = open-market sale -- the two codes that carry signal.
VALID_TRANSACTION_CODES = set("PSAFDGVJKCEHIMOUWXLZ")

# Issuers without a listed symbol file placeholder strings; downstream enrichment
# needs a priceable symbol, so these are rejected at the gate (found live 2026-07-13,
# see logs/RUN_LOG.md).
TICKER_PLACEHOLDERS = {"NONE", "N/A", "NA"}
TICKER_PATTERN = re.compile(r"^[A-Z][A-Z0-9.\-]{0,9}$")


def _text(element: ET.Element | None, path: str) -> str:
    """Extract nested element text, tolerating the <value> wrapper Form 4 uses."""
    if element is None:
        return ""
    node = element.find(path)
    if node is None:
        return ""
    value = node.find("value")
    return ((value.text if value is not None else node.text) or "").strip()


def parse_form4(xml_path: Path) -> list[dict]:
    """Parse one ownershipDocument XML into zero or more flat trade records."""
    root = ET.fromstring(xml_path.read_text(encoding="utf-8", errors="replace"))
    issuer = root.find("issuer")
    owner = root.find("reportingOwner")
    relationship = owner.find("reportingOwnerRelationship") if owner is not None else None

    base = {
        "accession": xml_path.stem,
        "period_of_report": (root.findtext("periodOfReport") or "").strip(),
        "issuer_cik": _text(issuer, "issuerCik"),
        "issuer_name": _text(issuer, "issuerName"),
        "ticker": _text(issuer, "issuerTradingSymbol").upper(),
        "owner_cik": _text(owner, "reportingOwnerId/rptOwnerCik"),
        "owner_name": _text(owner, "reportingOwnerId/rptOwnerName"),
        "is_director": _text(relationship, "isDirector") in ("1", "true"),
        "is_officer": _text(relationship, "isOfficer") in ("1", "true"),
        "is_ten_percent_owner": _text(relationship, "isTenPercentOwner") in ("1", "true"),
        "officer_title": _text(relationship, "officerTitle"),
    }

    records = []
    table = root.find("nonDerivativeTable")
    for txn in table.findall("nonDerivativeTransaction") if table is not None else []:
        records.append(
            {
                **base,
                "security_title": _text(txn, "securityTitle"),
                "transaction_date": _text(txn, "transactionDate"),
                "transaction_code": _text(txn, "transactionCoding/transactionCode"),
                "shares": _text(txn, "transactionAmounts/transactionShares"),
                "price_per_share": _text(txn, "transactionAmounts/transactionPricePerShare"),
                "acquired_disposed": _text(txn, "transactionAmounts/transactionAcquiredDisposedCode"),
                "shares_owned_after": _text(txn, "postTransactionAmounts/sharesOwnedFollowingTransaction"),
            }
        )
    return records


def validate(record: dict) -> list[str]:
    """Return the list of validation failures for a record (empty = passes the gate)."""
    failures = []
    if not record["ticker"]:
        failures.append("missing ticker")
    elif record["ticker"] in TICKER_PLACEHOLDERS:
        failures.append(f"placeholder ticker {record['ticker']!r} (issuer has no listed symbol)")
    elif not TICKER_PATTERN.match(record["ticker"]):
        failures.append(f"ticker {record['ticker']!r} not a plausible exchange symbol")
    if not record["owner_name"]:
        failures.append("missing owner name")
    if record["transaction_code"] not in VALID_TRANSACTION_CODES:
        failures.append(f"unknown transaction code {record['transaction_code']!r}")
    if record["acquired_disposed"] not in ("A", "D"):
        failures.append(f"acquired/disposed not A or D: {record['acquired_disposed']!r}")
    try:
        datetime.strptime(record["transaction_date"], "%Y-%m-%d")
    except ValueError:
        failures.append(f"unparseable transaction date {record['transaction_date']!r}")
    for numeric_field in ("shares", "price_per_share"):
        try:
            if float(record[numeric_field] or 0) < 0:
                failures.append(f"negative {numeric_field}")
        except ValueError:
            failures.append(f"non-numeric {numeric_field}: {record[numeric_field]!r}")
    return failures


def run(raw_dir: Path, verified_dir: Path) -> dict:
    xml_files = sorted((raw_dir / "form4").glob("*.xml"))
    verified_records, rejects, parse_errors = [], [], []

    for xml_path in xml_files:
        try:
            candidates = parse_form4(xml_path)
        except ET.ParseError as exc:
            parse_errors.append({"file": xml_path.name, "error": str(exc)})
            continue
        for record in candidates:
            failures = validate(record)
            if failures:
                rejects.append({**record, "reject_reasons": failures})
            else:
                record["shares"] = float(record["shares"] or 0)
                record["price_per_share"] = float(record["price_per_share"] or 0)
                verified_records.append(record)

    verified_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "parsed_at": datetime.now(timezone.utc).isoformat(),
        "xml_files_seen": len(xml_files),
        "records_extracted": len(verified_records) + len(rejects),
        "records_verified": len(verified_records),
        "records_rejected": len(rejects),
        "files_unparseable": len(parse_errors),
    }
    (verified_dir / "trades.json").write_text(
        json.dumps({"summary": summary, "records": verified_records}, indent=2) + "\n"
    )
    (raw_dir / "parse-rejects.json").write_text(
        json.dumps({"rejects": rejects, "parse_errors": parse_errors}, indent=2) + "\n"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse and validate raw Form 4 XML into verified trade records.")
    module_dir = Path(__file__).parent
    parser.add_argument("--raw-dir", default=str(module_dir / "data" / "raw"))
    parser.add_argument("--verified-dir", default=str(module_dir / "data" / "verified"))
    args = parser.parse_args()
    print(json.dumps(run(Path(args.raw_dir), Path(args.verified_dir)), indent=2))


if __name__ == "__main__":
    main()
