"""Derived financial metrics computed from extracted base metrics.

Deterministic and provenance-aware: for each fiscal year we pick one value per
base metric (FY period, latest-filed — so restatements win) and compute ratios
only where every needed input is present. A missing input yields None, never a
guess.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Optional

PROVENANCE_FIELDS = ("us_gaap_tag", "accession", "form", "filed", "source_url")


def _period_days(start: Optional[str], end: Optional[str]) -> Optional[int]:
    if not start or not end:
        return None
    try:
        return (date.fromisoformat(end) - date.fromisoformat(start)).days
    except ValueError:
        return None


def _safe_div(num: Optional[float], den: Optional[float]) -> Optional[float]:
    if num is None or den in (None, 0):
        return None
    return num / den


def _growth(prev: Optional[float], cur: Optional[float]) -> Optional[float]:
    if prev in (None, 0) or cur is None:
        return None
    return (cur - prev) / abs(prev)


def _annual_records(records: list[dict[str, Any]]) -> dict[str, dict[str, dict]]:
    """Pick one record per (period_end, metric): annual period, latest filed.

    We key on the *period-end date*, NOT the reported ``fy`` field. In a 10-K
    the comparative prior-year figures inherit the filing's ``fy``, so grouping
    by ``fy`` would collapse two or three different years onto one label. The
    period-end date is unambiguous and aligns income (duration) and balance
    (instant) items for the same fiscal year. Latest ``filed`` wins, so
    restatements supersede originals.
    """
    best: dict[tuple, dict] = {}
    for r in records:
        if r.get("status") != "OK" or r.get("fiscal_period") != "FY":
            continue
        end = r.get("period_end")
        if r.get("value") is None or not end:
            continue
        if r.get("period_type") == "duration":
            days = _period_days(r.get("period_start"), end)
            if days is None or not (330 <= days <= 400):
                continue  # require a genuine full-year duration
        key = (end, r["metric"])
        cur = best.get(key)
        if cur is None or (r.get("filed") or "") > (cur.get("filed") or ""):
            best[key] = r
    out: dict[str, dict[str, dict]] = {}
    for (end, metric), r in best.items():
        out.setdefault(end, {})[metric] = r
    return out


def _ratios(v: dict[str, float], prev: Optional[dict[str, float]]) -> dict[str, Optional[float]]:
    ratios = {
        "gross_margin": _safe_div(v.get("gross_profit"), v.get("revenue")),
        "operating_margin": _safe_div(v.get("operating_income"), v.get("revenue")),
        "net_margin": _safe_div(v.get("net_income"), v.get("revenue")),
        "roe": _safe_div(v.get("net_income"), v.get("stockholders_equity")),
        "roa": _safe_div(v.get("net_income"), v.get("total_assets")),
        "current_ratio": _safe_div(v.get("current_assets"), v.get("current_liabilities")),
        "debt_to_equity": _safe_div(v.get("total_liabilities"), v.get("stockholders_equity")),
        "revenue_growth": _growth((prev or {}).get("revenue"), v.get("revenue")) if prev else None,
        "net_income_growth": _growth((prev or {}).get("net_income"), v.get("net_income")) if prev else None,
    }
    return ratios


def build_annual(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One row per fiscal year (chronological) with base values, ratios, provenance.

    ``fiscal_year`` is derived from the year of the period-end date. For companies
    whose fiscal year ends in the first half of the calendar year this may differ
    from the company's own FY label — a known, documented convention.
    """
    by_end = _annual_records(records)
    rows: list[dict[str, Any]] = []
    prev_vals: Optional[dict[str, float]] = None
    for end in sorted(by_end):
        recs = by_end[end]
        vals = {m: r["value"] for m, r in recs.items()}
        rows.append({
            "fiscal_year": int(end[:4]),
            "period_end": end,
            "base": vals,
            "ratios": _ratios(vals, prev_vals),
            "provenance": {
                m: {k: r.get(k) for k in PROVENANCE_FIELDS} for m, r in recs.items()
            },
        })
        prev_vals = vals
    return rows
