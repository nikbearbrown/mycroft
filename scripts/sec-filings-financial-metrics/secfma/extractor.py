"""Extract canonical metrics from an EDGAR companyfacts payload.

Each extracted value carries full provenance so it can be traced back to the
exact filing and XBRL tag it came from. Nothing here interprets the numbers;
that is validation's job (see validation.py).
"""
from __future__ import annotations

from typing import Any

from .concept_map import CANONICAL_METRICS, MetricSpec

US_GAAP = "us-gaap"


def _source_url(cik10: str, accn: str) -> str:
    """Build the EDGAR filing-index URL for an accession number."""
    if not accn:
        return ""
    folder = accn.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik10)}/{folder}/{accn}-index.htm"


def _resolve_tag(facts: dict[str, Any], spec: MetricSpec) -> tuple[str, dict] | None:
    """Return (matched_tag, tag_block) for the first candidate present in us-gaap."""
    usgaap = facts.get("facts", {}).get(US_GAAP, {})
    for tag in spec.candidates:
        if tag in usgaap:
            return tag, usgaap[tag]
    return None


def extract_metrics(
    company_facts: dict[str, Any],
    cik10: str,
    forms: tuple[str, ...],
) -> list[dict[str, Any]]:
    """Return one record per (metric, period) with provenance, plus MISSING rows."""
    records: list[dict[str, Any]] = []
    entity = company_facts.get("entityName")

    for spec in CANONICAL_METRICS:
        resolved = _resolve_tag(company_facts, spec)
        if resolved is None:
            records.append({
                "metric": spec.name,
                "status": "MISSING",
                "note": (
                    f"No us-gaap tag among {spec.candidates} found; "
                    "the company may use a custom XBRL extension (needs mapping)."
                ),
            })
            continue

        matched_tag, block = resolved
        unit_entries = block.get("units", {}).get(spec.unit, [])
        for entry in unit_entries:
            if entry.get("form") not in forms:
                continue
            records.append({
                "metric": spec.name,
                "status": "OK",
                "value": entry.get("val"),
                "unit": spec.unit,
                "us_gaap_tag": matched_tag,
                "period_type": spec.period_type,
                "period_start": entry.get("start"),  # None for instant metrics
                "period_end": entry.get("end"),
                "fiscal_year": entry.get("fy"),
                "fiscal_period": entry.get("fp"),
                "form": entry.get("form"),
                "accession": entry.get("accn"),
                "filed": entry.get("filed"),
                "frame": entry.get("frame"),
                "entity": entity,
                "source_url": _source_url(cik10, entry.get("accn", "")),
            })
    return records
