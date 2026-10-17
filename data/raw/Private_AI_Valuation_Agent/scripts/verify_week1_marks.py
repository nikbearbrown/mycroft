"""Reproduce the Week 1 hand-verification from the recorded filing data.

This does no network I/O. It reads the positions a human transcribed from
primary_doc.xml and recomputes every price, so the claims in
docs/feasibility.md are reproducible rather than typed.

It also runs the two candidate private-position filters side by side. That
comparison is the Week 1 finding: the filter specified in plan.md drops most
of the universe.

    python scripts/verify_week1_marks.py
"""

import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "week1_verified_marks.json"

# CUSIP placeholders observed across filers. Private positions have no real
# CUSIP; each filer invents its own way of saying so.
CUSIP_PLACEHOLDERS = {"N/A", "000000000", "0", ""}


def price_per_share(position):
    """value_usd / balance, at full precision.

    A missing or zero balance is not a zero price -- it is an absent price.
    """
    balance = Decimal(str(position["balance"]))
    if balance == 0:
        return None
    return Decimal(str(position["valUSD"])) / balance


def passes_plan_filter(p):
    """The filter as written in plan.md line 106."""
    return (
        p["isRestrictedSec"] == "Y"
        and p["fairValLevel"] == 3
        and p["cusip"] == "N/A"
    )


def passes_corrected_filter(p):
    """fairValLevel is the load-bearing field; the others are signals, not gates.

    Verified against six fund families: isRestrictedSec is reported 'N' by ARK
    and Capital Group on unambiguously restricted private stock, and the CUSIP
    placeholder is filer-specific.
    """
    return p["fairValLevel"] == 3 and (
        p["cusip"] in CUSIP_PLACEHOLDERS or p["isRestrictedSec"] == "Y"
    )


def main():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    positions = data["positions"]

    print(f"Loaded {len(positions)} hand-verified positions "
          f"from {len({p['manager'] for p in positions})} managers.\n")

    # --- Prices, grouped by manager and period -------------------------------
    print("PRICE PER SHARE (value_usd / balance)")
    print("-" * 84)
    print(f"{'Manager':<15}{'Period':<13}{'Class / title':<34}{'Price':>12}")
    print("-" * 84)

    by_period = defaultdict(set)
    for p in positions:
        pps = price_per_share(p)
        if pps is None:
            print(f"{p['manager']:<15}{p['period_end']:<13}{p['title'][:32]:<34}{'NO BALANCE':>12}")
            continue
        by_period[p["period_end"]].add(pps)
        title = p["title"].replace("ANTHROPIC PBC", "").replace("Anthropic PBC", "").strip() or "(no class)"
        print(f"{p['manager']:<15}{p['period_end']:<13}{title[:32]:<34}{pps:>12.4f}")

    # --- Convergence ---------------------------------------------------------
    print("\nCONVERGENCE BY PERIOD END")
    print("-" * 84)
    for period in sorted(by_period):
        prices = sorted(by_period[period])
        managers = sorted({p["manager"] for p in positions if p["period_end"] == period})
        spread = (max(prices) - min(prices)) / min(prices) * 100
        rendered = ", ".join(f"{x:.4f}" for x in prices)
        print(f"  {period}  {', '.join(managers):<32} {rendered}   spread {spread:.4f}%")

    # --- The filter comparison ----------------------------------------------
    print("\nFILTER COMPARISON")
    print("-" * 84)
    plan_kept = [p for p in positions if passes_plan_filter(p)]
    corrected_kept = [p for p in positions if passes_corrected_filter(p)]

    print(f"  plan.md filter      kept {len(plan_kept):>2}/{len(positions)} rows, "
          f"{len({p['manager'] for p in plan_kept})} managers: "
          f"{', '.join(sorted({p['manager'] for p in plan_kept}))}")
    print(f"  corrected filter    kept {len(corrected_kept):>2}/{len(positions)} rows, "
          f"{len({p['manager'] for p in corrected_kept})} managers: "
          f"{', '.join(sorted({p['manager'] for p in corrected_kept}))}")

    dropped = {p["manager"] for p in positions} - {p["manager"] for p in plan_kept}
    if dropped:
        print(f"\n  Managers lost to the plan.md filter: {', '.join(sorted(dropped))}")
        print("  Losing these removes the cross-manager comparison the project is built on.")

    # --- Field reliability ---------------------------------------------------
    print("\nFIELD RELIABILITY ACROSS FILERS")
    print("-" * 84)
    for field, values in (
        ("fairValLevel", {p["fairValLevel"] for p in positions}),
        ("isRestrictedSec", {p["isRestrictedSec"] for p in positions}),
        ("cusip", {p["cusip"] for p in positions}),
        ("assetCat", {p["assetCat"] for p in positions}),
        ("lei", {p["lei"] for p in positions}),
    ):
        rendered = ", ".join(sorted(str(v) for v in values))
        verdict = "constant" if len(values) == 1 else f"{len(values)} distinct values"
        print(f"  {field:<18}{verdict:<22}{rendered}")

    print(f"\n  Distinct title strings for one company: "
          f"{len({p['title'] for p in positions})}")
    print(f"  Distinct issuer-name strings:            "
          f"{len({p['name'] for p in positions})}")


if __name__ == "__main__":
    main()
