"""Self-checks on a closing ledger (DESIGN.md §7.3). Plain code; a check never changes the ledger.

A check either passes or raises a **flag** with the instruments it is about. Flags are reports for the
investigators (week 6) and for a human reader — not verdicts. The checks need nothing outside the ledger and
the events that made it, so they run the same in a backtest and in live mode.

  cited            every applied change names its filing and the passages it was read from (§7.1 rule 3)
  no_negative      no instrument has a negative principal
  exits_known      every repayment or redemption matched an instrument in the ledger
  no_duplicates    no two outstanding bonds share a match key (currency, coupon, maturity year)
  new_after_quarter a bond added this quarter matures after the quarter's own year (one due sooner is
                   probably a misread year, or a bond repaid already)
  plausible_change net new borrowing in dollars is at most half the opening total debt (larger is possible —
                   an acquisition financing — but worth a look)
"""

from __future__ import annotations

from collections import Counter

from .engine import cited

PLAUSIBLE = 0.5


def run_checks(ledger: dict, quarter_end: str, opening_total: float | None = None) -> dict:
    meta = ledger.get("meta", {})
    year = int(quarter_end[:4])
    flags, passed = [], []

    def check(name: str, bad: list, what: str):
        if bad:
            flags.append({"check": name, "what": what, "items": bad[:10], "count": len(bad)})
        else:
            passed.append(name)

    changes = [x for x in meta.get("log", []) if x["change"] != "already held"]
    check("cited", [x for x in changes if not cited(x)] + [r["why"] for r in meta.get("rejected", [])],
          "changes without a citation")
    check("no_negative", [i["id"] for i in ledger["instruments"] if (i.get("principal") or 0) < 0],
          "negative principal")
    check("exits_known", [q["question"] for q in meta.get("questions", []) if q["type"] == "exit_of_unknown"],
          "repayments that match no instrument in the ledger")
    keys = Counter((i.get("currency") or "USD", round(i["coupon_pct"], 3), i["maturity_year"])
                   for i in ledger["instruments"]
                   if i.get("kind") == "bond" and i.get("coupon_pct") is not None and i.get("maturity_year"))
    check("no_duplicates", [k for k, n in keys.items() if n > 1], "two outstanding bonds with the same key")
    check("new_after_quarter", [i["id"] for i in ledger["instruments"]
                                if str(i.get("id", "")).startswith("new-") and (i.get("maturity_year") or 9999) < year],
          "a new bond maturing before the quarter's year")
    added = sum(i.get("amount_usd") or 0.0 for i in ledger["instruments"] if str(i.get("id", "")).startswith("new-"))
    if opening_total:
        check("plausible_change", [f"added ${added / 1e9:.2f} bn against ${opening_total / 1e9:.2f} bn opening"]
              if added > PLAUSIBLE * opening_total else [], "net new borrowing over half the opening debt")
    return {"passed": passed, "flags": flags, "questions": meta.get("questions", [])}
