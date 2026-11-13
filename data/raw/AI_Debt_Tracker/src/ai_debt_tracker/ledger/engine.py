"""The ledger engine (DESIGN.md §7.3): opening ledger + debt events → closing ledger. Plain code, no model.

Three steps, each one a node of the episode graph (`graph/supervisor.py`):

1. **Merge** (`merge_events`). The same bond shows up in a pricing press release, a term sheet and a closing 8-K.
   Events are merged on the match key — action class, currency, coupon (to 0.001 pp) and maturity year (P3).
   The merged event keeps every source; its principal is the amount most of its sources state (ties: the
   latest filing's). Events without a full key are not merged on a guess; two of them that repeat the same
   action, currency and amount are one.
2. **Sweep** (`sweep`). The maturity sweeper retires every instrument whose maturity *year* is before the
   quarter's year — the same rule as baseline B0, so the comparison with B0 isolates what reading adds.
   Most opening instruments carry only a year, so a bond due in the quarter's own year is kept.
3. **Apply** (`apply_events`), oldest filing first (by acceptance time; settlement dates are not parsed yet):
   * *new* (issue, add-on) with a key: if the ledger already holds that bond — the window opens a month before
     the opening report's period end, so a deal may already be in it — nothing changes, except an add-on, which
     adds its amount. Otherwise a new bond is added. A new facility or a draw is added as a facility: its
     commitment is not a drawn balance, so it is not counted in total debt.
   * *exit* (redemption, repayment, tender, exchange, conversion): the matching instrument is removed, or
     reduced when the stated amount is under 99% of what it holds (a partial redemption).
   * a new bond with no maturity year, or an exit that matches nothing, is not applied: it becomes an **open
     question** for the investigators (week 6).

Every applied change carries its sources (accession, document passage ids): a change with no citation is
rejected (§7.1 rule 3). The ledger is a plain dict in the grader's format, so the grader can score it without
knowing who made it; nothing here imports `eval/`.
"""

from __future__ import annotations

import copy
from collections import Counter

RATE_TOL = 0.005                   # P17: coupons rounded to two decimals in some sources
NEW = {"new_issue", "add_on"}
FACILITY = {"new_facility", "draw"}
EXIT = {"redemption", "repayment", "tender_offer", "exchange", "conversion"}
PARTIAL = 0.99


def _key(e: dict):
    if e.get("coupon_pct") is None or not e.get("maturity_year"):
        return None
    return (e.get("action_class"), e.get("currency") or "USD", round(float(e["coupon_pct"]), 3), int(e["maturity_year"]))


def _sources(e: dict) -> list[dict]:
    return e.get("sources") or [{"accession": e.get("accession"), "accepted": e.get("accepted"),
                                 "form": e.get("form"), "cites": e.get("cites", {})}]


def cited(e: dict) -> bool:
    """A change counts only if it names the filing and at least one passage it was read from."""
    return any(s.get("accession") and s.get("cites") for s in _sources(e))


# ------------------------------------------------------------------------------------ merge
def merge_events(events: list[dict]) -> list[dict]:
    groups: dict = {}
    loose = []
    for e in sorted(events, key=lambda x: (x.get("accepted") or "", x.get("accession") or "")):
        k = _key(e)
        if k is None:
            loose.append(e)
            continue
        groups.setdefault(k, []).append(e)
    out = []
    for k, es in groups.items():
        stated = [e["principal"] for e in es if e.get("principal")]
        counts = Counter(stated)
        principal = None
        if counts:
            top = max(counts.values())
            principal = [p for p in stated if counts[p] == top][-1]      # most stated; tie -> the latest
        first = es[0]
        m = {f: first.get(f) for f in ("action", "action_class", "kind", "currency", "coupon_pct", "floating",
                                       "maturity_year")}
        m.update({"principal": principal, "accepted": first.get("accepted"), "accession": first.get("accession"),
                  "sources": [s for e in es for s in _sources(e)], "merged_from": len(es),
                  "model_judgment": True,
                  # an add-on anywhere in the group wins: "new_issue" and "add_on" read from different filings
                  "action": "add_on" if any(e.get("action") == "add_on" for e in es) else first.get("action")})
        out.append(m)
    seen = {}
    for e in loose:
        k = (e.get("action_class"), e.get("currency") or "USD", e.get("principal"), e.get("maturity_year"))
        if e.get("principal") and k in seen:
            seen[k]["sources"] += _sources(e)
            seen[k]["merged_from"] += 1
            continue
        m = dict(e)
        m["sources"], m["merged_from"] = _sources(e), 1
        out.append(m)
        if e.get("principal"):
            seen[k] = m
    return sorted(out, key=lambda x: (x.get("accepted") or "", x.get("accession") or ""))


# ------------------------------------------------------------------------------------ sweep
def sweep(instruments: list[dict], quarter_end: str) -> tuple[list[dict], list[dict]]:
    year = int(quarter_end[:4])
    keep, gone = [], []
    for i in instruments:
        (gone if i.get("maturity_year") and i["maturity_year"] < year else keep).append(i)
    return keep, gone


# ------------------------------------------------------------------------------------ apply
def _matches(inst: dict, e: dict) -> bool:
    if inst.get("kind") != "bond" or inst.get("maturity_year") != e.get("maturity_year"):
        return False
    if (inst.get("currency") or "USD") != (e.get("currency") or "USD"):
        return False
    a, b = inst.get("coupon_pct"), e.get("coupon_pct")
    if a is not None and b is not None:
        return abs(a - b) <= RATE_TOL
    # one side without a coupon: same year and principal within 1% (the grader's rule)
    pa, pb = inst.get("principal"), e.get("principal")
    return bool(pa and pb and abs(pa - pb) <= 0.01 * max(pa, pb))


def _usd(principal, currency) -> float | None:
    return principal if principal and (currency or "USD") == "USD" else None


def apply_events(opening: list[dict], events: list[dict], quarter_end: str) -> dict:
    """Closing ledger, change log and open questions. `opening` instruments are in the grader's format
    (`kind`, `currency`, `principal`, `coupon_pct`, `maturity_year`, `amount_usd`, `source`)."""
    insts = [dict(copy.deepcopy(i), id=f"open-{n}", status="outstanding", events=[]) for n, i in enumerate(opening)]
    log, questions, rejected = [], [], []
    added_usd = removed_usd = 0.0
    foreign = 0
    for n, e in enumerate(events):
        act, src = e.get("action"), _sources(e)
        if not cited(e):
            rejected.append({"event": e, "why": "no citation (DESIGN.md §7.1 rule 3)"})
            continue
        stamp = {"action": act, "accepted": e.get("accepted"), "sources": src}
        if act in NEW:
            if not e.get("maturity_year"):
                questions.append({"type": "new_without_maturity", "event": e,
                                  "question": "A new instrument with no maturity year: which bond is it?"})
                continue
            held = next((i for i in insts if i["status"] == "outstanding" and _matches(i, e)), None)
            if held is not None:
                if act == "add_on" and e.get("principal") and held.get("principal"):
                    held["principal"] += e["principal"]
                    added_usd += _usd(e["principal"], e.get("currency")) or 0.0
                    foreign += _usd(e["principal"], e.get("currency")) is None
                    log.append({"change": "add-on", "id": held["id"], "amount": e["principal"], **stamp})
                else:
                    log.append({"change": "already held", "id": held["id"], **stamp})
                held["events"].append(stamp)
                continue
            new = {"id": f"new-{n}", "kind": "bond", "currency": e.get("currency") or "USD",
                   "principal": e.get("principal"), "coupon_pct": e.get("coupon_pct"),
                   "maturity_year": e.get("maturity_year"), "floating": bool(e.get("floating")),
                   "issued": (e.get("accepted") or "")[:7] or None, "amount_usd": _usd(e.get("principal"), e.get("currency")),
                   "status": "outstanding", "events": [stamp], "model_judgment": True}
            insts.append(new)
            if e.get("principal"):
                added_usd += new["amount_usd"] or 0.0
                foreign += new["amount_usd"] is None
            log.append({"change": "added", "id": new["id"], **stamp})
        elif act in FACILITY:
            insts.append({"id": f"fac-{n}", "kind": "facility", "currency": e.get("currency") or "USD",
                          "principal": e.get("principal"), "coupon_pct": e.get("coupon_pct"),
                          "maturity_year": e.get("maturity_year"), "status": "outstanding", "events": [stamp],
                          "commitment_not_drawn": True, "model_judgment": True})
            log.append({"change": "facility added (commitment; not in total debt)", "id": f"fac-{n}", **stamp})
        elif act in EXIT:
            held = next((i for i in insts if i["status"] == "outstanding" and _matches(i, e)), None) \
                if e.get("maturity_year") else None
            if held is None:
                questions.append({"type": "exit_of_unknown", "event": e,
                                  "question": "Repaid or redeemed, but not in the ledger: was it issued before the "
                                              "opening report, or is it a facility?"})
                continue
            amt, have = e.get("principal"), held.get("principal")
            if amt and have and amt < PARTIAL * have:
                held["principal"] = have - amt
                if held.get("amount_usd"):
                    held["amount_usd"] = _usd(held["principal"], held.get("currency"))
                removed_usd += _usd(amt, held.get("currency")) or 0.0
                log.append({"change": "partly redeemed", "id": held["id"], "amount": amt, **stamp})
            else:
                held["status"] = "repaid"
                removed_usd += _usd(have, held.get("currency")) or 0.0
                log.append({"change": "removed", "id": held["id"], **stamp})
            held["events"].append(stamp)
        else:
            log.append({"change": "recorded only", "id": None, **stamp})
    return {"instruments": insts, "log": log, "questions": questions, "rejected": rejected,
            "added_usd": added_usd, "removed_usd": removed_usd, "foreign_changes_not_in_total": foreign}


def closing_ledger(opening: list[dict], opening_totals: dict, events: list[dict], quarter_end: str) -> dict:
    """The whole engine: merge → sweep → apply → totals. Totals start from the opening report's (as B0's do)
    and move by the swept and the applied USD amounts; foreign-currency changes are not converted and are
    counted in `meta` instead."""
    merged = merge_events(events)
    # P55 (Week 5, dev): the window runs to the target report's filing, weeks after the quarter ends. A bond priced
    # after the quarter end is not owed at it (P4: the ledger follows settlement). Settlement dates are not parsed
    # yet, so the filing's acceptance date stands in: events filed after the quarter end are kept in the record and
    # not applied. (A bond priced on the last days of a quarter and settling after it is still applied — logged.)
    later = [e for e in merged if (e.get("accepted") or "")[:10] > quarter_end]
    merged = [e for e in merged if e not in later]
    kept, swept = sweep(opening, quarter_end)
    res = apply_events(kept, merged, quarter_end)
    out = [i for i in res["instruments"] if i["status"] == "outstanding"]
    totals = dict(opening_totals)
    if "total_debt" in totals:
        swept_usd = sum(i.get("amount_usd") or 0.0 for i in swept)
        totals["total_debt"] = totals["total_debt"] - swept_usd + res["added_usd"] - res["removed_usd"]
    return {"instruments": out, "totals": totals,
            "meta": {"merged_events": merged, "after_quarter": later, "swept": len(swept), "log": res["log"],
                     "questions": res["questions"],
                     "rejected": res["rejected"], "repaid": [i for i in res["instruments"] if i["status"] == "repaid"],
                     "foreign_changes_not_in_total": res["foreign_changes_not_in_total"]}}
