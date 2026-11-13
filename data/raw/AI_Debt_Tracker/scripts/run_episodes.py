"""Week 5: full episodes end to end on dev, and the first L1 bond recall and precision (DESIGN.md §11 week 5).

  run [ids…]   run the episode graph (`graph/supervisor.py`) on every AI-25 dev episode (or the ones named):
               timeline → triage → parallel readers → ledger engine → self-checks, oracle start. Each closing
               ledger and everything that made it goes to `$AI_DEBT_DATA/week5/episodes/<episode>.json`;
               LangGraph checkpoints to `$AI_DEBT_DATA/week5/checkpoints.sqlite`, so an interrupted run resumes
  score        grade every saved episode against its target report, and baseline B0 on the same episodes;
               writes docs/episodes.md

**Oracle start (ablation A4).** The opening ledger is the one B0 carries forward: the last report itemised finely
enough, read from the answer key, as plain instruments. The harness hands it to the graph; the graph never sees
the key. The graph's maturity sweep is B0's rule. So **the tracker's ledger is B0's ledger plus what reading the
filings changed**, and the comparison with B0 on the same episodes measures reading and nothing else.

**What is cached, and why that is fair.** Triage of a filing is looked up in this week's triage run over the same
pool (`$AI_DEBT_DATA/week5/triage_qwen3_4b.json`, the same code and model; a filing not in it is triaged live).
A reading of a filing is saved under `week5/readings/` and reused by the next episode whose window holds the
same filing: a document reads the same whichever quarter asks. Both are recorded per episode.

Usage:  python scripts/run_episodes.py run [episode ids]   ·   score
"""

from __future__ import annotations

import csv
import json
import sys
import threading
import time
from collections import Counter, defaultdict
from pathlib import Path

from ai_debt_tracker import config
from ai_debt_tracker.documents.store import DocumentStore
from ai_debt_tracker.graph import supervisor as sv
from ai_debt_tracker.graph.nodes import reader as rd
from ai_debt_tracker.graph.nodes import timeline as tl
from ai_debt_tracker.graph.nodes import triage as tr
from ai_debt_tracker.mcp_servers.edgar_pit_core import PointInTimeEdgar

ROOT = Path(__file__).resolve().parents[1]
OUT = config.data_dir() / "week5"
EPS = OUT / "episodes"
READINGS = OUT / "readings"
TRIAGE_RUN = OUT / "triage_qwen3_4b.json"
LOG = config.data_dir() / "logs" / "edgar_pit_week5.jsonl"
GPU = threading.Semaphore(2)          # Ollama's parallel slots on this laptop (DESIGN.md §7.5)


def dev_episodes() -> list[dict]:
    with open(ROOT / "manifests" / "dev.csv", encoding="utf-8") as f:
        return [e for e in csv.DictReader(line for line in f if not line.startswith("#")) if e["universe"] == "ai25"]


def iso(period: str) -> str:
    return f"{period[:4]}-{period[4:6]}-{period[6:8]}"


# ------------------------------------------------------------------------------------ the tools
def reading_docs(row: dict) -> list[dict]:
    """The main document and the press-release exhibits (EX-99), as in Week 4's evaluation."""
    form = row["form"]
    main = [d for d in row["documents"] if d["type"] == form or d["type"].startswith(form[:4])][:1]
    ex99 = [d for d in row["documents"] if d["type"].startswith("EX-99")]
    return [d for d in main + ex99 if d["document"].lower().endswith((".htm", ".html", ".txt"))]


def make_tools(pit: PointInTimeEdgar, triage_cache: dict, stats: Counter) -> sv.Tools:
    import triage_eval as te          # the cached text of each filing's start (Week 3's pool texts)
    store = DocumentStore(pit)

    def timeline(cik, start, end):
        return tl.to_json(tl.timeline(pit, cik, start, end, tl.issuing_subsidiaries(cik)))

    def triage(row, texts):
        if row["accession"] in triage_cache:
            stats["triage cached"] += 1
            return triage_cache[row["accession"]]
        stats["triage live"] += 1
        with GPU:
            return tr.to_json(tr.triage(row["form"], row["items"], texts, row["accession"]))

    def read(row):
        path = READINGS / f"{row['accession']}.json"
        if path.exists():
            stats["readings cached"] += 1
            return json.loads(path.read_text(encoding="utf-8")) | {"cached": True}
        docs = [store.open(f"{row['cik']}/{row['accession']}/{d['document']}") for d in reading_docs(row)]
        with GPU:
            r = rd.read_filing(docs, row["accession"], row["form"])
        stats["readings run"] += 1
        out = {"events": [rd.asdict(e) for e in r.events], "set_aside": [rd.asdict(e) for e in r.set_aside],
               "passages": r.passages, "seconds": r.seconds, "error": r.error}
        READINGS.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(out), encoding="utf-8")
        return out

    return sv.Tools(timeline=timeline, texts=lambda row: te.texts_for(pit, row), triage=triage, read=read, gpu=GPU)


# ------------------------------------------------------------------------------------ opening (oracle start)
def openings(eps: list[dict]):
    """For each episode: the opening ledger B0 carries forward (unswept: the graph sweeps), its totals, and the
    records the scorer needs. Grading side, kept in the harness."""
    from ai_debt_tracker.eval.answer_key import AnswerKey
    from ai_debt_tracker.eval.baselines.carry_forward import carry_forward, opening_report
    from review_universe import extracted_periods
    ak = AnswerKey(extracted_periods(), {int(e["cik"]) for e in eps})
    records, out = {}, {}
    for e in eps:
        reports = ak.reports(int(e["cik"]))
        for r in reports:
            if r["adsh"] not in records:
                records[r["adsh"]] = ak.filing_record(r["adsh"])
        rec, note = opening_report(reports, e["start_adsh"], e["graded_level"], records)
        unswept = carry_forward(rec, "00000000")                 # year 0: nothing swept here
        out[e["episode_id"]] = {"instruments": unswept["instruments"], "totals": unswept["totals"], "note": note,
                                "opening_adsh": rec["adsh"]}
    return out, records


def run(ids: list[str]) -> int:
    from langgraph.checkpoint.sqlite import SqliteSaver
    eps = [e for e in dev_episodes() if not ids or e["episode_id"] in ids]
    triage_cache = {r["accession"]: r for r in json.loads(TRIAGE_RUN.read_text(encoding="utf-8"))} \
        if TRIAGE_RUN.exists() else {}
    opens, _ = openings(eps)
    EPS.mkdir(parents=True, exist_ok=True)
    t_all = time.time()
    with SqliteSaver.from_conn_string(str(OUT / "checkpoints.sqlite")) as saver:
        for e in eps:
            path = EPS / f"{e['episode_id']}.json"
            if path.exists():
                continue
            cik = int(e["cik"])
            pit = PointInTimeEdgar.for_episode(cik, e["target_adsh"], log_path=LOG)
            stats = Counter()
            graph = sv.build(make_tools(pit, triage_cache, stats), saver)
            o = opens[e["episode_id"]]
            t0 = time.time()
            cfg = {"configurable": {"thread_id": e["episode_id"]}, "max_concurrency": 4}
            snap = graph.get_state(cfg)
            if snap.next:                              # interrupted mid-episode: resume from the checkpoint
                out = graph.invoke(None, cfg)
            elif snap.values.get("checks"):            # finished before the record was written
                out = snap.values
            else:
                out = graph.invoke({"episode": e["episode_id"], "cik": cik, "quarter_end": iso(e["target_period"]),
                                    "window_open": e["window_open"], "cutoff_date": pit.cutoff_date,
                                    "opening": o["instruments"], "opening_totals": o["totals"]}, cfg)
            rec = {"episode": e["episode_id"], "cik": cik, "company": e["company"], "group": e["group"],
                   "quarter_end": iso(e["target_period"]), "target_adsh": e["target_adsh"],
                   "graded_level": e["graded_level"], "opening": {"note": o["note"], "adsh": o["opening_adsh"]},
                   "candidates": len(out["candidates"]),
                   "relevant": [{"accession": r["accession"], "form": r["form"], "accepted": r["accepted"],
                                 "decided_by": r["triage"]["decided_by"], "event_type": r["triage"]["event_type"]}
                                for r in out["relevant"]],
                   "readings": out.get("readings", []), "ledger": out["ledger"], "checks": out["checks"],
                   "timings": out.get("timings", []), "wall_seconds": round(time.time() - t0, 1), "cache": dict(stats)}
            path.write_text(json.dumps(rec, indent=0, default=str), encoding="utf-8")
            lg = Counter(x["change"] for x in out["ledger"]["meta"]["log"])
            print(f"{e['episode_id']:22s} {e['company'][:14]:14s} {len(out['candidates']):3d} filings, "
                  f"{len(out['relevant']):2d} relevant, {sum(r['events'] for r in out.get('readings', [])):2d} events; "
                  f"{dict(lg)}; flags {[f['check'] for f in out['checks']['flags']]}; {rec['wall_seconds']}s "
                  f"{dict(stats)}", flush=True)
    print(f"\n{len(eps)} episodes in {time.time() - t_all:.0f}s")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "score"
    if cmd == "run":
        sys.exit(run(sys.argv[2:]))
    from episodes_report import score
    sys.exit(score())
