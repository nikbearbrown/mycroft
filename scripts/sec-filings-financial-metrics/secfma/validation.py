"""Rule-based validation over extracted metrics.

Philosophy (from the writeup): "validation builds trust ... without validation,
automation simply accelerates mistakes." Every check returns PASS / FAIL /
UNKNOWN and never silently drops a value. UNKNOWN is a first-class result:
the system is allowed to admit when it cannot decide.

Period-level checks (per fiscal period): accounting identity, margin bounds,
sum consistency, current-ratio sanity.
Dataset-level checks (across all records): unit consistency, restatement flags.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Literal

Result = Literal["PASS", "FAIL", "UNKNOWN"]
TOLERANCE = 0.01  # 1% relative tolerance for accounting identities
EXPECTED_UNIT = "USD"  # every monetary metric in the concept map is USD


def _by_period(records: list[dict[str, Any]]) -> dict[tuple, dict[str, float]]:
    """Group OK values by (fiscal_year, fiscal_period, period_end)."""
    grouped: dict[tuple, dict[str, float]] = defaultdict(dict)
    for r in records:
        if r.get("status") != "OK" or r.get("value") is None:
            continue
        key = (r.get("fiscal_year"), r.get("fiscal_period"), r.get("period_end"))
        grouped[key][r["metric"]] = float(r["value"])
    return grouped


# --- period-level checks ---------------------------------------------------

def check_accounting_identity(period: dict[str, float]) -> tuple[Result, str]:
    """Assets == Liabilities + StockholdersEquity (within tolerance)."""
    needed = ("total_assets", "total_liabilities", "stockholders_equity")
    if not all(k in period for k in needed):
        return "UNKNOWN", "missing one of assets/liabilities/equity for this period"
    assets = period["total_assets"]
    liab_equity = period["total_liabilities"] + period["stockholders_equity"]
    if assets == 0:
        return "UNKNOWN", "total_assets is zero"
    rel = abs(assets - liab_equity) / abs(assets)
    if rel <= TOLERANCE:
        return "PASS", f"A={assets:,.0f} ~= L+E={liab_equity:,.0f} (rel {rel:.4f})"
    return "FAIL", f"A={assets:,.0f} != L+E={liab_equity:,.0f} (rel {rel:.4f})"


def check_margin_bounds(period: dict[str, float]) -> tuple[Result, str]:
    """Gross/operating/net margins must be <= 100% (net may be negative)."""
    if "revenue" not in period or period["revenue"] == 0:
        return "UNKNOWN", "no non-zero revenue for this period"
    rev = period["revenue"]
    problems = []
    for m in ("gross_profit", "operating_income", "net_income"):
        if m in period and period[m] / rev > 1.0:
            problems.append(f"{m} margin {period[m] / rev:.1%} > 100%")
    if problems:
        return "FAIL", "; ".join(problems)
    return "PASS", "all present margins <= 100%"


def check_sum_consistency(period: dict[str, float]) -> tuple[Result, str]:
    """Cross-statement subtotal checks: gross_profit == revenue - cost_of_revenue,
    and current items must not exceed their totals."""
    problems, checked = [], False
    if all(k in period for k in ("revenue", "cost_of_revenue", "gross_profit")):
        checked = True
        expected = period["revenue"] - period["cost_of_revenue"]
        gp = period["gross_profit"]
        denom = abs(gp) or abs(expected)
        if denom and abs(gp - expected) / denom > TOLERANCE:
            problems.append(f"gross_profit {gp:,.0f} != revenue-cost {expected:,.0f}")
    if "current_assets" in period and "total_assets" in period:
        checked = True
        if period["current_assets"] > period["total_assets"] * (1 + TOLERANCE):
            problems.append("current_assets > total_assets")
    if "current_liabilities" in period and "total_liabilities" in period:
        checked = True
        if period["current_liabilities"] > period["total_liabilities"] * (1 + TOLERANCE):
            problems.append("current_liabilities > total_liabilities")
    if not checked:
        return "UNKNOWN", "no sum relationships computable for this period"
    if problems:
        return "FAIL", "; ".join(problems)
    return "PASS", "subtotal relationships hold"


def check_current_ratio_sanity(period: dict[str, float]) -> tuple[Result, str]:
    """current_assets / current_liabilities should be finite and non-negative."""
    ca, cl = period.get("current_assets"), period.get("current_liabilities")
    if ca is None or cl is None:
        return "UNKNOWN", "missing current assets or current liabilities"
    if cl == 0:
        return "UNKNOWN", "current_liabilities is zero"
    ratio = ca / cl
    if ratio < 0:
        return "FAIL", f"negative current ratio ({ratio:.2f})"
    return "PASS", f"current ratio {ratio:.2f}"


# --- dataset-level checks --------------------------------------------------

def check_unit_consistency(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Each metric should use a single, expected currency unit across all records."""
    units: dict[str, set] = defaultdict(set)
    for r in records:
        if r.get("status") == "OK":
            units[r["metric"]].add(r.get("unit"))
    results = []
    for metric, us in sorted(units.items()):
        if len(us) > 1:
            res, detail = "FAIL", f"mixed units {sorted(u for u in us if u)}"
        elif us and next(iter(us)) != EXPECTED_UNIT:
            res, detail = "FAIL", f"unexpected unit {next(iter(us))}"
        else:
            res, detail = "PASS", EXPECTED_UNIT
        results.append({"metric": metric, "check": "check_unit_consistency",
                        "result": res, "detail": detail})
    return results


def check_restatements(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flag periods where a metric was later restated (value changed across filings).

    The latest-filed value is authoritative; the superseded originals are preserved
    in the record set for the audit trail. Restatements are surfaced as UNKNOWN
    (a legitimate event flagged for a human), not silently passed over.
    """
    groups: dict[tuple, list] = defaultdict(list)
    for r in records:
        if r.get("status") != "OK" or r.get("value") is None or not r.get("period_end"):
            continue
        groups[(r["metric"], r.get("period_start"), r["period_end"])].append(
            (r.get("filed") or "", float(r["value"]))
        )
    results = []
    for (metric, _start, end), entries in groups.items():
        if len({round(v, 2) for _, v in entries}) > 1:
            entries.sort()
            prior, current = entries[0][1], entries[-1][1]
            delta = (current - prior) / abs(prior) if prior else None
            detail = f"{metric} @ {end}: restated {prior:,.0f} -> {current:,.0f}"
            if delta is not None:
                detail += f" ({delta:+.1%}); latest-filed used"
            results.append({"metric": metric, "period_end": end,
                            "check": "check_restatements", "result": "UNKNOWN",
                            "detail": detail})
    if not results:
        results.append({"check": "check_restatements", "result": "PASS",
                        "detail": "no restatements detected (values stable across filings)"})
    return results


def run_all(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Run all checks (period-level + dataset-level); return a flat report."""
    report: list[dict[str, Any]] = []
    period_checks = (check_accounting_identity, check_margin_bounds,
                     check_sum_consistency, check_current_ratio_sanity)
    for (fy, fp, end), period in _by_period(records).items():
        for check in period_checks:
            result, detail = check(period)
            report.append({
                "fiscal_year": fy,
                "fiscal_period": fp,
                "period_end": end,
                "check": check.__name__,
                "result": result,
                "detail": detail,
            })
    report.extend(check_unit_consistency(records))
    report.extend(check_restatements(records))
    return report
