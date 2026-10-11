"""Purpose: Step 5 of recipes/portfolio-price-fetcher.md: run the workflow's two calculation nodes,
Calculate Metrics and Aggregate Summary, as a faithful Python port over verified prices only.
Input: data/verified/portfolio-price-fetcher/<set>/validated.json (step 3's promoted records), the portfolio
       as the workflow's Define Portfolio node declares it, and data/raw/portfolio-price-fetcher/run-envelope.json
       (mode, and the as_of timestamp that stands in for the original's `new Date()`).
Output: data/verified/portfolio-price-fetcher/<set>/portfolio-summary.json, shaped exactly like the original's
        Aggregate Summary output ({stocks, summary}); and logs/portfolio-price-fetcher-run-approved-tools-<date>.json
        with tool_name, input_path, output_path, action_taken, approval_id, no_write_mode (the recipe's step-5
        fields) plus the live-call handoff for the Fetch Stock Prices node, never executed.
Faithful to the original where JavaScript and Python differ:
        - price = regularMarketPrice || previousClose, with JavaScript truthiness (0 falls through);
        - Number.prototype.toFixed(2) rounds the exact binary value half away from zero (Python rounds
          half to even), via js_to_fixed;
        - items are processed in the portfolio's own order, as n8n feeds them, so floating-point sums
          match the original to the last bit;
        - integral numbers are written as JSON integers, as JSON.stringify does.
        lastUpdatedFormatted uses toLocaleString(), which depends on the host's locale: the port writes the
        en-US form of as_of in UTC and the parity check excludes both timestamp fields.
Side effects: writes those two files. Never calls Yahoo Finance or any network service.
Idempotent: Yes; byte-identical output for the same input and envelope.
Errors: exit 1 if validated.json is missing, reports rejects, or holds a ticker outside the portfolio
        (the original would throw on it); nothing is written in that case.
Recipe: recipes/portfolio-price-fetcher.md
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

SLUG = "portfolio-price-fetcher"
REPO = Path(__file__).resolve().parents[2]


# ── JavaScript semantics (our own helpers, first written for the Week 25 contradiction-detection port) ──
def js_truthy(v: Any) -> bool:
    if v is None or v is False:
        return False
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return not (v == 0 or (isinstance(v, float) and math.isnan(v)))
    if isinstance(v, str):
        return v != ""
    return True


def js_or(a: Any, b: Any) -> Any:
    return a if js_truthy(a) else b


def js_to_fixed(x: float, digits: int = 2) -> str:
    """Number.prototype.toFixed: the exact binary value, ties rounded away from zero."""
    return str(Decimal(x).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP))


def js_number(x: float) -> float | int:
    """How JSON.stringify writes a number: integral values carry no '.0'."""
    return int(x) if isinstance(x, float) and x.is_integer() else x


def js_iso_string(iso: str) -> str:
    """new Date(iso).toISOString(): always milliseconds and 'Z', e.g. '2026-10-10T00:00:00.000Z'
    (the parity check caught the port writing '...00Z' before this existed)."""
    d = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(timezone.utc)
    return d.strftime("%Y-%m-%dT%H:%M:%S.") + f"{d.microsecond // 1000:03d}Z"


def js_locale_string(iso: str) -> str:
    """new Date(iso).toLocaleString() under en-US in UTC, e.g. '10/10/2026, 12:00:00 AM'."""
    d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    hour = d.hour % 12 or 12
    return f"{d.month}/{d.day}/{d.year}, {hour}:{d.minute:02d}:{d.second:02d} {'AM' if d.hour < 12 else 'PM'}"


# ── the source of truth ───────────────────────────────────────────────────────────────────────────
def declared_workflow() -> Path:
    text = (REPO / "recipes" / f"{SLUG}.md").read_text()
    return REPO / re.search(r"^\| Original workflow JSON \| JSON \| `([^`]+)` \|", text, re.M).group(1)


def workflow_portfolio(wf_path: Path) -> list[tuple[str, float, float]]:
    """[(ticker, shares, buyPrice)] in Define Portfolio's own order."""
    wf = json.loads(wf_path.read_text())
    code = next(n["parameters"]["jsCode"] for n in wf["nodes"] if n["name"] == "Define Portfolio")
    return [(t, float(s), float(b)) for t, s, b in
            re.findall(r"ticker:\s*'([^']+)',\s*shares:\s*([\d.]+),\s*buyPrice:\s*([\d.]+)", code)]


# ── the two nodes ─────────────────────────────────────────────────────────────────────────────────
def calculate_metrics(rec: dict[str, Any], holdings: dict[str, tuple[float, float]]) -> dict[str, Any]:
    """Calculate Metrics, once per item."""
    current_price = js_or(rec["regularMarketPrice"], rec["previousClose"])
    shares, buy_price = holdings[rec["ticker"]]
    current_value = shares * current_price
    cost_basis = shares * buy_price
    gain_loss = current_value - cost_basis
    return {"ticker": rec["ticker"], "shares": js_number(shares), "buyPrice": js_number(buy_price),
            "currentPrice": js_number(float(current_price)), "currentValue": js_number(current_value),
            "costBasis": js_number(cost_basis), "gainLoss": js_number(gain_loss),
            "gainLossPct": js_to_fixed((gain_loss / cost_basis) * 100)}


def aggregate_summary(stocks: list[dict[str, Any]], as_of: str) -> dict[str, Any]:
    """Aggregate Summary, once over all items."""
    total_value, total_cost = 0.0, 0.0
    for s in stocks:
        total_value = total_value + s["currentValue"]
        total_cost = total_cost + s["costBasis"]
    total_gain = total_value - total_cost
    return {"stocks": stocks, "summary": {
        "totalStocks": len(stocks), "totalCurrentValue": js_to_fixed(total_value),
        "totalCostBasis": js_to_fixed(total_cost), "totalGainLoss": js_to_fixed(total_gain),
        "totalReturn": js_to_fixed((total_gain / total_cost) * 100),
        "lastUpdated": js_iso_string(as_of), "lastUpdatedFormatted": js_locale_string(as_of)}}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fixture-set", default="clean")
    ap.add_argument("--verified-dir", default=str(REPO / "data" / "verified" / SLUG))
    ap.add_argument("--envelope", default=str(REPO / "data" / "raw" / SLUG / "run-envelope.json"))
    ap.add_argument("--log-dir", default=str(REPO / "logs"))
    ap.add_argument("--workflow", help="override the declared workflow (tests only)")
    a = ap.parse_args()

    src = Path(a.verified_dir) / a.fixture_set / "validated.json"
    if not src.exists():
        print(f"step 5 stop: {src} not found; run step 3 first")
        return 1
    validated = json.loads(src.read_text())
    if validated["rejects"]:
        print(f"step 5 stop: step 3 rejected {len(validated['rejects'])} record(s); tools read verified data only")
        return 1
    envelope = json.loads(Path(a.envelope).read_text())
    wf_path = Path(a.workflow) if a.workflow else declared_workflow()
    order = workflow_portfolio(wf_path)
    holdings = {t: (s, b) for t, s, b in order}
    by_ticker = {r["ticker"]: r for r in validated["records"]}
    stray = sorted(set(by_ticker) - set(holdings))
    if stray:
        print(f"step 5 stop: tickers outside the portfolio {stray} (the original would throw)")
        return 1
    stocks = [calculate_metrics(by_ticker[t], holdings) for t, _, _ in order if t in by_ticker]
    result = aggregate_summary(stocks, envelope["as_of"])

    out = src.parent / "portfolio-summary.json"
    out.write_text(json.dumps(result, indent=1) + "\n")
    wf = json.loads(wf_path.read_text())
    fetch = next(n for n in wf["nodes"] if n["name"] == "Fetch Stock Prices")
    record = {
        "tool_name": "Calculate Metrics + Aggregate Summary (Python port)",
        "input_path": str(src.relative_to(REPO)) if src.is_relative_to(REPO) else str(src),
        "output_path": str(out.relative_to(REPO)) if out.is_relative_to(REPO) else str(out),
        "action_taken": f"computed metrics for {len(stocks)} holdings and the portfolio summary from verified sample prices",
        "approval_id": None,
        "no_write_mode": True,
        "mode": envelope.get("mode"),
        "live_handoff": {
            "node": fetch["name"], "type": fetch["type"],
            "url_template": fetch["parameters"].get("url"),
            "approved_for_live_action": False,
            "note": "Sample mode never fetches. A live run needs a logged approval for this call (gate 5) and an ingest script.",
        },
    }
    log = Path(a.log_dir) / f"{SLUG}-run-approved-tools-{envelope['as_of'][:10]}.json"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(json.dumps(record, indent=1) + "\n")
    s = result["summary"]
    print(f"step 5 pass: {len(stocks)} holdings · total value {s['totalCurrentValue']} · "
          f"cost {s['totalCostBasis']} · gain {s['totalGainLoss']} ({s['totalReturn']}%) → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
