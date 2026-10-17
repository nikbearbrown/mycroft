"""Measure the deterministic matcher against the golden set. Sets the thresholds.

    python -m scripts.score_matcher              # table to stdout + metrics json
    python -m scripts.score_matcher --no-write   # look before writing

Two systems are scored on the same labels, which is the only way to know
whether this week's work was worth doing:

  A  like_patterns   the frozen '%ANTHROPIC%' style patterns Week 2 shipped
                     and that produced the 5,806-row universe layer.
  B  matcher_v1      LEI, exact alias, SPV unwrap, gated fuzzy (src/resolve).

Four measurements, in the order they should be read:

  1. Company resolution, reported on the hard subset first. Precision and
     recall, macro (per issuer string) and micro (weighted by holdings),
     because a spelling used once and a spelling used 990 times are not
     equally important and neither number alone says so.

  2. The threshold sweep. Matcher v1 emits a confidence; sweeping it gives the
     precision/recall curve, and the operating points are read off the curve
     rather than guessed. This is the deliverable plan.md asks for.

  3. Share-class parsing, measured against ASSET_CAT -- an independent field
     the filer sets separately. The golden set's own share_class column is
     parser output and cannot score the parser; saying so is the point.

  4. Price-series consistency: within one (company, share class, period end),
     do the filers agree on a price? This is what a class parse is FOR. Too
     coarse and the 10x preferred rows contaminate a common-stock series; too
     fine and one security splits into two. Neither failure is visible in a
     precision number.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.ingest.build_parquet import ALL_QUARTERS, PARQUET  # noqa: E402
from src.ingest.universe import ASSET_CATS  # noqa: E402
from src.resolve.match import like_pattern_company, resolve  # noqa: E402
from src.resolve.normalize import BASIS_PER_SHARE, COMMON, PREFERRED, parse_class  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "golden_set_v1.json"
METRICS = ROOT / "docs" / "_matcher_metrics.json"

NOT_IN_UNIVERSE = "NOT_IN_UNIVERSE"
UNKNOWN = "UNKNOWN"

# An UNKNOWN label is not a negative and not a positive: the filing does not
# say. Scoring it either way would be inventing a fact, so those entries are
# excluded from precision and recall and counted separately -- P3.
SCORABLE = lambda company: company != UNKNOWN  # noqa: E731

SWEEP = [0.0, 0.50, 0.70, 0.75, 0.80, 0.85, 0.90, 0.92, 0.95, 0.99, 1.00]


def _prf(tp: int, fp: int, fn: int) -> dict:
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision and recall and precision + recall
        else None
    )
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round(precision, 4) if precision is not None else None,
        "recall": round(recall, 4) if recall is not None else None,
        "f1": round(f1, 4) if f1 is not None else None,
    }


def score(entries, predict, weight=lambda e: 1) -> dict:
    """Precision and recall over a multi-class problem with a reject option.

    A prediction of None means 'not one of ours'. So:
      tp  predicted a company and it is the right company
      fp  predicted a company and the truth is a different company, or none
      fn  predicted none and the truth is a company
    A wrong company therefore costs both a false positive and a false
    negative, which is correct: the mark lands on the wrong price series and
    is missing from the right one.
    """
    tp = fp = fn = 0
    per_company: dict = {}
    errors = []
    for entry in entries:
        truth = entry["company"]
        if not SCORABLE(truth):
            continue
        predicted = predict(entry)
        w = weight(entry)
        truth_company = None if truth == NOT_IN_UNIVERSE else truth

        if predicted and predicted == truth_company:
            tp += w
            per_company.setdefault(truth_company, [0, 0, 0])[0] += w
        elif predicted and predicted != truth_company:
            fp += w
            per_company.setdefault(predicted, [0, 0, 0])[1] += w
            if truth_company:
                fn += w
                per_company.setdefault(truth_company, [0, 0, 0])[2] += w
            errors.append((entry["id"], entry["issuer_name"], truth, predicted, "false_positive"))
        elif not predicted and truth_company:
            fn += w
            per_company.setdefault(truth_company, [0, 0, 0])[2] += w
            errors.append((entry["id"], entry["issuer_name"], truth, None, "false_negative"))

    return {
        "overall": _prf(tp, fp, fn),
        "per_company": {
            name: _prf(*counts) for name, counts in sorted(per_company.items())
        },
        "errors": [
            {"id": i, "issuer_name": n, "truth": t, "predicted": p, "kind": k}
            for i, n, t, p, k in errors
        ],
    }


def _v1(entry, threshold: float = 0.0):
    match = resolve(entry["issuer_name"], entry["issuer_title"])
    if match.resolved and match.score >= threshold:
        return match.company
    return None


# --------------------------------------------------------------------------
# Share-class measurements, both against fields the parser never sees
# --------------------------------------------------------------------------


def class_vs_asset_cat(con) -> dict:
    """Does the title grammar's COM/PFD agree with the filer's own ASSET_CAT?

    ASSET_CAT is set by the filer in a separate field, so it is an independent
    check on the grammar -- and an unreliable one, which is the finding: where
    they disagree, one of the two is wrong and the disagreements cluster by
    filer rather than scattering.
    """
    rows = con.execute(f"""
        SELECT ISSUER_TITLE, ISSUER_NAME, ASSET_CAT, REGISTRANT_NAME, count(*)
        FROM u WHERE ASSET_CAT IN {ASSET_CATS} GROUP BY 1, 2, 3, 4
    """).fetchall()

    agree = disagree = unknown = 0
    by_filer: dict = {}
    for title, name, asset_cat, registrant, n in rows:
        kind = parse_class(title, name).kind
        if kind not in (COMMON, PREFERRED) or asset_cat not in ("EC", "EP"):
            unknown += n
            continue
        expected = COMMON if asset_cat == "EC" else PREFERRED
        if kind == expected:
            agree += n
        else:
            disagree += n
            by_filer[registrant] = by_filer.get(registrant, 0) + n
    total = agree + disagree
    return {
        "holdings_compared": total,
        "agree": agree,
        "disagree": disagree,
        "agreement_rate": round(agree / total, 4) if total else None,
        "not_comparable": unknown,
        "disagreements_by_filer": dict(sorted(by_filer.items(), key=lambda kv: -kv[1])[:10]),
    }


def price_consistency(con, tolerance: float = 0.005) -> dict:
    """Within one (company, class, period end), do the filers agree on a price?

    A cell whose prices span more than the tolerance is a cell where the class
    parse has merged two securities -- or where the filers genuinely disagree,
    which is the project's actual subject. The two are told apart by the size
    of the spread: a near-integer multiple is a class or split artefact, a few
    per cent is dispersion.
    """
    rows = con.execute(f"""
        SELECT COMPANY, ISSUER_NAME, ISSUER_TITLE, PERIOD_END, PRICE_PER_SHARE
        FROM u
        WHERE COMPANY IS NOT NULL AND PRICE_PER_SHARE > 0 AND PERIOD_END IS NOT NULL
          AND (ASSET_CAT IN {ASSET_CATS} OR ASSET_CAT IS NULL)
    """).fetchall()

    cells: dict = {}
    for company, name, title, period, price in rows:
        parsed = parse_class(title, name)
        if parsed.basis != BASIS_PER_SHARE:
            continue
        cells.setdefault((company, parsed.label(), str(period)), []).append(float(price))

    tight = loose = 0
    tenfold = []
    for (company, label, period), prices in cells.items():
        lo, hi = min(prices), max(prices)
        if len(prices) < 2:
            continue
        if (hi - lo) / lo <= tolerance:
            tight += 1
        else:
            loose += 1
            ratio = hi / lo
            if abs(ratio - round(ratio)) < 0.02 and round(ratio) >= 2:
                tenfold.append(
                    {"company": company, "class": label, "period_end": period,
                     "ratio": round(ratio, 3), "low": round(lo, 2), "high": round(hi, 2)}
                )
    multi = tight + loose
    return {
        "cells": len(cells),
        "cells_with_two_or_more_filers": multi,
        "agree_within_tolerance": tight,
        "disagree": loose,
        "agreement_rate": round(tight / multi, 4) if multi else None,
        "near_integer_ratio_cells": sorted(tenfold, key=lambda c: -c["ratio"])[:12],
        "near_integer_ratio_count": len(tenfold),
    }


# --------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    entries = fixture["entries"]
    hard = [e for e in entries if e["evidence_class"] not in ("E2_self_name", "E0_none")]
    holdings = lambda e: e["holdings"]  # noqa: E731

    subsets = {"all": entries, "hard": hard}
    systems = {
        "A_like_patterns": lambda e: like_pattern_company(e["issuer_name"]),
        "B_matcher_v1": _v1,
    }

    results: dict = {"subsets": {}}
    print(f"golden set v{fixture['golden_set_version']}: {len(entries)} strings, "
          f"{sum(map(holdings, entries)):,} holdings "
          f"({len(hard)} strings in the hard subset)\n")

    print("1. COMPANY RESOLUTION")
    print(f"   {'subset':6} {'system':17} {'weighting':10} "
          f"{'P':>7} {'R':>7} {'F1':>7}   {'tp':>5} {'fp':>4} {'fn':>4}")
    for subset_name, subset in subsets.items():
        results["subsets"][subset_name] = {}
        for system_name, predict in systems.items():
            entry = {}
            for weighting, weight in (("macro", lambda e: 1), ("micro", holdings)):
                scored = score(subset, predict, weight)
                entry[weighting] = scored
                o = scored["overall"]
                fmt = lambda v: f"{v:.4f}" if v is not None else "   -  "  # noqa: E731
                print(f"   {subset_name:6} {system_name:17} {weighting:10} "
                      f"{fmt(o['precision']):>7} {fmt(o['recall']):>7} {fmt(o['f1']):>7}   "
                      f"{o['tp']:>5} {o['fp']:>4} {o['fn']:>4}")
            results["subsets"][subset_name][system_name] = entry

    print("\n2. THRESHOLD SWEEP -- matcher v1, hard subset, macro")
    print(f"   {'threshold':>10} {'P':>8} {'R':>8} {'F1':>8}  resolved  errors")
    sweep = []
    for threshold in SWEEP:
        scored = score(hard, lambda e, t=threshold: _v1(e, t))
        o = scored["overall"]
        resolved = sum(1 for e in hard if _v1(e, threshold))
        fmt = lambda v: f"{v:.4f}" if v is not None else "   -    "  # noqa: E731
        print(f"   {threshold:>10.2f} {fmt(o['precision']):>8} {fmt(o['recall']):>8} "
              f"{fmt(o['f1']):>8}  {resolved:>8}  "
              f"{', '.join(e['issuer_name'][:22] for e in scored['errors'][:3])}")
        sweep.append({"threshold": threshold, **o, "resolved": resolved,
                      "errors": scored["errors"]})
    results["threshold_sweep"] = sweep

    con = duckdb.connect()
    uni = [(PARQUET / q / "universe_holdings.parquet").as_posix() for q in ALL_QUARTERS]
    con.execute(f"CREATE VIEW u AS SELECT * FROM read_parquet([{','.join(map(repr, uni))}])")

    print("\n3. SHARE-CLASS KIND vs the filer's own ASSET_CAT")
    cac = class_vs_asset_cat(con)
    results["class_vs_asset_cat"] = cac
    print(f"   {cac['holdings_compared']:,} holdings comparable; "
          f"{cac['agree']:,} agree, {cac['disagree']:,} disagree "
          f"({cac['agreement_rate']:.4f})")
    for filer, n in cac["disagreements_by_filer"].items():
        print(f"     {n:>5}  {filer}")

    print("\n4. PRICE CONSISTENCY within (company, class, period end)")
    pc = price_consistency(con)
    results["price_consistency"] = pc
    print(f"   {pc['cells']:,} cells, {pc['cells_with_two_or_more_filers']:,} with two or "
          f"more filers; {pc['agree_within_tolerance']:,} agree within 0.5% "
          f"({pc['agreement_rate']:.4f})")
    print(f"   {pc['near_integer_ratio_count']} cells span a near-integer ratio "
          f"(a class or split artefact, never dispersion):")
    for cell in pc["near_integer_ratio_cells"][:8]:
        print(f"     {cell['ratio']:>6.2f}x  {cell['company'][:34]:36} {cell['class'][:14]:16} "
              f"{cell['period_end']}  {cell['low']} -> {cell['high']}")

    if not args.no_write:
        METRICS.write_text(json.dumps(results, indent=1), encoding="utf-8")
        print(f"\nwrote {METRICS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
