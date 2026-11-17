"""Purpose: Step 4 of recipes/portfolio-price-fetcher.md: take the records step 3 promoted and ask the questions a
per-file schema check cannot: does every holding in the portfolio have exactly one price, did any price come from the
previous close instead of the live price, and is any price implausibly far from the previous close or from what the
holding cost. Transforms the promoted records into verified_records (portfolio order, one per holding, with the
derived numbers beside them) and reports everything else as flags, duplicates or rejects.
Input: data/verified/portfolio-price-fetcher/<set>/validated.json (step 3's promoted records) and the portfolio as the
       workflow's Define Portfolio node declares it (tickers, shares, buy prices).
Output: data/verified/portfolio-price-fetcher/<set>/quality-checked.json with the recipe's step-4 fields (verified_records,
        record_count, duplicates, rejects, flags, quality_notes) plus coverage and the parameters used; and
        quality-audit.md beside it, for a person to read.
What it checks (the three numeric lines are ours, a judgment, written into the output so nobody has to guess them):
        - duplicates: two records for one ticker. Identical ones are collapsed; ones that disagree are BOTH rejected, since
          nothing in the files says which is right (a person decides);
        - coverage: a holding with no verified record is flagged HOLDING_MISSING (the portfolio summary would leave it out);
        - PRICE_FELL_BACK: the effective price is previousClose, because regularMarketPrice was null, 0 or absent;
        - DAY_MOVE_LARGE: regularMarketPrice differs from previousClose by more than DAY_MOVE_LINE (15%);
        - FAR_FROM_BUY_PRICE: effective price is more than BUY_RATIO_HIGH (3x) or under BUY_RATIO_LOW (one third) of the
          workflow's buy price, which in a real feed would suggest a wrong ticker or a unit error.
Side effects: writes those two files. No network, no clock.
Idempotent: Yes; byte-identical output for the same input.
Errors: exit 2 if step 3's output is missing; exit 1 if step 3 rejected anything (tools and quality checks read promoted
        data only, nothing is written), or if this step rejects a record (conflicting duplicates): the output is still
        written so a person can see the whole picture. Flags alone never fail the run; they are for the human report.
Recipe: recipes/portfolio-price-fetcher.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SLUG = "portfolio-price-fetcher"
REPO = Path(__file__).resolve().parents[2]
DAY_MOVE_LINE = 0.15      # our line, a judgment: a day move larger than this is surfaced for a person
BUY_RATIO_HIGH = 3.0      # our line, a judgment
BUY_RATIO_LOW = 1.0 / 3.0  # our line, a judgment


def declared_workflow() -> Path:
    text = (REPO / "recipes" / f"{SLUG}.md").read_text()
    return REPO / re.search(r"^\| Original workflow JSON \| JSON \| `([^`]+)` \|", text, re.M).group(1)


def workflow_portfolio(wf_path: Path) -> list[tuple[str, float, float]]:
    """[(ticker, shares, buyPrice)] in Define Portfolio's own order (the workflow is the source of truth)."""
    wf = json.loads(wf_path.read_text())
    code = next(n["parameters"]["jsCode"] for n in wf["nodes"] if n["name"] == "Define Portfolio")
    return [(t, float(s), float(b)) for t, s, b in
            re.findall(r"ticker:\s*'([^']+)',\s*shares:\s*([\d.]+),\s*buyPrice:\s*([\d.]+)", code)]


def flag(ticker: str, code: str, severity: str, detail: str) -> dict[str, str]:
    return {"ticker": ticker, "code": code, "severity": severity, "detail": detail}


def r2(x: float) -> float:
    return round(x + 0.0, 2)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fixture-set", default="clean", help="the set step 3 validated: clean or any quality-* set")
    ap.add_argument("--verified-dir", default=str(REPO / "data" / "verified" / SLUG))
    ap.add_argument("--workflow", help="override the declared workflow (tests only)")
    ap.add_argument("--sample", action="store_true", help="sample mode, as the recipe's step table lists it; this step is always sample mode (it only reads step 3's output)")
    a = ap.parse_args()

    src = Path(a.verified_dir) / a.fixture_set / "validated.json"
    if not src.exists():
        print(f"step 4 stop: {src} not found; run step 3 first")
        return 2
    validated = json.loads(src.read_text())
    if validated["rejects"]:
        print(f"step 4 stop: step 3 rejected {len(validated['rejects'])} record(s); the quality check reads promoted data only")
        return 1
    order = workflow_portfolio(Path(a.workflow) if a.workflow else declared_workflow())
    holdings = {t: (s, b) for t, s, b in order}

    # duplicates: group by ticker, in file order
    by_ticker: dict[str, list[dict[str, Any]]] = {}
    for rec in validated["records"]:
        by_ticker.setdefault(rec["ticker"], []).append(rec)
    kept: dict[str, dict[str, Any]] = {}
    duplicates, rejects = [], []
    for ticker, recs in by_ticker.items():
        if len(recs) == 1:
            kept[ticker] = recs[0]
            continue
        prices = {(r["effective_price"], r["price_source"]) for r in recs}
        files = [r["file"] for r in recs]
        if len(prices) == 1:
            kept[ticker] = recs[0]
            duplicates.append({"ticker": ticker, "files": files, "identical": True,
                               "action": f"kept {files[0]}, collapsed the rest"})
        else:
            detail = " vs ".join(f"{r['effective_price']} ({r['file']})" for r in recs)
            duplicates.append({"ticker": ticker, "files": files, "identical": False,
                               "action": "rejected every record for this ticker; a person decides which is right"})
            for r in recs:
                rejects.append({"file": r["file"], "reason": f"conflicting records for {ticker}: {detail}"})

    flags: list[dict[str, str]] = []
    verified = []
    for ticker, shares, buy in order:
        rec = kept.get(ticker)
        if rec is None:
            reason = "its records conflict (see rejects)" if any(d["ticker"] == ticker for d in duplicates) else "no response for it in this set"
            flags.append(flag(ticker, "HOLDING_MISSING", "high",
                              f"no verified price for {ticker} ({reason}); the portfolio summary would leave out "
                              f"{shares:g} shares, cost basis {shares * buy:,.2f}"))
            continue
        price = rec["effective_price"]
        rflags = []
        if rec["price_source"] == "previousClose":
            rflags.append("PRICE_FELL_BACK")
            flags.append(flag(ticker, "PRICE_FELL_BACK", "medium",
                              f"regularMarketPrice was {'null' if rec['regularMarketPrice'] is None else rec['regularMarketPrice']}; the previous close {rec['previousClose']} "
                              f"was used, so this is yesterday's price, not today's"))
        day = None
        prev, reg = rec.get("previousClose"), rec.get("regularMarketPrice")
        if rec["price_source"] == "regularMarketPrice" and isinstance(prev, (int, float)) and not isinstance(prev, bool) and prev > 0:
            day = reg / prev - 1.0
            if abs(day) > DAY_MOVE_LINE:
                rflags.append("DAY_MOVE_LARGE")
                flags.append(flag(ticker, "DAY_MOVE_LARGE", "medium",
                                  f"price {reg} is {day * 100:+.1f}% against the previous close {prev} (line: {DAY_MOVE_LINE * 100:.0f}%)"))
        ratio = price / buy
        if ratio > BUY_RATIO_HIGH or ratio < BUY_RATIO_LOW:
            rflags.append("FAR_FROM_BUY_PRICE")
            flags.append(flag(ticker, "FAR_FROM_BUY_PRICE", "medium",
                              f"price {price} is {ratio:.2f}x the workflow's buy price {buy:g} "
                              f"(lines: under {BUY_RATIO_LOW:.2f}x or over {BUY_RATIO_HIGH:g}x)"))
        verified.append({"ticker": ticker, "file": rec["file"], "effective_price": price, "price_source": rec["price_source"],
                         "day_change_pct": None if day is None else r2(day * 100),
                         "price_vs_buy": round(ratio, 3), "quality_flags": rflags})

    notes = [
        f"The three numeric lines are ours, a judgment, not the workflow's: day move {DAY_MOVE_LINE * 100:.0f}%, price over {BUY_RATIO_HIGH:g}x "
        f"or under {BUY_RATIO_LOW:.2f}x the buy price. A flag asks a person to look; it is not a verdict.",
        "Every price in the sample corpus is invented. These checks say nothing about any real market.",
        "Step 5 still reads step 3's output; this step's verified_records are written beside it for the report to cross-check.",
    ]
    out = {
        "recipe": SLUG, "fixture_set": a.fixture_set,
        "parameters": {"DAY_MOVE_LINE": DAY_MOVE_LINE, "BUY_RATIO_HIGH": BUY_RATIO_HIGH, "BUY_RATIO_LOW": round(BUY_RATIO_LOW, 4),
                       "note": "ours, a judgment"},
        "record_count": len(validated["records"]), "verified_count": len(verified),
        "coverage": {"expected": [t for t, _, _ in order], "present": [v["ticker"] for v in verified],
                     "missing": [t for t, _, _ in order if t not in {v["ticker"] for v in verified}]},
        "verified_records": verified, "duplicates": duplicates, "rejects": rejects, "flags": flags, "quality_notes": notes,
    }
    dest = Path(a.verified_dir) / a.fixture_set
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "quality-checked.json").write_text(json.dumps(out, indent=1) + "\n")
    audit = [f"# Step 4 audit: {SLUG}, fixture set `{a.fixture_set}`", "",
             f"Records read from step 3: {out['record_count']} · verified: {len(verified)} of {len(order)} holdings · "
             f"duplicates: {len(duplicates)} · rejected: {len(rejects)} · flags: {len(flags)}", "",
             "## Verified records", "", "| Ticker | Price | Taken from | Day change | Price / buy price | Flags |", "|---|---|---|---|---|---|"]
    audit += [f"| {v['ticker']} | {v['effective_price']} | {v['price_source']} | "
              f"{'n/a' if v['day_change_pct'] is None else format(v['day_change_pct'], '+.2f') + '%'} | {v['price_vs_buy']} | "
              f"{', '.join(v['quality_flags']) or 'none'} |" for v in verified] or ["| (none) | | | | | |"]
    audit += ["", "## Flags", "", "| Ticker | Code | Severity | Detail |", "|---|---|---|---|"]
    audit += [f"| {f['ticker']} | {f['code']} | {f['severity']} | {f['detail']} |" for f in flags] or ["| (none) | | | |"]
    audit += ["", "## Duplicates and rejects", "", "| Ticker | Files | Identical | Action |", "|---|---|---|---|"]
    audit += [f"| {d['ticker']} | {', '.join(d['files'])} | {d['identical']} | {d['action']} |" for d in duplicates] or ["| (none) | | | |"]
    audit += ["", "| Rejected file | Reason |", "|---|---|"] + [f"| {r['file']} | {r['reason']} |" for r in rejects] if rejects else \
        ["", "Rejects: none."]
    audit += ["", "## Notes", ""] + [f"- {n}" for n in notes]
    audit += ["", "This audit reports what it found; it does not say pass. Whether a flag matters, and which of two conflicting prices is right, "
              "is a human call (gate 3)."]
    (dest / "quality-audit.md").write_text("\n".join(audit) + "\n")
    print(f"step 4 {'pass' if not rejects else 'stop'}: {len(verified)} of {len(order)} holdings verified, "
          f"{len(flags)} flag(s), {len(duplicates)} duplicate group(s), {len(rejects)} reject(s) → {dest}")
    for f in flags:
        print(f"  - {f['ticker']} {f['code']}: {f['detail']}")
    for r in rejects:
        print(f"  - rejected {r['file']}: {r['reason']}")
    return 0 if not rejects else 1


if __name__ == "__main__":
    sys.exit(main())
