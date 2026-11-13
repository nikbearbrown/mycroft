"""Week 5: score the saved episodes (scripts/run_episodes.py) and baseline B0 on the same episodes → docs/episodes.md.

Grading is the Week 2 grader, unchanged: each closing ledger against its target report at the episode's frozen
level, with change detection where the start report is itemised too. B0 is rebuilt here from the same opening
report the graph was given, so the two are paired episode by episode. Intervals are 95% bootstrap over episodes;
the difference is a *paired* bootstrap (the same resampled episodes for both).
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from ai_debt_tracker import config
from ai_debt_tracker.eval.answer_key import AnswerKey, grading_level
from ai_debt_tracker.eval.baselines.carry_forward import carry_forward
from ai_debt_tracker.eval.grader import _bond_cost, assign, grade_episode, summarise, truth_bonds
from review_universe import extracted_periods

ROOT = Path(__file__).resolve().parents[1]
EPS = config.data_dir() / "week5" / "episodes"
EPS_RUN1 = config.data_dir() / "week5" / "episodes_run1"   # the first run, before the P55 fix (kept, not overwritten)


def _paired(a_num, a_den, b_num, b_den, n_boot=2000, seed=0):
    a_num, a_den, b_num, b_den = map(lambda x: np.asarray(x, float), (a_num, a_den, b_num, b_den))
    d = a_num.sum() / max(a_den.sum(), 1) - b_num.sum() / max(b_den.sum(), 1)
    rng, n, ds = np.random.default_rng(seed), len(a_num), []
    for _ in range(n_boot):
        i = rng.integers(0, n, n)
        if a_den[i].sum() and b_den[i].sum():
            ds.append(a_num[i].sum() / a_den[i].sum() - b_num[i].sum() / b_den[i].sum())
    return d, float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5))


def pct(t):
    p, lo, hi = t
    return "—" if p != p else f"{p:.1%} ({lo:.1%}–{hi:.1%})"


def score() -> int:
    with open(ROOT / "manifests" / "dev.csv", encoding="utf-8") as f:
        man = {e["episode_id"]: e for e in csv.DictReader(line for line in f if not line.startswith("#"))}
    runs = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(EPS.glob("*.json"))]
    ak = AnswerKey(extracted_periods(), {r["cik"] for r in runs})
    rec = {}

    def record(adsh):
        if adsh not in rec:
            rec[adsh] = ak.filing_record(adsh)
        return rec[adsh]

    full, b0, rows, added_rows = [], [], [], []
    for r in runs:
        e = man[r["episode"]]
        target, start = record(e["target_adsh"]), record(e["start_adsh"])
        start_ch = start if grading_level(start)["level"] == "L1" else None
        led = r["ledger"]
        g = grade_episode(target, led, e["graded_level"], start_ch)
        base = carry_forward(record(r["opening"]["adsh"]), e["target_period"])
        gb = grade_episode(target, base, e["graded_level"], start_ch)
        for x, src in ((g, full), (gb, b0)):
            x.update({"episode": r["episode"], "company": r["company"], "group": r["group"]})
            src.append(x)
        # which of the ledger's additions are real
        new = [i for i in led["instruments"] if str(i.get("id", "")).startswith("new-") and i.get("kind") == "bond"]
        truth = truth_bonds(target)
        bonds = [i for i in led["instruments"] if i.get("kind") == "bond"]
        matched_cols = {c for _, c in assign(truth, bonds, _bond_cost)}
        new_ok = [i for i in new if bonds.index(i) in matched_cols]
        rows.append({"r": r, "e": e, "g": g, "gb": gb, "new": new, "new_ok": new_ok})
        for i in new:
            added_rows.append((r["company"], r["episode"], i, i in new_ok, e["graded_level"]))
    sf, sb = summarise(full), summarise(b0)
    run1 = None
    if EPS_RUN1.exists():
        g1, add1 = [], [0, 0]
        for p1 in sorted(EPS_RUN1.glob("*.json")):
            r1 = json.loads(p1.read_text(encoding="utf-8"))
            e = man[r1["episode"]]
            target, start = record(e["target_adsh"]), record(e["start_adsh"])
            g1.append(grade_episode(target, r1["ledger"], e["graded_level"],
                                    start if grading_level(start)["level"] == "L1" else None))
            if e["graded_level"] == "L1":
                bonds = [i for i in r1["ledger"]["instruments"] if i.get("kind") == "bond"]
                cols = {c for _, c in assign(truth_bonds(target), bonds, _bond_cost)}
                new = [k for k, i in enumerate(bonds) if str(i.get("id", "")).startswith("new-")]
                add1[0] += len(new)
                add1[1] += sum(k in cols for k in new)
        run1 = (summarise(g1), add1)
    write(runs, rows, sf, sb, full, b0, added_rows, run1)
    print(json.dumps({"full": {k: v for k, v in sf.items() if k != "l3"}, "b0": {k: v for k, v in sb.items() if k != "l3"}},
                     indent=1, default=str)[:3000])
    return 0


def write(runs, rows, sf, sb, full, b0, added_rows, run1=None):
    l1f, l1b = sf.get("l1", {}), sb.get("l1", {})
    chf, chb = l1f.get("changes", {}), l1b.get("changes", {})
    L1 = [(x, y) for x, y in zip(full, b0) if "l1" in x]
    claimed = lambda x: x["l1"]["ledger"] - x["l1"]["covered_by_offering"] - x["l1"].get("covered_by_unkeyed", 0)  # noqa: E731
    d_rec = _paired([x["l1"]["matched"] for x, _ in L1], [x["l1"]["truth"] for x, _ in L1],
                    [y["l1"]["matched"] for _, y in L1], [y["l1"]["truth"] for _, y in L1])
    d_pre = _paired([x["l1"]["matched"] for x, _ in L1], [claimed(x) for x, _ in L1],
                    [y["l1"]["matched"] for _, y in L1], [claimed(y) for _, y in L1])
    n_eps = len(runs)
    cands = sum(r["candidates"] for r in runs)
    rel = {x["accession"] for r in runs for x in r["relevant"]}
    # cost comes from the first run, where every filing was read; the second run reused those readings
    cost_runs = [json.loads(q.read_text(encoding="utf-8")) for q in sorted(EPS_RUN1.glob("*.json"))] \
        if EPS_RUN1.exists() else runs
    reads = [x for r in cost_runs for x in r["readings"]]
    fresh = [x for x in reads if not x.get("cached")]
    secs = sum(x.get("seconds") or 0 for x in fresh)
    wall = sum(r["wall_seconds"] for r in cost_runs)
    errors = Counter(x["error"] for x in fresh if x.get("error"))
    flags = Counter(f["check"] for r in runs for f in r["checks"]["flags"])
    qs = Counter(q["type"] for r in runs for q in r["checks"]["questions"])
    changes = Counter(c["change"] for r in runs for c in r["ledger"]["meta"]["log"])
    flagged_eps = sum(bool(r["checks"]["flags"]) for r in runs)
    n_new = len(added_rows)
    l1_add = [x for x in added_rows if x[4] == "L1"]
    n_l1, n_l1_ok = len(l1_add), sum(x[3] for x in l1_add)
    tot_f = [x["l3"]["total_debt"] for x in full if "total_debt" in x["l3"]]
    tot_b = [x["l3"]["total_debt"] for x in b0 if "total_debt" in x["l3"]]

    L = ["# Full episodes, end to end on dev (week 5)\n",
         "> Generated by `scripts/run_episodes.py score` (`scripts/episodes_report.py`). The graph: "
         "`src/ai_debt_tracker/graph/supervisor.py`; the ledger engine and self-checks: `ledger/engine.py`, "
         "`ledger/checks.py`. Every episode, with its ledger, the events and their citations: "
         "`$AI_DEBT_DATA/week5/episodes/`. Intervals are 95% bootstrap over episodes.\n",
         "## The week 5 check\n",
         f"**{n_eps} of {n_eps} AI-25 dev episodes ran end to end** — timeline, triage, parallel readers, merge, "
         "maturity sweep, ledger engine, self-checks — and every closing ledger was graded. The first L1 bond recall "
         "and precision are below. (DESIGN.md §11's check for week 5 is that full episodes run end to end and that "
         "these numbers exist; there is no pass line on them yet.)\n",
         "**Oracle start.** Every episode opens from the ledger B0 carries forward (the last report itemised finely "
         "enough, from the answer key; ablation A4). The graph's own maturity sweep is B0's rule. So the difference "
         "between the tracker and B0 below is what reading the filings added — and everything the opening ledger "
         "gets wrong, both share. The opening-ledger reader (agent start) is week 6.\n",
         "## L1 — per bond\n",
         "| | Episodes | True bonds | Recall | Precision | Principal right | Exact episodes |", "|---|---|---|---|---|---|---|",
         f"| **Tracker (reads the filings)** | {l1f.get('episodes')} | {l1f.get('truth')} | **{pct(l1f['recall'])}** | "
         f"**{pct(l1f['precision'])}** | {pct(l1f['principal_accuracy'])} | {l1f.get('exact_episodes')} |",
         (f"| Tracker, first run (before P55) | {run1[0]['l1']['episodes']} | {run1[0]['l1']['truth']} | "
          f"{pct(run1[0]['l1']['recall'])} | {pct(run1[0]['l1']['precision'])} | {pct(run1[0]['l1']['principal_accuracy'])} | "
          f"{run1[0]['l1']['exact_episodes']} |") if run1 else "",
         f"| B0 (carry forward) | {l1b.get('episodes')} | {l1b.get('truth')} | {pct(l1b['recall'])} | {pct(l1b['precision'])} | "
         f"{pct(l1b['principal_accuracy'])} | {l1b.get('exact_episodes')} |",
         "",
         f"Paired difference, tracker minus B0, same episodes: recall **{d_rec[0]:+.1%}** ({d_rec[1]:+.1%} to "
         f"{d_rec[2]:+.1%}), precision **{d_pre[0]:+.1%}** ({d_pre[1]:+.1%} to {d_pre[2]:+.1%}).\n"]
    if run1:
        c1 = run1[0]["l1"]["changes"]
        L += [f"**The first run, and the one fix made on dev (P55).** The first run applied every event up to the target "
              f"report's filing — weeks after the quarter ended — so bonds priced *after* the quarter end were put in its "
              f"ledger (CoreWeave's July 2025 notes in the June quarter; Super Micro's early-2025 notes in two 2024 "
              f"quarters). The design keeps the ledger by settlement date (P4); settlement dates are not parsed yet, so "
              f"the fix applies only events filed on or before the quarter end and keeps the rest in the record. First "
              f"run: new bonds caught {round(c1['added_recall'][0] * c1['added'])} of {c1['added']}; of {run1[1][0]} bonds "
              f"added in L1 episodes, {run1[1][1]} matched. Both runs are on dev, which is what dev is for; the test "
              f"split has not been touched.\n"]
    if chf:
        L += ["## What reading added: the changes\n",
              f"{chf['episodes']} episodes have an itemised start report too, so their bond changes can be counted "
              f"({chf['episodes_with_change']} have at least one).\n",
              "| | New bonds caught | Removed bonds caught |", "|---|---|---|",
              f"| **Tracker** | **{round(chf['added_recall'][0] * chf['added'])} of {chf['added']}** ({pct(chf['added_recall'])}) | "
              f"{round(chf['removed_recall'][0] * chf['removed'])} of {chf['removed']} ({pct(chf['removed_recall'])}) |",
              f"| B0 | {round(chb['added_recall'][0] * chb['added'])} of {chb['added']} | "
              f"{round(chb['removed_recall'][0] * chb['removed'])} of {chb['removed']} |", "",
              f"Across all {n_eps} episodes the tracker added **{n_new} bonds** to the opening ledgers. "
              f"**{n_l1}** were added in L1 episodes, where the target report itemises every bond: **{n_l1_ok}** of them "
              f"match a bond in it and **{n_l1 - n_l1_ok} do not** — misreads, or bonds that settled after the quarter "
              f"(listed below). The other {n_new - n_l1} were added in L2/L3 episodes, whose reports do not itemise bonds, "
              "so they cannot be checked one by one (they count through the L2 offerings and the L3 totals).\n"]
    if sf.get("l2"):
        L += [f"**L2 — per offering** ({sf['l2']['episodes']} episodes): tracker recall {pct(sf['l2']['recall'])}, "
              f"precision {pct(sf['l2']['precision'])}; B0 recall {pct(sb['l2']['recall'])}, precision "
              f"{pct(sb['l2']['precision'])}.\n"]
    L += [f"**L3 — total debt within 2%:** tracker {sum(v['ok'] for v in tot_f)} of {len(tot_f)}, B0 "
          f"{sum(v['ok'] for v in tot_b)} of {len(tot_b)}. Totals move only by the swept and the applied dollar "
          "amounts; foreign-currency changes are not converted "
          f"({sum(r['ledger']['meta'].get('foreign_changes_not_in_total', 0) for r in runs)} left out), and a new "
          "facility's commitment is not a drawn balance, so it is not added.\n",
          "## The episodes, as a system\n",
          f"- **Filings:** {cands} candidate filings across the windows (windows overlap, so a filing can be in two "
          f"episodes); triage kept {sum(len(r['relevant']) for r in runs)} (distinct: {len(rel)}).",
          f"- **Readings:** {len(reads)} reader branches ran as `Send` fan-outs; {len(fresh)} read a filing for the first "
          f"time ({secs / 60:.1f} reader-minutes summed over branches; two run at once and Ollama serves one, so this "
          f"counts queueing too), {len(reads) - len(fresh)} reused a reading saved by an earlier episode. "
          + (f"Reader errors: {dict(errors)}." if errors else "No reader errors."),
          f"- **Wall time:** {wall / 60:.1f} minutes for {n_eps} episodes on the laptop "
          f"(median {sorted(r['wall_seconds'] for r in cost_runs)[len(cost_runs) // 2]:.1f} s, longest "
          f"{max(r['wall_seconds'] for r in cost_runs):.0f} s, first run; most windows hold no debt news, and a reading saved by an earlier "
          "episode is reused). The run was stopped once by the laptop running low on memory and resumed from the saved "
          "episodes and readings. The second run (after P55) reused every reading and took about a minute.",
          f"- **Ledger changes applied:** " + ", ".join(f"{k} {v}" for k, v in changes.most_common()) + ".",
          f"- **Self-checks:** {flagged_eps} of {n_eps} episodes raised at least one flag — "
          + (", ".join(f"{k} {v}" for k, v in flags.most_common()) if flags else "none")
          + f". Open questions for the investigators (week 6): "
          + (", ".join(f"{k} {v}" for k, v in qs.most_common()) if qs else "none") + ".\n"]
    L += ["## Why precision fell: the false additions\n",
          "Reading added 40 true bonds to L1 ledgers and 26 that are not in the target report — so recall rose and "
          "precision fell. The 26, read one by one after scoring (Claude's diagnosis, a judgment), are three kinds, "
          "logged for week 6 and not fixed against this run:\n",
          "- **P57 — a proposed offering added as its own bond (10).** A launch announcement (\"intends to offer $300 "
          "million of convertible notes due 2030\") or a blank preliminary prospectus states no coupon yet, so its event "
          "has no match key and cannot merge with the priced bond that follows; the engine adds both. Oracle's blank "
          "five-tranche prospectus, CoreWeave's, Super Micro's, Cipher Mining's and Applied Digital's launches, and one of "
          "Equinix's.",
          "- **P56 — existing notes read from a prospectus as new issues (10, all Equinix).** Two preliminary prospectuses' "
          "descriptions of the notes already outstanding; no amount was read for any of them. P52's set-aside covers only "
          "values read from table rows, and these were not.",
          "- **P58 — the banks' option listed as a bond of its own (4).** \"up to an additional $45 million\" (Applied "
          "Digital), $75 m, $22 m (Cipher Mining), Super Micro's $300 m: part of the base notes, as in the answer key's "
          "own P38.",
          "- One misread maturity (Digital Realty's euro notes as 2033 as well as 2035) and one coupon read as a new bond "
          "(Micron, 4.975% 2026).\n",
          "All three main kinds are visible in the record (no coupon, no amount, or an option sentence), so they are "
          "rules for the merge step, not new model calls.\n"]
    L += ["## Every bond the tracker added\n", "| Company | Episode | Level | Bond | In the target report? | Read from |",
          "|---|---|---|---|---|---|"]
    for comp, ep, i, ok, lvl in added_rows:
        accs = sorted({s["accession"] for ev in i.get("events", []) for s in ev.get("sources", [])})
        p = f"{i.get('currency')} {i['principal'] / 1e6:,.0f} m" if i.get("principal") else "amount not read"
        L.append(f"| {comp} | {ep} | {lvl} | {i.get('coupon_pct')}% {i.get('maturity_year')}, {p} | {('yes' if ok else '**no**') if lvl == 'L1' else 'not itemised (' + lvl + ')'} | "
                 f"{', '.join(accs[:3])} |")
    misses = defaultdict(list)
    for x in rows:
        if "l1" in x["g"]:
            misses[x["r"]["company"]].append(len(x["g"]["l1"]["missed"]))
    L += ["\n## By episode (L1)\n", "| Episode | Company | True | Tracker matched | B0 matched | Tracker extra | B0 extra | "
          "New caught (tracker / B0) |", "|---|---|---|---|---|---|---|---|"]
    for x in rows:
        if "l1" not in x["g"]:
            continue
        a, b = x["g"]["l1"], x["gb"]["l1"]
        ch = f"{a.get('added_caught', '—')} / {b.get('added_caught', '—')} of {a.get('added', '—')}" if "added" in a else "—"
        L.append(f"| {x['r']['episode']} | {x['r']['company']} | {a['truth']} | {a['matched']} | {b['matched']} | "
                 f"{a['extra']} | {b['extra']} | {ch} |")
    L += ["\n## Who decided what\n",
          "Which filings are about debt, which instruments each announces and each one's action are model judgments "
          "(`qwen3:4b`, P8), flagged in every event. Every number in a ledger was parsed by code from words in a cited "
          "passage, or comes from the opening report. The merge, the sweep, the ledger and the checks are code. Nothing "
          "here has been reviewed by a person yet.\n"]
    (ROOT / "docs" / "episodes.md").write_text("\n".join(L) + "\n", encoding="utf-8")
