"""Grade a ledger against the answer key (DESIGN.md §9.1–9.2).

A **ledger** is what a tracker (a baseline now, the agent later) claims a company owes at the end
of the quarter. It is a plain dict, so anything can produce one:

    {"instruments": [{"kind": "bond" | "offering" | "facility" | "other",
                      "currency": "USD", "principal": 1.25e9, "coupon_pct": 4.75,
                      "maturity_year": 2031, "issued": "2026-05" | None, "amount_usd": 1.2e9}],
     "totals": {"total_debt": ..., "current": ..., "due_next_12m": ..., "due_2_5": ..., "due_after_5": ...}}

The **answer key** is the target report's record from `answer_key.AnswerKey.filing_record`.
Grading happens at the episode's level (manifests: `graded_level`), and every episode is also
graded at L3:

  L1 — per bond. A ledger bond *matches* a true bond when the currency and maturity year agree and
       the coupons agree within 0.01 percentage points (P17's rounding included). A true bond
       with no tagged coupon (some 10-Qs) matches on maturity year and principal within 1%
       instead. Pairs are one-to-one, chosen by optimal assignment (Hungarian algorithm), so one
       ledger bond can never claim two true bonds. *Principal accuracy* is then scored on the
       matched pairs: within 1% of face, or 2% of carrying amount when only that is tagged (P5).
  L2 — per offering. Each true offering (and any single bond the report tags beside them) is one
       unit: an amount in a currency, an issue period, a maturity. A ledger unit matches when
       the currency agrees, the amount is within 1%, and the issue period and maturity agree
       wherever both sides state them. Ledger bonds that share an issue period are summed into
       one unit first, so a bond-level ledger can be graded against an offering-level report.
  L3 — totals: total debt, current portion and the maturity ladder (next 12 months, years 2–5,
       after year 5), each within 2%, wherever the report tags it.

**Change detection** (L1, when the start report is itemised too): bonds *added* during the
quarter are true bonds with no match in the start report; bonds *removed* are start bonds with no
match in the target. A tracker catches an addition if its ledger matches it, and a removal if its
ledger no longer holds it.

Facilities and loans are not graded instrument by instrument yet — their drawn balances move
without announcements (P6, P7) and week 6 adds capacity vs drawn. They count through L3 totals.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment

from .answer_key import TOTAL_DEBT_CHAIN

RATE_TOL = 0.0101          # ±0.01 pp, inclusive of P17's half-basis-point rounding
PRINCIPAL_TOL = 0.01
CARRYING_TOL = 0.02
TOTAL_TOL = 0.02

BIG = 1e6


# ------------------------------------------------------------------------------------ truth side
def total_debt(totals: dict) -> tuple[float | None, str | None]:
    for label, keys in TOTAL_DEBT_CHAIN:
        if totals.get(keys[0]):
            return totals[keys[0]] + sum(next((totals[k] for k in alt.split("|") if totals.get(k)), 0)
                                         for alt in keys[1:]), label
    return None, None


def truth_totals(record: dict) -> dict:
    t = record["totals"]
    out = {}
    total, _ = total_debt(t)
    if total:
        out["total_debt"] = total
    cur = t.get("long_term_debt_current") or t.get("debt_current")
    if cur:
        out["current"] = cur
    if t.get("due_next_12m") is not None and "due_next_12m" in t:
        out["due_next_12m"] = t["due_next_12m"]
    years = [t.get(f"due_year_{k}") for k in (2, 3, 4, 5)]
    if all(v is not None for v in years):
        out["due_2_5"] = sum(years)
    if t.get("due_after_5") is not None:
        out["due_after_5"] = t["due_after_5"]
    return out


def principal_of(inst: dict) -> tuple[float | None, str | None]:
    """The principal in the bond's own currency, and whether it is the face or carrying amount."""
    cur = inst.get("currency") or "USD"
    if inst.get("face") and (inst.get("face_uom") or cur) == cur:
        return inst["face"], "face"
    if inst.get("carrying") and (inst.get("carrying_uom") or cur) == cur:
        return inst["carrying"], "carrying"
    return None, None


def truth_bonds(record: dict) -> list[dict]:
    """Outstanding bonds with a maturity year. Subtotal members (P26) drop out here because they
    carry no maturity (Digital Realty's "Unsecured senior notes"); a size test would be wrong — a
    company can owe one large bond (TeraWulf's $3.2 bn notes are 60% of its debt)."""
    out = []
    for i in record["instruments"]:
        if not i["outstanding"] or i["klass"] != "bond" or not i.get("maturity_year"):
            continue
        p, basis = principal_of(i)
        out.append({"member": i["member"], "currency": i.get("currency") or "USD",
                    # a currency is known only if the label names it or the face is tagged in a foreign
                    # unit; Equinix tags its Swiss franc notes' face *and* carrying amounts in USD
                    "currency_known": i.get("currency_from", "label") == "label"
                                      or (i.get("currency_from") == "face" and i.get("face_uom") not in (None, "USD")),
                    "coupon_pct": i.get("rate"), "maturity_year": i["maturity_year"], "principal": p,
                    "principal_basis": basis, "amount_usd": i.get("amount_usd")})
    return out


def truth_offerings(record: dict) -> list[dict]:
    """Offering members of a report (L2 units without the single bonds)."""
    return [u for u in truth_units(record) if u["maturity_year"] is None]


def offering_amount(inst: dict) -> tuple[float | None, str | None, str]:
    """What is left of an offering: (amount, basis, currency).

    An offering's tagged *face* is often the original deal size, not what is left: Microsoft's 2016
    issuance is tagged $19.8 bn face and $7.93 bn carrying, and the printed table shows $7,930 million
    outstanding (Week 2 hand-check). So the outstanding carrying amount comes first. Used by the key
    and by anything that carries an offering forward, so both sides measure the same thing."""
    if inst.get("carrying"):
        return inst["carrying"], "carrying", inst.get("carrying_uom") or "USD"
    p, basis = principal_of(inst)
    return p, basis, inst.get("currency") or "USD"


def truth_units(record: dict) -> list[dict]:
    """L2 units: offerings plus any single bonds tagged beside them."""
    units = []
    for i in record["instruments"]:
        if not i["outstanding"] or i["klass"] != "offering":
            continue
        p, basis, cur = offering_amount(i)
        if p:
            units.append({"member": i["member"], "currency": cur, "amount": p, "basis": basis,
                          "issued": i.get("issued"), "maturity_year": None})
    for b in truth_bonds(record):
        if b["principal"]:
            units.append({"member": b["member"], "currency": b["currency"], "amount": b["principal"],
                          "basis": b["principal_basis"], "issued": None, "maturity_year": b["maturity_year"]})
    return units


# ------------------------------------------------------------------------------------ matching
def _close(a, b, tol):
    return a is not None and b is not None and abs(a - b) <= tol * max(abs(a), abs(b))


def _bond_cost(t: dict, led: dict) -> float:
    if t.get("currency_known", True) and (t.get("currency") or "USD") != (led.get("currency") or "USD"):
        return BIG
    if not t.get("maturity_year") or t["maturity_year"] != led.get("maturity_year"):
        return BIG
    tr, lr = t.get("coupon_pct"), led.get("coupon_pct")
    if tr is not None and lr is not None:
        if abs(tr - lr) > RATE_TOL:
            return BIG
    elif not _close(t.get("principal"), led.get("principal"), PRINCIPAL_TOL):
        return BIG  # no coupon on one side: identify by maturity + principal instead
    # among compatible pairs prefer the one whose principal also agrees
    return 0.0 if _close(t.get("principal"), led.get("principal"), PRINCIPAL_TOL) else 0.5


def assign(truth: list[dict], ledger: list[dict], cost_fn) -> list[tuple[int, int]]:
    if not truth or not ledger:
        return []
    cost = np.array([[cost_fn(t, l_) for l_ in ledger] for t in truth])
    rows, cols = linear_sum_assignment(cost)
    return [(r, c) for r, c in zip(rows, cols) if cost[r, c] < BIG]


def _period_ok(a: str | None, b: str | None) -> bool:
    return not a or not b or a.startswith(b) or b.startswith(a)


def _unit_cost(t: dict, u: dict) -> float:
    if t["currency"] != u["currency"] or not _close(t["amount"], u["amount"], PRINCIPAL_TOL):
        return BIG
    if not _period_ok(t.get("issued"), u.get("issued")):
        return BIG
    if t.get("maturity_year") and u.get("maturity_year") and t["maturity_year"] != u["maturity_year"]:
        return BIG
    return abs(t["amount"] - u["amount"]) / max(t["amount"], 1)


def ledger_units(ledger: dict) -> list[dict]:
    """Ledger offerings as-is; ledger bonds summed by (issue period, currency) when dated, else
    kept one by one."""
    units, groups = [], {}
    for i in ledger["instruments"]:
        amt = i.get("principal")
        if not amt:
            continue
        cur = i.get("currency") or "USD"
        if i.get("kind") == "offering":
            units.append({"currency": cur, "amount": amt, "issued": i.get("issued"), "maturity_year": None})
        elif i.get("kind") == "bond":
            if i.get("issued"):
                g = groups.setdefault((i["issued"], cur), {"currency": cur, "amount": 0.0, "issued": i["issued"],
                                                           "maturity_year": None})
                g["amount"] += amt
            else:
                units.append({"currency": cur, "amount": amt, "issued": None, "maturity_year": i.get("maturity_year")})
    return units + list(groups.values())


def ledger_totals(ledger: dict) -> dict:
    if ledger.get("totals"):
        return ledger["totals"]
    usd = [i["amount_usd"] for i in ledger["instruments"] if i.get("amount_usd")]
    return {"total_debt": sum(usd)} if usd else {}


def covered_by_offerings(target: dict, unmatched: list[dict], max_size: int = 6) -> int:
    """Unmatched ledger bonds that make up an offering the report tags only as a total.

    Broadcom's April 2025 10-Q tags older bonds one by one but its three newest deals only as
    totals ($5.0 bn, $5.0 bn, $3.0 bn); a ledger that lists those 10 bonds is right, not padded
    (Week 2 hand-check). For each such offering, the smallest set of unmatched bonds in its currency
    whose principals add up to it within 1% is set aside: those bonds are neither matches nor extras.

    Only offerings issued in the 18 months before the report qualify — the case is a *new* deal not
    yet itemised. Without that limit, small leftover bonds can add up to an old deal by coincidence:
    the first version of this rule "covered" seven of Broadcom's assumed VMware notes with 2020-21
    deal totals."""
    from itertools import combinations
    pool = [b for b in unmatched if b.get("principal")]
    covered = 0
    period = int(target["period"][:4]) * 12 + int(target["period"][4:6])

    def recent(off):
        iss = off.get("issued")
        if not iss:
            return False
        m = int(iss[:4]) * 12 + (int(iss[5:7]) if len(iss) >= 7 else 1)
        return 0 <= period - m <= 18

    for off in sorted(filter(recent, truth_offerings(target)), key=lambda u: -u["amount"]):
        cands = [i for i, b in enumerate(pool) if (b.get("currency") or "USD") == off["currency"]]
        hit = None
        for k in range(1, min(max_size, len(cands)) + 1):
            for combo in combinations(cands, k):
                if _close(sum(pool[i]["principal"] for i in combo), off["amount"], PRINCIPAL_TOL):
                    hit = combo
                    break
            if hit:
                break
        if hit:
            covered += len(hit)
            pool = [b for i, b in enumerate(pool) if i not in hit]
    return covered


# ------------------------------------------------------------------------------------ grading
def grade_l1(target: dict, ledger: dict, start: dict | None = None) -> dict:
    truth = truth_bonds(target)
    bonds = [i for i in ledger["instruments"] if i.get("kind") == "bond"]
    pairs = assign(truth, bonds, _bond_cost)
    p_scored = p_ok = p_unstated = 0
    for r, c in pairs:
        tp, lp = truth[r].get("principal"), bonds[c].get("principal")
        if (not truth[r].get("currency_known", True)
                and (truth[r].get("currency") or "USD") != (bonds[c].get("currency") or "USD")):
            continue  # P37: the key's amount may be a dollar translation of a euro face; not comparable
        if tp is not None:
            p_scored += 1
            p_unstated += lp is None
            tol = PRINCIPAL_TOL if truth[r]["principal_basis"] == "face" else CARRYING_TOL
            p_ok += _close(tp, lp, tol)
    matched_truth = {r for r, _ in pairs}
    covered = covered_by_offerings(target, [bonds[c] for c in range(len(bonds)) if c not in {c_ for _, c_ in pairs}])
    out = {"truth": len(truth), "ledger": len(bonds), "matched": len(pairs),
           "principal_scored": p_scored, "principal_ok": p_ok, "principal_unstated": p_unstated,
           "covered_by_offering": covered,
           "missed": [truth[r]["member"] for r in range(len(truth)) if r not in matched_truth],
           "extra": len(bonds) - len(pairs) - covered}
    if start is not None:
        prev = truth_bonds(start)
        carried = {r for r, _ in assign(truth, prev, _bond_cost)}
        added = [r for r in range(len(truth)) if r not in carried]
        kept = {c for _, c in assign(truth, prev, _bond_cost)}
        removed = [c for c in range(len(prev)) if c not in kept]
        still_in_ledger = {r for r, _ in assign(prev, bonds, _bond_cost)}
        out.update({"added": len(added), "added_caught": sum(r in matched_truth for r in added),
                    "removed": len(removed), "removed_caught": sum(c not in still_in_ledger for c in removed)})
    return out


def grade_l2(target: dict, ledger: dict) -> dict:
    truth = truth_units(target)
    units = ledger_units(ledger)
    pairs = assign(truth, units, _unit_cost)
    return {"truth": len(truth), "ledger": len(units), "matched": len(pairs),
            "missed": [truth[r]["member"] for r in range(len(truth)) if r not in {r_ for r_, _ in pairs}]}


def grade_l3(target: dict, ledger: dict) -> dict:
    truth, led = truth_totals(target), ledger_totals(ledger)
    out = {}
    for k, v in truth.items():
        lv = led.get(k)
        out[k] = {"truth": v, "ledger": lv, "ok": _close(v, lv, TOTAL_TOL) if lv is not None else False,
                  "error_pct": round(100 * (lv - v) / v, 2) if lv is not None and v else None}
    return out


def grade_episode(target: dict, ledger: dict, level: str, start: dict | None = None) -> dict:
    out = {"level": level, "l3": grade_l3(target, ledger)}
    if level == "L1":
        out["l1"] = grade_l1(target, ledger, start)
    elif level == "L2":
        out["l2"] = grade_l2(target, ledger)
    return out


# ------------------------------------------------------------------------------------ aggregation
def _ratio_ci(num: np.ndarray, den: np.ndarray, n_boot: int = 2000, seed: int = 0) -> tuple[float, float, float]:
    """Ratio of sums with a 95% bootstrap interval over episodes (§9.5)."""
    if den.sum() == 0:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(num), size=(n_boot, len(num)))
    with np.errstate(invalid="ignore", divide="ignore"):
        boots = num[idx].sum(1) / den[idx].sum(1)
    boots = boots[~np.isnan(boots)]
    return float(num.sum() / den.sum()), float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def summarise(results: list[dict]) -> dict:
    """Micro-averaged metrics with bootstrap intervals, per level."""
    out = {"episodes": len(results)}
    l1 = [r["l1"] for r in results if "l1" in r]
    if l1:
        a = lambda k: np.array([x.get(k, 0) for x in l1], dtype=float)  # noqa: E731
        claimed = a("ledger") - a("covered_by_offering")   # bonds a report's offering totals vouch for are not extras
        out["l1"] = {"episodes": len(l1), "truth": int(a("truth").sum()), "ledger": int(a("ledger").sum()),
                     "matched": int(a("matched").sum()), "covered_by_offering": int(a("covered_by_offering").sum()),
                     "recall": _ratio_ci(a("matched"), a("truth")), "precision": _ratio_ci(a("matched"), claimed),
                     "principal_accuracy": _ratio_ci(a("principal_ok"), a("principal_scored")),
                     "exact_episodes": int(sum(x["matched"] == x["truth"] and x["extra"] == 0 for x in l1))}
        ch = [x for x in l1 if "added" in x]
        if ch:
            b = lambda k: np.array([x[k] for x in ch], dtype=float)  # noqa: E731
            out["l1"]["changes"] = {"episodes": len(ch), "added": int(b("added").sum()), "removed": int(b("removed").sum()),
                                    "added_recall": _ratio_ci(b("added_caught"), b("added")),
                                    "removed_recall": _ratio_ci(b("removed_caught"), b("removed")),
                                    "episodes_with_change": int(sum((x["added"] + x["removed"]) > 0 for x in ch))}
    l2 = [r["l2"] for r in results if "l2" in r]
    if l2:
        a = lambda k: np.array([x[k] for x in l2], dtype=float)  # noqa: E731
        out["l2"] = {"episodes": len(l2), "truth": int(a("truth").sum()),
                     "recall": _ratio_ci(a("matched"), a("truth")), "precision": _ratio_ci(a("matched"), a("ledger"))}
    l3 = {}
    for r in results:
        for k, v in r["l3"].items():
            s = l3.setdefault(k, {"graded": 0, "ok": 0, "not_provided": 0, "abs_err": []})
            s["graded"] += 1
            s["ok"] += bool(v["ok"])
            if v["ledger"] is None:
                s["not_provided"] += 1        # the tracker gave no figure: a miss, but not a wrong number
            if v["error_pct"] is not None:
                s["abs_err"].append(abs(v["error_pct"]))
    out["l3"] = {k: {"graded": s["graded"], "within_2pct": s["ok"], "not_provided": s["not_provided"],
                     "median_abs_error_pct": float(np.median(s["abs_err"])) if s["abs_err"] else None}
                 for k, s in l3.items()}
    return out
