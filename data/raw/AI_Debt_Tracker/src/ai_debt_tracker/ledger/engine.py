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
LOAN_KINDS = {"term_loan", "revolving_facility", "delayed_draw_facility"}


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
        # P58: an amount the banks may still buy ("up to an additional $45 million") is not the bond's principal
        stated = [e["principal"] for e in es if e.get("principal") and not e.get("option")] \
            or [e["principal"] for e in es if e.get("principal")]
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
                  "option": all(e.get("option") for e in es),
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


def fold_launches(merged: list[dict]) -> tuple[list[dict], list[dict]]:
    """P57 (Week 6): a proposed offering is not a second bond. A launch announcement or a blank preliminary
    prospectus states no coupon yet, so its event has no match key and `merge_events` cannot join it to the priced
    bond that follows. A *new* event with no coupon is folded into a priced new event (one with a coupon) of the
    same maturity year and currency (a launch that names none matches any) from a filing accepted the same day or
    later — when the launch's own filing prices nothing. A filing that prices some tranches and leaves one without a
    coupon is announcing a floating-rate note, not a launch, so its coupon-less tranches are left alone, as is any
    event the reader marked floating. Returns (events, the launches folded), the latter kept for the record."""
    priced_in = {e.get("accession") for e in merged if e.get("coupon_pct") is not None}
    out, folded = [], []
    for e in merged:
        launch = (e.get("action_class") == "new" and e.get("action") in NEW and e.get("coupon_pct") is None
                  and not e.get("floating") and e.get("maturity_year") and e.get("accession") not in priced_in)
        if not launch:
            out.append(e)
            continue
        cur = e.get("currency")
        target = next((p for p in merged if p is not e and p.get("action") in NEW and p.get("coupon_pct") is not None
                       and p.get("maturity_year") == e["maturity_year"]
                       and (not cur or (p.get("currency") or "USD") == cur)
                       and (p.get("accepted") or "") >= (e.get("accepted") or "")), None)
        if target is not None:
            target["sources"] = target.get("sources", []) + _sources(e)
            target["merged_from"] = target.get("merged_from", 1) + e.get("merged_from", 1)
            target.setdefault("launches", []).append(e.get("accession"))
            folded.append(e | {"folded_into": target.get("accession")})
        else:
            out.append(e | {"launch": True})
    return out, folded


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
        if act in NEW and e.get("option"):
            # P58: the banks' option to buy more of a bond is part of that bond's deal, not a bond of its own
            log.append({"change": "option, not a bond (P58)", "id": None, **stamp})
            continue
        if act in NEW and e.get("launch"):
            questions.append({"type": "launch_not_priced", "event": e,
                              "question": "A proposed offering with no coupon and no priced bond after it in the "
                                          "window: was it priced, and when? (P57)"})
            continue
        if act in NEW and e.get("maturity_year") and not e.get("principal"):
            # P56: a bond named with no amount is most often one already outstanding, described in a prospectus
            questions.append({"type": "new_without_amount", "event": e,
                              "question": "A new bond with no amount read: is it new, or one already outstanding "
                                          "described in the filing? (P56)"})
            continue
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
            # Week 6, capacity vs drawn: a new facility's size is a commitment, not money owed, and stays out of
            # total debt; a draw is borrowed money and goes in. The reader says which (a model judgment).
            drawn = act == "draw"
            insts.append({"id": f"fac-{n}", "kind": "facility", "currency": e.get("currency") or "USD",
                          "principal": e.get("principal"), "coupon_pct": e.get("coupon_pct"),
                          "maturity_year": e.get("maturity_year"), "status": "outstanding", "events": [stamp],
                          "commitment_not_drawn": not drawn, "drawn": drawn, "model_judgment": True})
            if drawn and e.get("principal"):
                added_usd += _usd(e["principal"], e.get("currency")) or 0.0
                foreign += _usd(e["principal"], e.get("currency")) is None
                log.append({"change": "loan drawn (in total debt)", "id": f"fac-{n}", "amount": e["principal"], **stamp})
            else:
                log.append({"change": "facility added (commitment; not in total debt)", "id": f"fac-{n}", **stamp})
        elif act in EXIT and e.get("kind") in LOAN_KINDS:
            # a loan repaid: loans are not itemised bond by bond, so it moves total debt and nothing else
            if e.get("principal"):
                removed_usd += _usd(e["principal"], e.get("currency")) or 0.0
                foreign += _usd(e["principal"], e.get("currency")) is None
                log.append({"change": "loan repaid (total debt)", "id": None, "amount": e["principal"], **stamp})
            else:
                log.append({"change": "loan repaid, amount not read (recorded only)", "id": None, **stamp})
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


def fingerprint(e: dict) -> str:
    """A merged event's identity, stable across re-runs of the merge (the investigators address events by it)."""
    return "|".join(str(e.get(k)) for k in ("action", "accession", "currency", "coupon_pct", "maturity_year",
                                            "principal", "kind"))


def amend(merged: list[dict], amendments: list[dict]) -> tuple[list[dict], list[dict]]:
    """Apply the investigators' findings (week 6) to the merged events. Each amendment names an event by its
    `fingerprint` and either drops it (`drop`: why) or replaces fields (`set`: {field: value}) — every replaced value
    with the citation it was read from, so rule 3 still holds. `add` amendments carry whole new events. Returns
    (events, the amendments that found their event)."""
    by_fp = {a["fingerprint"]: a for a in amendments if a.get("fingerprint")}
    out, used = [], []
    for e in merged:
        a = by_fp.get(fingerprint(e))
        if a is None:
            out.append(e)
            continue
        used.append(a)
        if a.get("drop"):
            continue
        e = dict(e)
        e.update(a.get("set", {}))
        for k in ("launch", "option"):
            if k in a.get("clear", []):
                e.pop(k, None)
        e["sources"] = e.get("sources", []) + a.get("sources", [])
        e["investigated"] = a.get("resolution")
        out.append(e)
    out += [x["event"] for x in amendments if x.get("event")]
    used += [x for x in amendments if x.get("event")]
    return sorted(out, key=lambda x: (x.get("accepted") or "", x.get("accession") or "")), used


def closing_ledger(opening: list[dict], opening_totals: dict, events: list[dict], quarter_end: str,
                   amendments: list[dict] | None = None) -> dict:
    """The whole engine: merge → sweep → apply → totals. Totals start from the opening report's (as B0's do)
    and move by the swept and the applied USD amounts; foreign-currency changes are not converted and are
    counted in `meta` instead. `amendments` are the investigators' findings (week 6), applied after the merge."""
    merged, folded = fold_launches(merge_events(events))                           # P57
    merged, used = amend(merged, amendments or [])
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
            "meta": {"merged_events": merged, "after_quarter": later, "launches_folded": folded, "amendments": used,
                     "swept": len(swept), "log": res["log"],
                     "questions": res["questions"],
                     "rejected": res["rejected"], "repaid": [i for i in res["instruments"] if i["status"] == "repaid"],
                     "foreign_changes_not_in_total": res["foreign_changes_not_in_total"]}}
