"""Week 2: which debt changes were announced? — Week 0's F2 check, with a proper method for removals.

Week 0 searched each filing in the window for a vanished bond's coupon and called the removal
"announced" if the word "redeem" (or similar) appeared *anywhere* in the document — which also
matches new-issue prospectuses that merely mention redemption terms. This replaces it:

* **Changes come from the grader**, not from member names: for every dev episode graded L1 whose
  start report is itemised too, a bond is *added* if it has no match in the start report and
  *removed* if it has no match in the target (the same one-to-one assignment the grader uses).
* **Documents come through `edgar_pit`**, at the episode's cut-off (pinned to the target report,
  P29): 8-K bodies and EX-99 press releases, 424B2/424B5 prospectuses and FWP term sheets, from 30
  days before the start period to the cut-off — exactly what the agent could read.
* **A bond is named** when its coupon and maturity year appear within 300 characters.
* **An exit is announced** only when an exit word (redeem, repurchase, tender, repay, retire,
  exchange, convert, called) appears within 400 characters of that naming — not anywhere.
* **Scheduled maturities** need no announcement (P10's "it just disappears"): a removed bond
  whose maturity year is the target's year or earlier is classed as matured.

Every change gets one class; the counts are the *unannounced debt* finding of P10. Outputs
`$AI_DEBT_DATA/week2/changes_dev.json` and docs/changes_dev.md.

Usage:  python scripts/explain_changes.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

from ai_debt_tracker import config
from ai_debt_tracker.eval.answer_key import AnswerKey, grading_level
from ai_debt_tracker.eval.grader import _bond_cost, assign, truth_bonds
from ai_debt_tracker.mcp_servers.edgar_pit_core import PointInTimeEdgar, Refused
from review_universe import extracted_periods

ROOT = Path(__file__).resolve().parents[1]
FORMS = ["8-K", "8-K/A", "424B2", "424B5", "FWP"]
EXIT = re.compile(r"redeem|redemption|repurchas|tender|repa(y|id|yment)|retire|exchang|conver|called|prepa(y|id)|"
                  r"extinguish|settle", re.I)
READ_CHARS = 60_000


def rate_strings(rate: float) -> list[str]:
    """Every way a filing may print this coupon. The key can hold a rounded value (P17: 3.625% is
    stored as 3.62 or 3.63), so every three-decimal coupon that rounds to it is tried too — the first
    run of this script called four announced changes "unannounced" for want of exactly this."""
    cands = {round(rate, 3)} | {round(rate + k / 1000, 3) for k in range(-5, 6) if round(rate + k / 1000, 2) == round(rate, 2)}
    s = set()
    for x in cands:
        if x <= 0 and rate > 0:
            continue
        for v in (f"{x:.3f}", f"{x:.2f}" if round(x, 2) == x else None, f"{x:g}"):
            if v:
                s |= {v + "%", v + " %"}
    return sorted(s, key=len, reverse=True)


def mentions(text: str, rate: float, year: int):
    """Positions where the bond is named: its coupon with its maturity year within 300 characters.
    The coupon must start a number — "0%" inside "20%" is not a 0% coupon (P40: Week 3's triage check
    found a 0% 2031 convertible credited to an earnings release whose lease table says "escalates 20%"
    near "Nov 2031")."""
    for rs in rate_strings(rate):
        for m in re.finditer(r"(?<![\d.,])" + re.escape(rs), text):
            if str(year) in text[max(0, m.start() - 300): m.end() + 300]:
                yield m.start()


def documents(pit: PointInTimeEdgar, cik: int, start: str, end: str):
    for f in pit.timeline(cik, start, end, FORMS):
        try:
            for d in pit.exhibits(cik, f["accession"]):
                t = d["type"].upper()
                main = t == f["form"] or t.startswith("424B") or t == "FWP" or t.startswith("8-K")
                if (main or t.startswith("EX-99")) and d["document"].lower().endswith((".htm", ".html", ".txt")):
                    yield f, pit.fetch(cik, f["accession"], d["document"], 0, READ_CHARS)["text"]
        except Refused:
            continue
        except Exception as ex:  # noqa: BLE001 — a document that will not load is counted, not fatal
            print("   fetch failed", f["accession"], type(ex).__name__, file=sys.stderr)


def family(form: str) -> str:
    return "FWP" if form == "FWP" else "424B" if form.startswith("424B") else "8-K"


def main() -> int:
    with open(ROOT / "manifests" / "dev.csv", encoding="utf-8") as fh:
        eps = [e for e in csv.DictReader(line for line in fh if not line.startswith("#")) if e["graded_level"] == "L1"]
    ak = AnswerKey(extracted_periods(), {int(e["cik"]) for e in eps})
    log = config.data_dir() / "logs" / "edgar_pit_changes.jsonl"
    rows, tally = [], Counter()
    for e in eps:
        cik = int(e["cik"])
        start, target = ak.filing_record(e["start_adsh"]), ak.filing_record(e["target_adsh"])
        if grading_level(start)["level"] != "L1":
            continue
        prev, now = truth_bonds(start), truth_bonds(target)
        pairs = assign(now, prev, _bond_cost)
        added = [now[r] for r in range(len(now)) if r not in {r_ for r_, _ in pairs}]
        removed = [prev[c] for c in range(len(prev)) if c not in {c_ for _, c_ in pairs}]
        if not added and not removed:
            continue
        pit = PointInTimeEdgar.for_episode(cik, e["target_adsh"], log_path=log)
        docs = list(documents(pit, cik, e["window_open"], pit.cutoff_date))
        target_year = int(e["target_period"][:4])
        for kind, bonds in (("added", added), ("removed", removed)):
            for b in bonds:
                cls, where = None, None
                if kind == "removed" and b["maturity_year"] <= target_year:
                    cls = "matured (scheduled)"
                elif b["coupon_pct"] is None:
                    cls = "no coupon to search for"
                else:
                    for f, text in docs:
                        for pos in mentions(text, b["coupon_pct"], b["maturity_year"]):
                            if kind == "added" or EXIT.search(text[max(0, pos - 400): pos + 400]):
                                cls, where = f"announced ({family(f['form'])})", f["accession"]
                                break
                        if cls:
                            break
                    cls = cls or "unannounced"
                tally[(kind, cls)] += 1
                rows.append({"episode": e["episode_id"], "company": e["company"], "change": kind, "class": cls,
                             "member": b["member"], "coupon_pct": b["coupon_pct"], "maturity_year": b["maturity_year"],
                             "principal": b["principal"], "document": where})
        print(f"{e['episode_id']:22s} {e['company'][:16]:16s} +{len(added):2d} -{len(removed):2d}  docs {len(docs)}", flush=True)
    out = config.data_dir() / "week2"
    out.mkdir(parents=True, exist_ok=True)
    (out / "changes_dev.json").write_text(json.dumps(rows, indent=1, default=str))
    write_doc(rows, tally)
    for k, v in sorted(tally.items()):
        print(k, v)
    return 0


def write_doc(rows, tally):
    add = [r for r in rows if r["change"] == "added"]
    rem = [r for r in rows if r["change"] == "removed"]
    add_ann = sum(r["class"].startswith("announced") for r in add)
    add_searchable = sum(r["class"] != "no coupon to search for" for r in add)
    rem_sched = sum(r["class"].startswith("matured") for r in rem)
    rem_ann = sum(r["class"].startswith("announced") for r in rem)
    rem_left = len(rem) - rem_sched
    rem_searchable = sum(r["class"] not in ("no coupon to search for",) and not r["class"].startswith("matured") for r in rem)
    usd = lambda rs: sum(r["principal"] or 0 for r in rs) / 1e9  # noqa: E731
    L = ["# Which debt changes were announced? — dev split\n",
         "> Generated by `scripts/explain_changes.py`. Every change: `$AI_DEBT_DATA/week2/changes_dev.json`; every "
         "document read is in `$AI_DEBT_DATA/logs/edgar_pit_changes.jsonl`. This replaces Week 0's keyword check "
         "for removals (see the script's docstring).\n",
         "## Results\n",
         f"Dev episodes graded per bond whose start report is itemised too, with at least one change.\n",
         f"**New bonds: {add_ann} of {add_searchable} announced** ({add_ann / max(add_searchable, 1):.0%}) in a filing the "
         f"agent could read before the report; {add_searchable - add_ann} unannounced "
         f"(${usd([r for r in add if r['class'] == 'unannounced']):.1f} bn)"
         + (f"; {len(add) - add_searchable} without a tagged coupon to search for" if len(add) > add_searchable else "") + ".\n",
         f"**Removed bonds: {len(rem)}** — {rem_sched} reached their scheduled maturity (no announcement needed); "
         f"of the other {rem_left}, **{rem_ann} of {rem_searchable} announced** as a redemption, repurchase, tender, "
         f"exchange or conversion.\n",
         "| Change | Class | Bonds |", "|---|---|---|"]
    L += [f"| {k[0]} | {k[1]} | {v} |" for k, v in sorted(tally.items())]
    L += ["\n## Unexplained changes\n",
          "Each is either debt never announced in a document the agent can see (P10 — a finding about the data), or a "
          "change announced in a form this search does not read (an exhibit, a 10-Q, a subsidiary's filing).\n",
          "| Episode | Company | Change | Bond | Principal $m |", "|---|---|---|---|---|"]
    for r in rows:
        if r["class"] == "unannounced":
            L.append(f"| {r['episode']} | {r['company']} | {r['change']} | {r['coupon_pct']}% {r['maturity_year']} | "
                     f"{(r['principal'] or 0) / 1e6:,.0f} |")
    L += ["\n## Comparison with Week 0\n",
          "Week 0 (test-window episodes, keyword method): 56 of 64 genuinely new bonds announced (87.5%); removals "
          "\"noisy\". This run is on the dev split, with changes taken from the grader and exits required next to the "
          "bond, so the two are not the same population; the method, not the number, is what changed.\n"]
    (ROOT / "docs" / "changes_dev.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
