"""Extract canonical metrics from an EDGAR companyfacts payload.

Each extracted value carries full provenance so it can be traced back to the
exact filing and XBRL tag it came from. Nothing here interprets the numbers;
that is validation's job (see validation.py).

Resolution order for each metric: try the us-gaap candidate tags in priority
order. Resolution is PERIOD-AWARE: for every reporting period we pick the value
from the highest-priority candidate tag that actually reports that period. This
handles companies that MIGRATED tags across years (e.g. a filer that reported
net income under ``NetIncomeLoss`` historically and ``ProfitLoss`` in its latest
10-K) — the recent value is no longer lost just because an older tag still
exists in the company's history. If no us-gaap candidate resolves, fall back to
a human-curated custom-extension override for this company
(custom_extension_map.json). If neither resolves, the metric is flagged MISSING
— never guessed.
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


def _select_usgaap(
    usgaap: dict[str, Any], spec: MetricSpec, forms: tuple[str, ...]
) -> tuple[dict[tuple, str], dict[str, list]]:
    """Period-aware candidate selection.

    Returns ``(owner, entries_by_tag)`` where ``owner`` maps each
    ``(fiscal_period, start, end)`` to the HIGHEST-PRIORITY candidate tag that
    reports a value for it, and ``entries_by_tag`` holds each candidate's
    form-filtered, non-null unit entries. Keying on fiscal_period (not just the
    date range) matters: a year-end balance can appear under a high-priority tag
    only as a quarterly (10-Q) comparative while the annual (FY) value for that
    same date lives under a lower-priority tag — keying by date alone would let
    the quarterly-only tag shut out the annual value. Only forms in ``forms`` and
    the metric's expected unit are considered.
    """
    entries_by_tag: dict[str, list] = {}
    owner: dict[tuple, str] = {}
    for tag in spec.candidates:  # priority order: most-preferred first
        block = usgaap.get(tag)
        if not block:
            continue
        ents = [
            e for e in block.get("units", {}).get(spec.unit, [])
            if e.get("form") in forms and e.get("val") is not None
        ]
        if not ents:
            continue
        entries_by_tag[tag] = ents
        for e in ents:
            pk = (e.get("fp"), e.get("start"), e.get("end"))
            owner.setdefault(pk, tag)  # first (highest-priority) tag to report the period wins
    return owner, entries_by_tag


def _record(spec: MetricSpec, entry: dict, tag: str, namespace: str,
            entity: str | None, cik10: str) -> dict[str, Any]:
    return {
        "metric": spec.name,
        "status": "OK",
        "value": entry.get("val"),
        "unit": spec.unit,
        "us_gaap_tag": tag,
        "namespace": namespace,
        "tag_source": "us-gaap" if namespace == US_GAAP else "custom-extension",
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
    }


def extract_metrics(
    company_facts: dict[str, Any],
    cik10: str,
    forms: tuple[str, ...],
) -> list[dict[str, Any]]:
    """Return one record per (metric, period, filing) with provenance, plus MISSING rows."""
    records: list[dict[str, Any]] = []
    entity = company_facts.get("entityName")
    all_facts = company_facts.get("facts", {})
    usgaap = all_facts.get(US_GAAP, {})

    for spec in CANONICAL_METRICS:
        owner, entries_by_tag = _select_usgaap(usgaap, spec, forms)
        emitted = False
        for tag, ents in entries_by_tag.items():
            for entry in ents:
                pk = (entry.get("fp"), entry.get("start"), entry.get("end"))
                if owner.get(pk) != tag:
                    continue  # a higher-priority candidate owns this (period, fiscal-period)
                records.append(_record(spec, entry, tag, US_GAAP, entity, cik10))
                emitted = True

        if not emitted:
            override = CUSTOM_OVERRIDES.get(cik10, {}).get(spec.name)
            if override:
                ns, tag = override.get("namespace"), override.get("tag")
                block = all_facts.get(ns, {}).get(tag)
                if block is not None:
                    for entry in block.get("units", {}).get(spec.unit, []):
                        if entry.get("form") not in forms or entry.get("val") is None:
                            continue
                        records.append(_record(spec, entry, tag, ns, entity, cik10))
                        emitted = True

        if not emitted:
            records.append({
                "metric": spec.name,
                "status": "MISSING",
                "note": (
                    f"No us-gaap tag among {spec.candidates} and no custom-extension "
                    f"override for CIK {cik10}; add one to custom_extension_map.json."
                ),
            })
    return records
