"""Week 6: the opening-ledger reader (agent start), measured on its own (DESIGN.md §7.3, ablation A4).

  run [model]   read the opening report of every AI-25 dev episode — the same report baseline B0 carries forward —
                with the opening-ledger reader (`graph/nodes/opening.py`: code finds the debt tables, `qwen3:4b`
                points at instrument rows and the period-end column, code parses) and with its no-model comparison
                (`rules`). One reading per report, saved to `$AI_DEBT_DATA/week6/opening/<accession>.json`
  score         grade each reading against the answer key's record of *that same report* (L1 per bond where the
                report is itemised, L2 per offering, total debt within 2%); writes docs/opening_reader.md

Which report to read is B0's choice (the last report itemised finely enough; `carry_forward.opening_report`), so the
oracle and the agent start from the same document and the gap between them is reading error only. That choice uses
the key's itemisation, which an agent in live mode would not have; it is stated in the report.

Usage:  python scripts/opening_eval.py run [model] · score
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

from ai_debt_tracker import config
from ai_debt_tracker.documents.store import DocumentStore
from ai_debt_tracker.graph.nodes import opening as op
from ai_debt_tracker.mcp_servers.edgar_pit_core import PointInTimeEdgar, Refused

ROOT = Path(__file__).resolve().parents[1]
OUT = config.data_dir() / "week6" / "opening"
LOG = config.data_dir() / "logs" / "edgar_pit_week6.jsonl"


def iso(period: str) -> str:
    return f"{period[:4]}-{period[4:6]}-{period[6:8]}"


def reports() -> list[dict]:
    """One row per distinct opening report: the report, its period, and one episode whose cut-off allows it."""
    import run_episodes as rx
    eps = rx.dev_episodes()
    opens, recs = rx.openings(eps)
    out = {}
    for e in eps:
        o = opens[e["episode_id"]]
        a = o["opening_adsh"]
        if a not in out:
            r = recs[a]
            out[a] = {"adsh": a, "cik": int(e["cik"]), "company": e["company"], "form": r["form"],
                      "period": iso(r["period"]), "episode": e["episode_id"], "target_adsh": e["target_adsh"],
                      "episodes": []}
        out[a]["episodes"].append(e["episode_id"])
    return list(out.values()), recs


def open_main(pit, cik: int, adsh: str):
    ex = pit.exhibits(cik, adsh)
    main = next(d for d in ex if d["type"] in ("10-Q", "10-K", "10-Q/A", "10-K/A"))
    return DocumentStore(pit).open(f"{cik}/{adsh}/{main['document']}"), main["document"]


def reading(adsh: str) -> dict | None:
    p = OUT / f"{adsh}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def run(model: str = "qwen3:4b") -> int:
    rows, _ = reports()
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    for r in rows:
        path = OUT / f"{r['adsh']}.json"
        if path.exists():
            continue
        doc, name, refused = None, None, []
        man = {e["episode_id"]: e for e in __import__("run_episodes").dev_episodes()}
        for ep in r["episodes"]:                 # any episode whose cut-off lets it see the report
            pit = PointInTimeEdgar.for_episode(r["cik"], man[ep]["target_adsh"], log_path=LOG)
            try:
                doc, name = open_main(pit, r["cik"], r["adsh"])
                break
            except Refused as ex:
                refused.append({"episode": ep, "why": str(ex)})
        if doc is None:
            empty = {"instruments": [], "totals": {}, "tables": [], "error": "refused by the point-in-time rule"}
            path.write_text(json.dumps({k: r[k] for k in ("adsh", "cik", "company", "form", "period", "episodes")}
                                       | {"document": None, "rules": empty, "model": empty, "refused_for": refused},
                                       indent=0), encoding="utf-8")
            print(f"{r['company'][:16]:16s} {r['form']:5s} {r['period']} refused for every episode", flush=True)
            continue
        rules = op.read_rules(doc, r["period"])
        agent = op.read_opening(doc, r["form"], r["period"], model=model)
        rec = {k: r[k] for k in ("adsh", "cik", "company", "form", "period", "episodes")} | {
            "document": name, "rules": rules, "model": agent, "refused_for": refused}
        path.write_text(json.dumps(rec, indent=0, default=str), encoding="utf-8")
        print(f"{r['company'][:16]:16s} {r['form']:5s} {r['period']} rules {len(rules['instruments']):3d}  model "
              f"{len(agent['instruments']):3d} {agent.get('error') or ''} {agent.get('seconds', 0):.1f}s", flush=True)
    print(f"{len(rows)} reports in {time.time() - t0:.0f}s")
    return 0


def reapply(model: str = "qwen3:4b") -> int:
    """After a code fix (P61): re-read every saved report. The model's saved answer is reused when code offers it
    the same tables; only a report whose candidate tables changed is asked again. The first pass is kept in
    `week6/opening_run1/` and its scores in `opening_run1_summary.json` (both runs are reported)."""
    import shutil
    first = OUT.parent / "opening_run1"
    if not first.exists():
        shutil.copytree(OUT, first)
        s = score_numbers()
        (OUT.parent / "opening_run1_summary.json").write_text(json.dumps(s, indent=1), encoding="utf-8")
    man = {e["episode_id"]: e for e in __import__("run_episodes").dev_episodes()}
    asked = 0
    for path in sorted(first.glob("*.json")):
        old = json.loads(path.read_text(encoding="utf-8"))
        if not old.get("document"):
            continue
        ep = next(e for e in old["episodes"] if e not in {x["episode"] for x in old.get("refused_for", [])})
        pit = PointInTimeEdgar.for_episode(old["cik"], man[ep]["target_adsh"], log_path=LOG)
        doc, _ = open_main(pit, old["cik"], old["adsh"])
        saved = old["model"]

        def ask(tables, form, period, mdl, host, saved=saved):
            nonlocal asked
            if [t.id for t in tables] == saved.get("tables") and saved.get("raw"):
                try:                                     # the first pass kept 3,000 characters of the answer:
                    json.loads(saved["raw"])             # a longer one was cut and is asked again
                    return saved["raw"]
                except json.JSONDecodeError:
                    pass
            asked += 1
            return op.ask_model(tables, form, period, mdl, host)

        rules = op.read_rules(doc, old["period"])
        agent = op.read_opening(doc, old["form"], old["period"], model=model, ask=ask)
        if saved.get("seconds") is not None and agent.get("raw") == saved.get("raw"):
            agent["seconds"] = saved["seconds"]          # the model time is the first pass's; nothing was re-asked
        (OUT / path.name).write_text(json.dumps(old | {"rules": rules, "model": agent}, indent=0, default=str),
                                     encoding="utf-8")
    print(f"re-read with the saved answers; {asked} reports asked the model again")
    return 0


# ------------------------------------------------------------------------------------ scoring
def grade_reading(rec: dict, led: dict) -> dict:
    from ai_debt_tracker.eval.answer_key import grading_level
    from ai_debt_tracker.eval.grader import grade_episode
    level = grading_level(rec)["level"]
    return grade_episode(rec, led, level) | {"report_level": level}


def score_numbers() -> dict:
    """The headline numbers of the readings now on disk (kept before a re-read, so both runs are reported)."""
    per, s, _ = graded()
    out = {}
    for m in ("model", "rules"):
        l1, l2 = s[m].get("l1", {}), s[m].get("l2", {})
        tot = [x[m]["l3"]["total_debt"] for x in per if "total_debt" in x[m]["l3"]]
        out[m] = {"l1_reports": l1.get("episodes"), "l1_truth": l1.get("truth"), "l1_recall": l1.get("recall"),
                  "l1_precision": l1.get("precision"), "l1_principal": l1.get("principal_accuracy"),
                  "l1_exact": l1.get("exact_episodes"), "l2_recall": l2.get("recall"),
                  "l2_precision": l2.get("precision"), "total_ok": sum(v["ok"] for v in tot), "total_graded": len(tot)}
    return out


def score() -> int:
    per, s, res = graded()
    write(per, s, res)
    print(json.dumps({m: {k: v for k, v in x.items() if k != "l3"} for m, x in s.items()}, indent=1, default=str)[:2500])
    return 0


def graded():
    from ai_debt_tracker.eval.grader import summarise
    rows, recs = reports()
    res = {"rules": [], "model": []}
    per = []
    for r in rows:
        rd = reading(r["adsh"])
        if rd is None:
            continue
        rec = recs[r["adsh"]]
        line = {"r": r, "rd": rd, "rec": rec}
        for m in ("rules", "model"):
            g = grade_reading(rec, rd[m])
            g.update({"episode": r["adsh"], "company": r["company"]})
            res[m].append(g)
            line[m] = g
        per.append(line)
    s = {m: summarise(v) for m, v in res.items()}
    return per, s, res


def pct(t):
    p, lo, hi = t
    return "—" if p != p else f"{p:.1%} ({lo:.1%}–{hi:.1%})"


def write(per, s, res):
    n = len(per)
    secs = [x["rd"]["model"].get("seconds") or 0 for x in per]
    errs = Counter((x["rd"]["model"].get("error") or "")[:40] for x in per if x["rd"]["model"].get("error"))
    refused = sum(len(x["rd"]["model"].get("refused", [])) for x in per)
    tot = {m: [x[m]["l3"]["total_debt"] for x in per if "total_debt" in x[m]["l3"]] for m in ("rules", "model")}
    L = ["# The opening-ledger reader (agent start) — week 6\n",
         "> Generated by `scripts/opening_eval.py score`. The reader: `src/ai_debt_tracker/graph/nodes/opening.py`. Every "
         "reading, with the rows and cells it cites: `$AI_DEBT_DATA/week6/opening/`. Intervals are 95% bootstrap over "
         "reports.\n",
         "## What it does\n",
         "For each dev episode the tracker needs the debt the company owed at the start: the opening ledger. Until now that "
         "was borrowed from the answer key (oracle start). The opening-ledger reader reads it from the report itself: code "
         "finds the debt tables, `qwen3:4b` points at the rows that are one instrument and at the column for the period "
         "end (a model judgment, P8), and code parses every value from the cited cell and the row's label with the answer "
         "key's own label parser. `rules` is the same reader with no model: the best table, rows naming a coupon or a "
         "year, and the period-end column found from the header's dates.\n",
         f"It is graded on the **{n} distinct opening reports** of the 95 dev episodes — the reports B0 carries forward — "
         "against the answer key's record of each report: per bond where the report itemises its bonds (L1), per offering "
         "(L2), and total debt within 2%.\n",
         "## Against the report it read\n",
         "| | Reports (L1) | True bonds | Recall | Precision | Principal right | Exact |", "|---|---|---|---|---|---|---|"]
    for m, name in (("model", "**Reader (model points, code reads)**"), ("rules", "Rules only (no model)")):
        l1 = s[m].get("l1", {})
        if l1:
            L.append(f"| {name} | {l1['episodes']} | {l1['truth']} | {pct(l1['recall'])} | {pct(l1['precision'])} | "
                     f"{pct(l1['principal_accuracy'])} | {l1['exact_episodes']} |")
    L.append("")
    for m, name in (("model", "Reader"), ("rules", "Rules only")):
        l2 = s[m].get("l2")
        if l2:
            L.append(f"- **L2, {name.lower()}** ({l2['episodes']} reports): offering recall {pct(l2['recall'])}, "
                     f"precision {pct(l2['precision'])}.")
    L += [f"- **Total debt within 2%:** reader {sum(v['ok'] for v in tot['model'])} of {len(tot['model'])}, rules "
          f"{sum(v['ok'] for v in tot['rules'])} of {len(tot['rules'])} (a report the key gives no total for is not graded).",
          f"- **Cost:** {sum(secs) / 60:.1f} model-minutes for {n} reports (median {sorted(secs)[n // 2]:.1f} s). "
          f"Rows the model named that code refused (no such row, or no amount in the named column): {refused}. "
          + (f"Fallbacks to rules: {dict(errs)}." if errs else "No model failures.") + "\n"]
    first = OUT.parent / "opening_run1_summary.json"
    if first.exists():
        f = json.loads(first.read_text(encoding="utf-8"))
        a, b = f["model"], f["rules"]
        L += ["## The first pass, before P61\n",
              "The first pass was scored on these same dev reports, and two code defects were found in it (P61): a "
              "rate column read as the amount when the header names one column per cell (Salesforce's 10-K and the "
              "10-Q after it: six coupons read as amounts), and the units of a table whose caption the parser cut "
              "before \"(in thousands)\" (Super Micro: a total read in billions). A table of *available* borrowings "
              "now scores as off-topic. They were fixed on dev, and every report was re-read with the model's saved "
              "answer; a report whose candidate tables changed was asked again. Both passes are reported. First pass: "
              f"reader L1 recall {pct(a['l1_recall'])}, precision {pct(a['l1_precision'])}, principal right "
              f"{pct(a['l1_principal'])}, exact {a['l1_exact']}; total debt within 2% {a['total_ok']} of "
              f"{a['total_graded']}. Rules only: recall {pct(b['l1_recall'])}, precision {pct(b['l1_precision'])}; "
              f"total debt {b['total_ok']} of {b['total_graded']}. First-pass readings: `$AI_DEBT_DATA/week6/opening_run1/`.\n"]
        again = []
        for x in per:
            p1 = OUT.parent / "opening_run1" / f"{x['r']['adsh']}.json"
            if not p1.exists():
                continue
            old = json.loads(p1.read_text(encoding="utf-8"))["model"]
            try:
                json.loads(old.get("raw") or "{}")
            except json.JSONDecodeError:
                g1 = grade_reading(x["rec"], old)
                was = g1.get("l1", {}).get("matched", "—")
                now = x["model"].get("l1", {}).get("matched", "—")
                again.append(f"{x['r']['company']} {x['r']['form']} {x['r']['period']} ({was} → {now})")
        if again:
            L += [f"The first pass stored only 3,000 characters of each model answer, so the {len(again)} longest "
                  "answers could not be reused and were asked again. The model's answer is not the same from run to "
                  "run: bonds matched, first pass → second, " + "; ".join(again) + ". That variance is part of what "
                  "the reader is; the full answer is now stored.\n"]
    L += ["## Report by report\n",
          "| Report | Company | Level | True | Reader matched / extra | Rules matched / extra | Total debt (reader) |",
          "|---|---|---|---|---|---|---|"]
    for x in per:
        a, b = x["model"], x["rules"]
        if "l1" in a:
            t = a["l1"]["truth"]
            ma, mb = f"{a['l1']['matched']} / {a['l1']['extra']}", f"{b['l1']['matched']} / {b['l1']['extra']}"
        elif "l2" in a:
            t = a["l2"]["truth"]
            ma, mb = f"{a['l2']['matched']} of {a['l2']['ledger']} units", f"{b['l2']['matched']} of {b['l2']['ledger']} units"
        else:
            t, ma, mb = "—", "—", "—"
        td = a["l3"].get("total_debt")
        tds = "—" if not td else ("ok" if td["ok"] else (f"{td['error_pct']:+.1f}%" if td["error_pct"] is not None else "none read"))
        L.append(f"| {x['r']['form']} {x['r']['period']} | {x['r']['company']} | {a['report_level']} | {t} | {ma} | {mb} | {tds} |")
    L += ["\n## Who decided what\n",
          "Which rows are instruments, their kinds and which column is the period end are `qwen3:4b`'s judgments (P8), "
          "flagged in every reading. Every number was parsed by code from a cited cell or label. Which report to read is "
          "B0's choice, made with the answer key's itemisation: the same document for both starts, so the comparison "
          "isolates reading; in live mode the agent would read the latest report and could not walk back by the key.\n"]
    (ROOT / "docs" / "opening_reader.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "score"
    if cmd == "run":
        sys.exit(run(sys.argv[2] if len(sys.argv) > 2 else "qwen3:4b"))
    if cmd == "reapply":
        sys.exit(reapply(sys.argv[2] if len(sys.argv) > 2 else "qwen3:4b"))
    sys.exit(score())
