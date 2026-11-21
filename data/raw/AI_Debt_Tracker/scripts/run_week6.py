"""Week 6: the episode graph with the opening-ledger reader and the investigators, on every AI-25 dev episode.

  run <start> <inv> [ids…]   start = oracle | agent; inv = inv | noinv. Writes each episode to
                             `$AI_DEBT_DATA/week6/episodes_<start>_<inv>/<episode>.json`, checkpoints to
                             `week6/checkpoints_<start>_<inv>.sqlite` (an interrupted run resumes)
  score                      grade every run and B0 on the same episodes → docs/agent_start.md (`week6_report.py`)

Three runs answer the week's questions (DESIGN.md §9.4, §11 week 6):

  oracle noinv   the Week 5 graph with this week's merge fixes (P56–P58) and loan rules — against Week 5's run
  oracle inv     + investigators (ablation A1: what reconciliation fixes)
  agent inv      + the opening-ledger reader instead of B0's opening ledger (ablation A4: agent start vs oracle start)

**What is reused, and why that is fair.** Triage decisions come from Week 6's triage run over the same pool
(`week6/triage_qwen3_4b.json`: the rules with P53 and P54); readings of filings from Week 5's (`week5/readings/`,
the same reader), with the P58 option marker applied by code on top; opening readings from `opening_eval.py run`
(`week6/opening/`). A document reads the same whichever episode or run asks, so every run sees identical readings
and differs only in what the run is about. A filing that no saved reading covers is read live and saved.
"""

from __future__ import annotations

import json
import sys
import threading
import time
from collections import Counter

from ai_debt_tracker import config
from ai_debt_tracker.documents.store import DocumentStore
from ai_debt_tracker.graph import supervisor as sv
from ai_debt_tracker.graph.nodes import investigator as inv
from ai_debt_tracker.graph.nodes import reader as rd
from ai_debt_tracker.mcp_servers.edgar_pit_core import PointInTimeEdgar, Refused

import run_episodes as w5

OUT = config.data_dir() / "week6"
TRIAGE_RUN = OUT / "triage_qwen3_4b.json"
OPENING = OUT / "opening"
LOG = config.data_dir() / "logs" / "edgar_pit_week6.jsonl"
GPU = threading.Semaphore(1)          # one Ollama slot this week (memory, Week 5)
W5_READINGS = config.data_dir() / "week5" / "readings"
w5.READINGS = OUT / "readings"        # a filing no Week 5 reading covers is saved here, not in week5/


def run_dir(start: str, investigators: str):
    return OUT / f"episodes_{start}_{investigators}"


def make_tools(pit, triage_cache: dict, stats: Counter, start: str, use_inv: bool, opening_adsh: str) -> sv.Tools:
    base = w5.make_tools(pit, triage_cache, stats)
    store = DocumentStore(pit)
    rows: dict = {}

    def docs_of(row: dict) -> list:
        return [store.open(f"{row['cik']}/{row['accession']}/{d['document']}") for d in w5.reading_docs(row)]

    def read(row):
        rows[row["accession"]] = row
        p5 = W5_READINGS / f"{row['accession']}.json"
        if p5.exists():
            stats["readings cached"] += 1
            r = json.loads(p5.read_text(encoding="utf-8")) | {"cached": True}
        else:
            r = base.read(row)                # read live; saved under week6/readings
        evs = [dict(e) for e in r.get("events", [])]
        try:
            rd.mark_options(evs, docs_of(row))                    # P58, code on the cited words
        except Exception as ex:  # noqa: BLE001 — a document that cannot be reopened is read without the marker
            stats[f"option marker skipped: {type(ex).__name__}"] += 1
        stats["options marked"] += sum(bool(e.get("option")) for e in evs)
        return r | {"events": evs}

    def opening(state):
        try:
            pit._check(state["cik"], opening_adsh)     # this episode's cut-off must allow the report
        except Refused as ex:
            stats["opening refused"] += 1
            return {"instruments": [], "totals": {}, "error": f"refused by the point-in-time rule: {ex}"}
        rec = json.loads((OPENING / f"{opening_adsh}.json").read_text(encoding="utf-8"))
        return rec["model"] | {"document": rec["document"], "adsh": opening_adsh}

    def investigate(q, instruments):
        stats["investigations"] += 1
        return inv.investigate(q, instruments, lambda acc: docs_of(rows[acc]), gpu=GPU)

    base.read = read
    base.gpu = GPU
    base.opening = opening if start == "agent" else None
    base.investigate = investigate if use_inv else None
    return base


def run(start: str, investigators: str, ids: list[str]) -> int:
    from langgraph.checkpoint.sqlite import SqliteSaver
    assert start in ("oracle", "agent") and investigators in ("inv", "noinv")
    eps = [e for e in w5.dev_episodes() if not ids or e["episode_id"] in ids]
    triage_cache = {r["accession"]: r for r in json.loads(TRIAGE_RUN.read_text(encoding="utf-8"))}
    opens, _ = w5.openings(eps)
    out_dir = run_dir(start, investigators)
    out_dir.mkdir(parents=True, exist_ok=True)
    t_all = time.time()
    with SqliteSaver.from_conn_string(str(OUT / f"checkpoints_{start}_{investigators}.sqlite")) as saver:
        for e in eps:
            path = out_dir / f"{e['episode_id']}.json"
            if path.exists():
                continue
            cik = int(e["cik"])
            pit = PointInTimeEdgar.for_episode(cik, e["target_adsh"], log_path=LOG)
            stats = Counter()
            o = opens[e["episode_id"]]
            graph = sv.build(make_tools(pit, triage_cache, stats, start, investigators == "inv", o["opening_adsh"]),
                             saver)
            t0 = time.time()
            cfg = {"configurable": {"thread_id": e["episode_id"]}, "max_concurrency": 4, "recursion_limit": 60}
            snap = graph.get_state(cfg)
            if snap.next:
                out = graph.invoke(None, cfg)
            elif snap.values.get("checks"):
                out = snap.values
            else:
                inp = {"episode": e["episode_id"], "cik": cik, "quarter_end": w5.iso(e["target_period"]),
                       "window_open": e["window_open"], "cutoff_date": pit.cutoff_date, "rounds": 0}
                if start == "oracle":
                    inp |= {"opening": o["instruments"], "opening_totals": o["totals"]}
                out = graph.invoke(inp, cfg)
            rec = {"episode": e["episode_id"], "cik": cik, "company": e["company"], "group": e["group"],
                   "start": start, "investigators": investigators == "inv",
                   "quarter_end": w5.iso(e["target_period"]), "target_adsh": e["target_adsh"],
                   "graded_level": e["graded_level"], "opening": {"note": o["note"], "adsh": o["opening_adsh"]},
                   "opening_reading": out.get("opening_reading"),
                   "opening_ledger": out.get("opening") if start == "agent" else None,
                   "candidates": len(out["candidates"]),
                   "relevant": [{"accession": r["accession"], "form": r["form"], "accepted": r["accepted"],
                                 "decided_by": r["triage"]["decided_by"], "event_type": r["triage"]["event_type"]}
                                for r in out["relevant"]],
                   "readings": out.get("readings", []), "ledger": out["ledger"], "checks": out["checks"],
                   "findings": out.get("findings", []), "rounds": out.get("rounds", 0),
                   "timings": out.get("timings", []), "wall_seconds": round(time.time() - t0, 1), "cache": dict(stats)}
            path.write_text(json.dumps(rec, indent=0, default=str), encoding="utf-8")
            lg = Counter(x["change"] for x in out["ledger"]["meta"]["log"])
            print(f"{e['episode_id']:22s} {e['company'][:14]:14s} {len(out['relevant']):2d} relevant; {dict(lg)}; "
                  f"q {len(out['checks']['questions'])} findings {len(out.get('findings', []))} rounds "
                  f"{out.get('rounds', 0)}; {rec['wall_seconds']}s", flush=True)
    print(f"\n{len(eps)} episodes in {time.time() - t_all:.0f}s")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "score"
    if cmd == "run":
        sys.exit(run(sys.argv[2], sys.argv[3], sys.argv[4:]))
    from week6_report import score
    sys.exit(score())
