"""Week 6: score the three runs of `scripts/run_week6.py` and B0 on the same dev episodes → docs/agent_start.md.

The grader is Week 2's, with this week's two answer-key/grader fixes (P47: a convertible-only filer's total; P49: no
maturity ladder graded on 10-Q targets), applied to every row below — B0 and Week 5's run are re-graded with them, so
the rows compare like with like. Week 5's run is read from `$AI_DEBT_DATA/week5/episodes/` as it was saved.

Self-catch rate (DESIGN.md §9.2): of the episodes that ended wrong, how many the self-checks flagged. An episode
"ended wrong" when its graded ledger is not exact — at L1, a true bond missed or a bond claimed that is not there;
at L2/L3, total debt off by more than 2% (where the report tags one). "Flagged" means a check failed or a question
was still open when the episode ended.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from ai_debt_tracker import config
from ai_debt_tracker.eval.answer_key import AnswerKey, grading_level
from ai_debt_tracker.eval.baselines.carry_forward import carry_forward
from ai_debt_tracker.eval.grader import _bond_cost, assign, grade_episode, summarise, truth_bonds
from episodes_report import _paired, pct
from review_universe import extracted_periods


def pts(d) -> str:
    """A paired difference of two fractions, in percentage points with its interval."""
    return f"{d[0] * 100:+.1f} points ({d[1] * 100:+.1f} to {d[2] * 100:+.1f})"

ROOT = Path(__file__).resolve().parents[1]
D = config.data_dir()
RUNS = {"week5": D / "week5" / "episodes", "oracle_noinv": D / "week6" / "episodes_oracle_noinv",
        "oracle_inv": D / "week6" / "episodes_oracle_inv", "agent_inv": D / "week6" / "episodes_agent_inv"}
NAMES = {"week5": "Week 5's run (as saved)", "oracle_noinv": "Oracle start, merge fixes, no investigators",
         "oracle_inv": "Oracle start + investigators", "agent_inv": "**Agent start** + investigators", "b0": "B0 (carry forward)"}


def manifest() -> dict:
    with open(ROOT / "manifests" / "dev.csv", encoding="utf-8") as f:
        return {e["episode_id"]: e for e in csv.DictReader(line for line in f if not line.startswith("#"))
                if e["universe"] == "ai25"}


class Records:
    def __init__(self, ciks):
        self.ak = AnswerKey(extracted_periods(), set(ciks))
        self.cache = {}

    def __call__(self, adsh):
        if adsh not in self.cache:
            self.cache[adsh] = self.ak.filing_record(adsh)
        return self.cache[adsh]


def load(run: str) -> dict:
    d = RUNS[run]
    return {json.loads(p.read_text(encoding="utf-8"))["episode"]: json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(d.glob("*.json"))} if d.exists() else {}


def grade_all(runs: dict, man: dict, rec) -> dict:
    """{run: {episode: grade}}, plus B0 (rebuilt from the same opening report, as in Week 5)."""
    out = {k: {} for k in list(runs) + ["b0"]}
    some = next(iter(runs.values()))
    for ep in sorted(some):
        e = man[ep]
        target, start = rec(e["target_adsh"]), rec(e["start_adsh"])
        start_ch = start if grading_level(start)["level"] == "L1" else None
        for k, rr in runs.items():
            if ep in rr:
                out[k][ep] = grade_episode(target, rr[ep]["ledger"], e["graded_level"], start_ch)
        base = carry_forward(rec(some[ep]["opening"]["adsh"]), e["target_period"])
        out["b0"][ep] = grade_episode(target, base, e["graded_level"], start_ch)
    return out


def wrong(g: dict) -> bool | None:
    if "l1" in g:
        return bool(g["l1"]["missed"]) or g["l1"]["extra"] > 0
    t = g["l3"].get("total_debt")
    return None if t is None else not t["ok"]


def flagged(r: dict) -> bool:
    return bool(r["checks"]["flags"]) or bool(r["checks"]["questions"])


def additions(r: dict, target: dict) -> list[tuple[dict, bool]]:
    bonds = [i for i in r["ledger"]["instruments"] if i.get("kind") == "bond"]
    cols = {c for _, c in assign(truth_bonds(target), bonds, _bond_cost)}
    return [(i, k in cols) for k, i in enumerate(bonds) if str(i.get("id", "")).startswith("new-")]


def l1_pair(ga: dict, gb: dict):
    eps = [ep for ep in ga if "l1" in ga[ep] and ep in gb and "l1" in gb[ep]]
    cl = lambda x: x["l1"]["ledger"] - x["l1"]["covered_by_offering"] - x["l1"].get("covered_by_unkeyed", 0)  # noqa: E731
    rec = _paired([ga[e]["l1"]["matched"] for e in eps], [ga[e]["l1"]["truth"] for e in eps],
                  [gb[e]["l1"]["matched"] for e in eps], [gb[e]["l1"]["truth"] for e in eps])
    pre = _paired([ga[e]["l1"]["matched"] for e in eps], [cl(ga[e]) for e in eps],
                  [gb[e]["l1"]["matched"] for e in eps], [cl(gb[e]) for e in eps])
    return rec, pre


def score() -> int:
    man = manifest()
    runs = {k: load(k) for k in RUNS}
    runs = {k: v for k, v in runs.items() if v}
    rec = Records({int(e["cik"]) for e in man.values()})
    grades = grade_all(runs, man, rec)
    sums = {k: summarise(list(v.values())) for k, v in grades.items()}
    write(runs, grades, sums, man, rec)
    print(json.dumps({k: {kk: vv for kk, vv in s.get("l1", {}).items() if kk in ("recall", "precision", "changes")}
                      for k, s in sums.items()}, indent=1, default=str)[:3500])
    return 0


# ------------------------------------------------------------------------------------ the report
def _l1_row(name, s):
    l1 = s.get("l1", {})
    ch = l1.get("changes", {})
    new = f"{round(ch['added_recall'][0] * ch['added'])} of {ch['added']}" if ch else "—"
    gone = f"{round(ch['removed_recall'][0] * ch['removed'])} of {ch['removed']}" if ch else "—"
    return (f"| {name} | {pct(l1['recall'])} | {pct(l1['precision'])} | {pct(l1['principal_accuracy'])} | "
            f"{l1['exact_episodes']} of {l1['episodes']} | {new} | {gone} |")


def _total_ok(g: dict) -> tuple[int, int]:
    t = [x["l3"]["total_debt"] for x in g.values() if "total_debt" in x["l3"]]
    return sum(v["ok"] for v in t), len(t)


def _selfcatch(run: dict, grades: dict) -> dict:
    w = [ep for ep, g in grades.items() if wrong(g)]
    r = [ep for ep, g in grades.items() if wrong(g) is False]
    return {"wrong": len(w), "caught": sum(flagged(run[ep]) for ep in w), "right": len(r),
            "alarms": sum(flagged(run[ep]) for ep in r)}


def _unannounced(run: dict, grades: dict, man: dict, rec) -> dict:
    """Of the bonds added in L1 change episodes, which the tracker caught, and the Week 2 class of each it missed."""
    changes = json.loads((D / "week2" / "changes_dev.json").read_text(encoding="utf-8"))
    cls = {(c["episode"], c.get("coupon_pct"), c.get("maturity_year")): c["class"] for c in changes if c["change"] == "added"}
    out = Counter()
    rows = []
    for ep, g in grades.items():
        if "l1" not in g or "added" not in g["l1"]:
            continue
        e = man[ep]
        target, start = rec(e["target_adsh"]), rec(e["start_adsh"])
        truth, prev = truth_bonds(target), truth_bonds(start)
        carried = {r for r, _ in assign(truth, prev, _bond_cost)}
        bonds = [i for i in run[ep]["ledger"]["instruments"] if i.get("kind") == "bond"]
        matched = {r for r, _ in assign(truth, bonds, _bond_cost)}
        for k, t in enumerate(truth):
            if k in carried:
                continue
            c = cls.get((ep, t.get("coupon_pct"), t.get("maturity_year")), "not in Week 2's search")
            kind = "unannounced" if c == "unannounced" else "no coupon to search for" if c.startswith("no coupon") \
                else "announced" if c.startswith("announced") else c
            out[("caught" if k in matched else "missed", kind)] += 1
            if k not in matched:
                rows.append((man[ep]["company"], ep, t, kind))
    return {"counts": out, "missed": rows}


def _hard_cases(run: dict, grades: dict, man: dict, rec) -> Counter:
    """L1 misses and extras by kind of bond: foreign currency, no tagged coupon (floating or not stated), convertible."""
    c = Counter()
    for ep, g in grades.items():
        if "l1" not in g:
            continue
        target = rec(man[ep]["target_adsh"])
        truth = {t["member"]: t for t in truth_bonds(target)}
        for m in g["l1"]["missed"]:
            t = truth.get(m, {})
            kinds = []
            if (t.get("currency") or "USD") != "USD":
                kinds.append("foreign currency")
            if t.get("coupon_pct") is None:
                kinds.append("no coupon tagged")
            if "convertible" in m.lower():
                kinds.append("convertible")
            c[("missed", " + ".join(kinds) or "plain fixed-rate USD")] += 1
    return c


def write(runs, grades, sums, man, rec):
    a4 = "agent_inv" in grades and "oracle_inv" in grades
    L = ["# Agent start, investigators and the merge fixes — week 6\n",
         "> Generated by `scripts/run_week6.py score` (`scripts/week6_report.py`). Runs: `$AI_DEBT_DATA/week6/episodes_*`; "
         "the opening-ledger reader on its own: [`opening_reader.md`](opening_reader.md); Week 5's run: "
         "[`episodes.md`](episodes.md). Intervals are 95% bootstrap over episodes; differences are paired (the same "
         "resampled episodes on both sides).\n",
         "## The week 6 check\n"]
    if a4:
        rec_d, pre_d = l1_pair(grades["agent_inv"], grades["oracle_inv"])
        sa, so = sums["agent_inv"]["l1"], sums["oracle_inv"]["l1"]
        sc = {k: _selfcatch(runs[k], grades[k]) for k in ("oracle_inv", "agent_inv") if k in runs}
        L += [f"DESIGN.md §11 asks for two measurements: **the agent-start vs oracle-start gap** (ablation A4) and **the "
              "self-catch rate**. Both are below.\n",
              f"- **A4 — reading the opening ledger instead of borrowing it** moves L1 recall by **{pts(rec_d)}** "
              f"(agent {pct(sa['recall'])} vs oracle {pct(so['recall'])}) and precision by **{pts(pre_d)}** (agent "
              f"{pct(sa['precision'])} vs oracle {pct(so['precision'])}), paired on the same {sa['episodes']} L1 "
              "episodes. Recall falls because bonds the reader misses in the opening report are never in the ledger; "
              "precision rises for the same reason: fewer bonds held, fewer held wrongly.",
              f"- **Self-catch rate:** of the {sc['agent_inv']['wrong']} agent-start episodes that ended wrong, the checks "
              f"flagged **{sc['agent_inv']['caught']}** ({sc['agent_inv']['caught'] / max(sc['agent_inv']['wrong'], 1):.0%}); "
              f"they also flagged {sc['agent_inv']['alarms']} of the {sc['agent_inv']['right']} that ended right. Oracle "
              f"start: {sc['oracle_inv']['caught']} of {sc['oracle_inv']['wrong']} wrong flagged, "
              f"{sc['oracle_inv']['alarms']} of {sc['oracle_inv']['right']} right.\n"]
    L += ["## L1 — per bond, every run on the same episodes\n",
          "| Run | Recall | Precision | Principal right | Exact | New bonds caught | Removed caught |",
          "|---|---|---|---|---|---|---|"]
    for k in ("week5", "oracle_noinv", "oracle_inv", "agent_inv", "b0"):
        if k in sums and sums[k].get("l1"):
            L.append(_l1_row(NAMES[k], sums[k]))
    L.append("")
    if "oracle_inv" in grades:
        d = l1_pair(grades["oracle_inv"], grades["b0"])
        L.append(f"Oracle start + investigators against B0, paired: recall {pts(d[0])}, precision {pts(d[1])}.")
    if a4:
        d = l1_pair(grades["agent_inv"], grades["b0"])
        L.append(f"Agent start + investigators against B0, paired: recall {pts(d[0])}, precision {pts(d[1])}. B0 still "
                 "opens from the answer key; the agent does not.\n")
        L.append("*Removed caught* counts bonds of the start report that are gone from the target report and are not in "
                 "the tracker's ledger at the end. At agent start that includes bonds the opening-ledger reader never "
                 "read, so the agent's higher count does not by itself show repayments found.")
    L.append("")
    L += ["| Run | L2 offering recall | L2 precision | Total debt within 2% |", "|---|---|---|---|"]
    for k in ("week5", "oracle_noinv", "oracle_inv", "agent_inv", "b0"):
        if k in sums:
            l2 = sums[k].get("l2")
            ok, n = _total_ok(grades[k])
            L.append(f"| {NAMES[k]} | {pct(l2['recall']) if l2 else '—'} | {pct(l2['precision']) if l2 else '—'} | {ok} of {n} |")
    L.append("\nAll rows are graded with this week's P47 and P49 fixes, so Week 5's and B0's rows differ slightly from "
             "the numbers recorded last week ([`episodes.md`](episodes.md), [`baseline_b0.md`](baseline_b0.md)).\n")

    # ---- the merge fixes
    if "oracle_noinv" in runs:
        add_now, add_then = [], []
        for ep, r in runs["oracle_noinv"].items():
            if man[ep]["graded_level"] == "L1":
                add_now += additions(r, rec(man[ep]["target_adsh"]))
        if "week5" in runs:
            for ep, r in runs["week5"].items():
                if man[ep]["graded_level"] == "L1":
                    add_then += additions(r, rec(man[ep]["target_adsh"]))
        lg = Counter(c["change"] for r in runs["oracle_noinv"].values() for c in r["ledger"]["meta"]["log"])
        folded = sum(len(r["ledger"]["meta"].get("launches_folded", [])) for r in runs["oracle_noinv"].values())
        qs = Counter(q["type"] for r in runs["oracle_noinv"].values() for q in r["checks"]["questions"])
        L += ["## The merge fixes (P56–P58) — oracle start, no investigators\n",
              f"Week 5 added {len(add_then)} bonds in L1 episodes, {sum(ok for _, ok in add_then)} of them real. With the "
              f"three fixes the same readings add **{len(add_now)}**, **{sum(ok for _, ok in add_now)}** real and "
              f"**{len(add_now) - sum(ok for _, ok in add_now)}** not.",
              f"- **P57**, launches folded into the priced bond that followed: {folded}; launches with no pricing in the "
              f"window, held as questions: {qs.get('launch_not_priced', 0)}.",
              f"- **P56**, bonds named with no amount, held as questions instead of added: {qs.get('new_without_amount', 0)}.",
              f"- **P58**, the banks' option, recorded and not added: {lg.get('option, not a bond (P58)', 0)}.",
              f"- **Loans** (capacity vs drawn): {lg.get('loan drawn (in total debt)', 0)} draws added to total debt, "
              f"{lg.get('facility added (commitment; not in total debt)', 0)} new commitments kept out of it, "
              f"{lg.get('loan repaid (total debt)', 0)} loan repayments taken off it.\n"]
        bad = [(i, ok) for i, ok in add_now if not ok]
        if bad:
            L.append("The additions that are still not in the target report:\n")
            for i, _ in bad:
                accs = sorted({s["accession"] for ev in i.get("events", []) for s in ev.get("sources", [])})
                p = f"{i.get('currency')} {i['principal'] / 1e6:,.0f} m" if i.get("principal") else "amount not read"
                L.append(f"- {i.get('coupon_pct')}% {i.get('maturity_year')}, {p} — read from {', '.join(accs[:3])}")
            L.append("")

    # ---- investigators
    if "oracle_inv" in runs:
        for k in ("oracle_inv", "agent_inv"):
            if k not in runs:
                continue
            fs = [f for r in runs[k].values() for f in r.get("findings", [])]
            by = defaultdict(Counter)
            for f in fs:
                res = f.get("resolution") or ""
                by[f["type"]]["open" if res.startswith("open") else "settled"] += 1
            left = Counter(q["type"] for r in runs[k].values() for q in r["checks"]["questions"])
            rounds = Counter(r.get("rounds", 0) for r in runs[k].values())
            secs = sum(f.get("seconds") or 0 for f in fs)
            L += [f"## Investigators — {NAMES[k].replace('**', '')}\n" if k == "agent_inv" else "## Investigators (ablation A1)\n",
                  f"{len(fs)} questions investigated across {sum(1 for r in runs[k].values() if r.get('findings'))} "
                  f"episodes; rounds used: " + ", ".join(f"{n} in {c} episodes" for n, c in sorted(rounds.items()))
                  + f". {sum(f.get('model_judgment', False) for f in fs)} answers used the model "
                  f"({secs / 60:.1f} minutes); the rest were settled by code against the ledger.\n",
                  "| Question | Investigated | Settled | Left open |", "|---|---|---|---|"]
            for t in sorted(by):
                L.append(f"| {t} | {sum(by[t].values())} | {by[t]['settled']} | {by[t]['open']} |")
            L.append(f"\nOpen at the end of the episodes: " + (", ".join(f"{t} {n}" for t, n in left.most_common()) or "none") + ".")
            res = Counter((f["type"], (f.get("resolution") or "")[:60]) for f in fs)
            L.append("\nWhat they found: " + "; ".join(f"{t}: {r} ({n})" for (t, r), n in res.most_common(12)) + ".\n")
        if "oracle_noinv" in grades:
            d = l1_pair(grades["oracle_inv"], grades["oracle_noinv"])
            L.append(f"**A1 — what the investigators changed** (oracle start, with vs without, paired): recall "
                     f"{pts(d[0])}, precision {pts(d[1])}. Most of what they settled was a bond named with no amount, "
                     "which the merge step had already kept out of the ledger (P56): dropping it confirms the ledger "
                     "rather than changing it. Every maturity question stayed open: the passages the model named gave "
                     "no due date, or no passage named the bond.\n")

    # ---- agent start detail
    if a4:
        ag = runs["agent_inv"]
        n_read = Counter(len(r.get("opening_ledger") or []) > 0 for r in ag.values())
        L += ["## Agent start: where the gap comes from\n",
              f"The opening-ledger reader read an opening ledger for {n_read[True]} of {len(ag)} episodes "
              f"(for {n_read[False]} it found no debt table or no instrument row). Its accuracy against the report it read is in "
              "[`opening_reader.md`](opening_reader.md). Episode by episode, L1:\n",
              "| Episode | Company | True | Agent matched / extra | Oracle matched / extra | Opening read |", "|---|---|---|---|---|---|"]
        for ep in sorted(ag):
            ga, go = grades["agent_inv"][ep], grades["oracle_inv"].get(ep, {})
            if "l1" not in ga or "l1" not in go:
                continue
            a, o = ga["l1"], go["l1"]
            if (a["matched"], a["extra"]) == (o["matched"], o["extra"]):
                continue
            L.append(f"| {ep} | {man[ep]['company']} | {a['truth']} | {a['matched']} / {a['extra']} | {o['matched']} / "
                     f"{o['extra']} | {len(ag[ep].get('opening_ledger') or [])} instruments |")
        L.append("\n(Episodes where both starts end the same are left out.)\n")

    # ---- self-catch
    if "oracle_inv" in runs:
        L += ["## Self-catch rate\n", "| Run | Ended wrong | Flagged | Ended right | Flagged anyway |", "|---|---|---|---|---|"]
        for k in ("oracle_noinv", "oracle_inv", "agent_inv"):
            if k in runs:
                s = _selfcatch(runs[k], grades[k])
                L.append(f"| {NAMES[k]} | {s['wrong']} | **{s['caught']}** ({s['caught'] / max(s['wrong'], 1):.0%}) | "
                         f"{s['right']} | {s['alarms']} |")
        flags = Counter(f["check"] for r in runs["oracle_inv"].values() for f in r["checks"]["flags"])
        L.append("\nFlags raised (oracle start + investigators): " + (", ".join(f"{k} {v}" for k, v in flags.most_common()) or "none")
                 + ". A flag is a report for a person, not a verdict; an episode can end wrong in a way no check can see "
                 "(a bond the filings never mention).\n")

    # ---- unannounced
    k = "agent_inv" if a4 else "oracle_inv" if "oracle_inv" in runs else None
    if k:
        u = _unannounced(runs["oracle_inv"] if "oracle_inv" in runs else runs[k], grades["oracle_inv"] if "oracle_inv" in grades else grades[k], man, rec)
        c = u["counts"]
        tot = sum(c.values())
        un = sum(v for (s, kind), v in c.items() if kind == "unannounced")
        L += ["## Unannounced debt (P10)\n",
              f"Of the {tot} bonds that are new in the L1 change episodes' target reports, Week 2's search found "
              f"**{un} never announced** in any filing the agent could read ({un / max(tot, 1):.0%}) — a data finding, not "
              "an agent error. The tracker (oracle start + investigators):\n",
              "| | Announced | Unannounced | No coupon to search for | Other |", "|---|---|---|---|---|"]
        for s in ("caught", "missed"):
            L.append(f"| {s} | {c[(s, 'announced')]} | {c[(s, 'unannounced')]} | {c[(s, 'no coupon to search for')]} | "
                     f"{sum(v for (ss, kind), v in c.items() if ss == s and kind not in ('announced', 'unannounced', 'no coupon to search for'))} |")
        if u["missed"]:
            L.append("\nMissed:\n")
            for comp, ep, t, kind in u["missed"]:
                L.append(f"- {comp} {ep}: {t.get('currency')} {t.get('coupon_pct')}% {t.get('maturity_year')} — {kind}")
        L.append("")

    # ---- hard cases
    if "oracle_inv" in runs:
        L += ["## Hard cases: what the misses are\n", "| Run | " + " | ".join(
            ("plain fixed-rate USD", "foreign currency", "no coupon tagged", "convertible")) + " |", "|---|---|---|---|---|"]
        for k in ("oracle_inv", "agent_inv"):
            if k in runs:
                hc = _hard_cases(runs[k], grades[k], man, rec)
                cell = lambda name: sum(v for (s, kinds), v in hc.items() if name in kinds)  # noqa: E731
                L.append(f"| {NAMES[k]} (L1 bonds missed) | {cell('plain')} | {cell('foreign')} | {cell('no coupon')} | {cell('convertible')} |")
        L.append("\nA bond can be in more than one column. Foreign-currency changes still move no dollar total: there is "
                 "no exchange rate in the point-in-time data.\n")

    # ---- cost
    for k in ("oracle_inv", "agent_inv"):
        if k in runs:
            wall = sum(r["wall_seconds"] for r in runs[k].values())
            L.append(f"- **{NAMES[k].replace('**', '')}:** {wall / 60:.1f} minutes of wall time for {len(runs[k])} episodes "
                     "(readings and opening readings reused; investigators run live).")
    L += ["\n## Who decided what\n",
          "Which filings are about debt, what each announces, which table rows are instruments and which passage states a "
          "missing value are `qwen3:4b`'s judgments (P8), flagged in every record. Every number in a ledger was parsed by "
          "code from a cited passage, table cell or ledger row. The merge, the sweep, the ledger, the checks and the "
          "investigators' ledger matching are code. The diagnosis of the remaining false additions is Claude's reading, a "
          "judgment. Nothing here has been reviewed by a person.\n"]
    (ROOT / "docs" / "agent_start.md").write_text("\n".join(L) + "\n", encoding="utf-8")
