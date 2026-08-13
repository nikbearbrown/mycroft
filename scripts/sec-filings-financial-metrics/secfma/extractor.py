"""Extract canonical metrics from an EDGAR companyfacts payload.

Each extracted value carries full provenance so it can be traced back to the
exact filing and XBRL tag it came from. Nothing here interprets the numbers;
that is validation's job (see validation.py).

Resolution order for each metric: try the us-gaap candidate tags in priority
order; if none match, fall back to a human-curated custom-extension override
for this company (custom_extension_map.json). If neither resolves, the metric
is flagged MISSING — never guessed.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .concept_map import CANONICAL_METRICS, MetricSpec

US_GAAP = "us-gaap"
_OVERRIDES_PATH = Path(__file__).resolve().parent / "custom_extension_map.json"


def _load_overrides() -> dict:
    try:
        data = json.loads(_OVERRIDES_PATH.read_text())
    except (FileNotFoundError, ValueError):
        return {}
    return {k: v for k, v in data.items() if not k.startswith("_")}


CUSTOM_OVERRIDES = _load_overrides()


def _source_url(cik10: str, accn: str) -> str:
    """Build the EDGAR filing-index URL for an accession number."""
    if not accn:
        return ""
    folder = accn.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik10)}/{folder}/{accn}-index.htm"


def _resolve(facts: dict[str, Any], spec: MetricSpec, cik10: str) -> tuple[str, dict, str] | None:
    """Resolve a metric to (matched_tag, tag_block, namespace).

    us-gaap candidates first; then a curated custom-extension override for this
    CIK. Returns None if neither resolves (metric is then flagged MISSING).
    """
    all_facts = facts.get("facts", {})
    usgaap = all_facts.get(US_GAAP, {})
    for tag in spec.candidates:
        if tag in usgaap:
            return tag, usgaap[tag], US_GAAP
    override = CUSTOM_OVERRIDES.get(cik10, {}).get(spec.name)
    if override:
        ns, tag = override.get("namespace"), override.get("tag")
        block = all_facts.get(ns, {}).get(tag)
        if block is not None:
            return tag, block, ns
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
        resolved = _resolve(company_facts, spec, cik10)
        if resolved is None:
            records.append({
                "metric": spec.name,
                "status": "MISSING",
                "note": (
                    f"No us-gaap tag among {spec.candidates} and no custom-extension "
                    f"override for CIK {cik10}; add one to custom_extension_map.json."
                ),
            })
            continue

        matched_tag, block, namespace = resolved
        tag_source = "us-gaap" if namespace == US_GAAP else "custom-extension"
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
                "namespace": namespace,
                "tag_source": tag_source,
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
