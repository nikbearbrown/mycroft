"""Render a human-readable Markdown report from the annual metrics.

Every figure is traceable: the provenance appendix maps each fiscal year to the
filing (accession + link) its numbers came from.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any, Optional

BASE_ORDER = [
    ("revenue", "Revenue"),
    ("cost_of_revenue", "Cost of Revenue"),
    ("gross_profit", "Gross Profit"),
    ("operating_income", "Operating Income"),
    ("net_income", "Net Income"),
    ("research_and_development", "R&D"),
    ("operating_cash_flow", "Operating Cash Flow"),
    ("total_assets", "Total Assets"),
    ("total_liabilities", "Total Liabilities"),
    ("stockholders_equity", "Stockholders' Equity"),
    ("current_assets", "Current Assets"),
    ("current_liabilities", "Current Liabilities"),
    ("cash_and_equivalents", "Cash & Equivalents"),
]

RATIO_ORDER = [
    ("gross_margin", "Gross Margin", "pct"),
    ("operating_margin", "Operating Margin", "pct"),
    ("net_margin", "Net Margin", "pct"),
    ("roe", "ROE", "pct"),
    ("roa", "ROA", "pct"),
    ("current_ratio", "Current Ratio", "x"),
    ("debt_to_equity", "Debt / Equity", "x"),
    ("revenue_growth", "Revenue Growth (YoY)", "growth"),
    ("net_income_growth", "Net Income Growth (YoY)", "growth"),
]


def _m(v):   # USD in millions
    return "—" if v is None else f"{v / 1e6:,.0f}"

def _pct(v):
    return "—" if v is None else f"{v * 100:,.1f}%"

def _x(v):
    return "—" if v is None else f"{v:,.2f}"

def _grow(v):
    return "—" if v is None else f"{v * 100:+.1f}%"

_FMT = {"pct": _pct, "x": _x, "growth": _grow}


def render(meta: dict[str, Any], annual: list[dict[str, Any]],
           validation_report: Optional[list[dict]] = None) -> str:
    years = [r["fiscal_year"] for r in annual]
    lines: list[str] = []
    add = lines.append

    gen = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    fy_range = f"{years[0]}–{years[-1]}" if years else "none"

    add(f"# {meta.get('entity')} — Financial Metrics")
    add("")
    add(f"**Ticker:** {meta.get('ticker')}  |  **CIK:** {meta.get('cik')}  |  "
        f"**Source:** SEC EDGAR XBRL (companyfacts)")
    add(f"**Generated:** {gen}  |  **Fiscal years:** {fy_range}")
    add("")
    add("> Deterministic extraction, no LLM in the critical path. Every value is "
        "traceable to its filing — see the Provenance appendix.")
    add("")

    if not annual:
        add("_No annual (10-K / FY) data available for this company._")
        return "\n".join(lines)

    header = "| Metric | " + " | ".join(str(y) for y in years) + " |"
    sep = "|" + "---|" * (len(years) + 1)

    add("## Reported figures ($ millions)")
    add("")
    add(header)
    add(sep)
    for key, label in BASE_ORDER:
        cells = [_m(r["base"].get(key)) for r in annual]
        if all(c == "—" for c in cells):
            continue  # skip metrics this company never reports
        add(f"| {label} | " + " | ".join(cells) + " |")
    add("")

    add("## Derived ratios")
    add("")
    add(header.replace("Metric", "Ratio", 1))
    add(sep)
    for key, label, kind in RATIO_ORDER:
        fmt = _FMT[kind]
        cells = [fmt(r["ratios"].get(key)) for r in annual]
        add(f"| {label} | " + " | ".join(cells) + " |")
    add("")

    if validation_report is not None:
        counts = Counter(v["result"] for v in validation_report)
        add("## Validation summary")
        add("")
        add(f"- Checks run: **{len(validation_report)}**")
        add(f"- PASS: **{counts.get('PASS', 0)}**  |  FAIL: **{counts.get('FAIL', 0)}**  |  "
            f"UNKNOWN: **{counts.get('UNKNOWN', 0)}**")
        fails = [v for v in validation_report if v["result"] == "FAIL"]
        if fails:
            add("")
            add("**Failures:**")
            for v in fails[:20]:
                scope = v.get("period_end") or v.get("metric") or f"FY{v.get('fiscal_year')}"
                add(f"- {scope}: {v['check']} — {v['detail']}")
        add("")

    add("## Provenance appendix")
    add("")
    add("| Fiscal Year | Period End | Primary Filing |")
    add("|---|---|---|")
    for r in annual:
        prov = r["provenance"].get("revenue") or next(iter(r["provenance"].values()), {})
        accn = prov.get("accession") or "—"
        url = prov.get("source_url") or ""
        form = prov.get("form") or "—"
        link = f"[{form} {accn}]({url})" if url else f"{form} {accn}"
        add(f"| {r['fiscal_year']} | {r.get('period_end') or '—'} | {link} |")
    add("")
    add("_Per-metric tag & accession provenance is retained in the JSON output "
        "under `derived_metrics[].provenance`._")
    add("")
    return "\n".join(lines)
