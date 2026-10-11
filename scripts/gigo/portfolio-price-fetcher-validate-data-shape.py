"""Purpose: Step 3 of recipes/portfolio-price-fetcher.md: check every raw price response against the field
contract the workflow's own code relies on, report every finding, and promote only clean records.
Input: one fixture set of Yahoo Finance chart responses, data/raw/portfolio-price-fetcher/sample/<set>/
       (every file in the set is read, whatever its extension, so an unparseable response is reported, not
       skipped), and the portfolio as the workflow's Define Portfolio node declares it.
Output: data/verified/portfolio-price-fetcher/<set>/validated.json with record_count, required_fields_present,
        missing_fields, parse_errors, schema_version (the recipe's step-3 fields) plus records (promoted) and
        rejects (file, reason); and validate-audit.md beside it, for a person to read.
Contract (from the Calculate Metrics node): chart.result is a non-empty list; result[0].meta is an object;
        meta.symbol is a ticker in the portfolio; the effective price, regularMarketPrice || previousClose
        with JavaScript's || (so 0, null or a missing value falls through), is a finite number > 0.
Side effects: writes those two files. No network.
Idempotent: Yes; byte-identical output for the same input.
Errors: exit 1 if any file is rejected (all findings are still reported and the clean records still promoted,
        so a person can see the whole picture); exit 2 if the set directory is missing.
Recipe: recipes/portfolio-price-fetcher.md
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

SLUG = "portfolio-price-fetcher"
REPO = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "yahoo-chart-meta/1 (fields read by the workflow's Calculate Metrics node)"
REQUIRED = ["chart.result[0].meta.symbol", "chart.result[0].meta.regularMarketPrice | previousClose"]


def declared_workflow() -> Path:
    text = (REPO / "recipes" / f"{SLUG}.md").read_text()
    return REPO / re.search(r"^\| Original workflow JSON \| JSON \| `([^`]+)` \|", text, re.M).group(1)


def workflow_portfolio(wf_path: Path) -> dict[str, dict[str, float]]:
    """The portfolio exactly as the Define Portfolio node declares it (the workflow is the source of truth)."""
    wf = json.loads(wf_path.read_text())
    code = next(n["parameters"]["jsCode"] for n in wf["nodes"] if n["name"] == "Define Portfolio")
    rows = re.findall(r"ticker:\s*'([^']+)',\s*shares:\s*([\d.]+),\s*buyPrice:\s*([\d.]+)", code)
    return {t: {"shares": float(s), "buyPrice": float(b)} for t, s, b in rows}


def js_truthy(v: Any) -> bool:
    """JavaScript truthiness for the values a JSON price can take (our own helper, as in Week 25's port)."""
    if v is None or v is False:
        return False
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return not (v == 0 or (isinstance(v, float) and math.isnan(v)))
    if isinstance(v, str):
        return v != ""
    return True


def check(doc: Any, portfolio: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None, list[str]]:
    """(record, reject reason, missing fields) for one parsed response."""
    result = ((doc or {}).get("chart") or {}).get("result") if isinstance(doc, dict) else None
    if not isinstance(result, list) or not result:
        return None, "chart.result is missing or empty (the original reads result[0])", ["chart.result[0]"]
    meta = result[0].get("meta") if isinstance(result[0], dict) else None
    if not isinstance(meta, dict):
        return None, "chart.result[0].meta is not an object", ["chart.result[0].meta"]
    symbol = meta.get("symbol")
    if not isinstance(symbol, str) or not symbol:
        return None, "meta.symbol is missing", ["chart.result[0].meta.symbol"]
    if symbol not in portfolio:
        return None, f"meta.symbol {symbol!r} is not in the workflow's portfolio", []
    regular, previous = meta.get("regularMarketPrice"), meta.get("previousClose")
    price = regular if js_truthy(regular) else previous          # JavaScript: regular || previous
    if price is None:
        return None, "neither regularMarketPrice nor previousClose is present", \
            ["chart.result[0].meta.regularMarketPrice | previousClose"]
    if isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
        return None, f"effective price {price!r} is not a finite number > 0", []
    return {"ticker": symbol, "regularMarketPrice": regular, "previousClose": previous,
            "effective_price": price,
            "price_source": "regularMarketPrice" if js_truthy(regular) else "previousClose"}, None, []


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fixture-set", default="clean", help="clean | defective | any folder under sample/")
    ap.add_argument("--raw-dir", default=str(REPO / "data" / "raw" / SLUG / "sample"))
    ap.add_argument("--out-dir", default=str(REPO / "data" / "verified" / SLUG))
    ap.add_argument("--workflow", help="override the declared workflow (tests only)")
    a = ap.parse_args()

    src = Path(a.raw_dir) / a.fixture_set
    if not src.is_dir():
        print(f"step 3 stop: no fixture set at {src}")
        return 2
    portfolio = workflow_portfolio(Path(a.workflow) if a.workflow else declared_workflow())
    records, rejects, parse_errors, missing = [], [], [], set()
    files = sorted(p for p in src.iterdir() if p.is_file())
    for p in files:
        try:
            doc = json.loads(p.read_text())
        except json.JSONDecodeError as e:
            parse_errors.append({"file": p.name, "error": str(e)})
            rejects.append({"file": p.name, "reason": "the response is not valid JSON"})
            continue
        rec, reason, miss = check(doc, portfolio)
        missing.update(miss)
        if rec:
            records.append({"file": p.name, **rec})
        else:
            rejects.append({"file": p.name, "reason": reason})

    out = {
        "recipe": SLUG, "fixture_set": a.fixture_set, "schema_version": SCHEMA_VERSION,
        "record_count": len(files), "promoted_count": len(records), "rejected_count": len(rejects),
        "required_fields_present": not missing and not parse_errors,
        "required_fields": REQUIRED, "missing_fields": sorted(missing), "parse_errors": parse_errors,
        "records": records, "rejects": rejects,
    }
    dest = Path(a.out_dir) / a.fixture_set
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "validated.json").write_text(json.dumps(out, indent=1) + "\n")
    audit = [f"# Step 3 audit: {SLUG}, fixture set `{a.fixture_set}`", "",
             f"Files read: {len(files)} · promoted: {len(records)} · rejected: {len(rejects)} · "
             f"parse errors: {len(parse_errors)}", "", f"Contract: {SCHEMA_VERSION}", "",
             "## Promoted", "", "| File | Ticker | Effective price | Taken from |", "|---|---|---|---|"]
    audit += [f"| {r['file']} | {r['ticker']} | {r['effective_price']} | {r['price_source']} |" for r in records] or ["| (none) | | | |"]
    audit += ["", "## Rejected", "", "| File | Reason |", "|---|---|"]
    audit += [f"| {r['file']} | {r['reason']} |" for r in rejects] or ["| (none) | |"]
    audit += ["", "This audit reports what it found; it does not say pass. Whether the rejects are acceptable is a human call (gate 3)."]
    (dest / "validate-audit.md").write_text("\n".join(audit) + "\n")
    print(f"step 3 {'pass' if not rejects else 'stop'}: {len(records)} promoted, {len(rejects)} rejected → {dest}")
    for r in rejects:
        print(f"  - {r['file']}: {r['reason']}")
    return 0 if not rejects else 1


if __name__ == "__main__":
    sys.exit(main())
