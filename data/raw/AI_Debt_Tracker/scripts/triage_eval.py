"""Week 3: build the triage evaluation (DESIGN.md §11 week 3) and score triage against it.

  pool      every candidate filing in every **dev** episode's window, for the 25 AI companies and
            their issuing subsidiaries, from the `timeline` node through `edgar_pit` at each episode's
            cut-off; the start of each readable document is cached as text
  sample    draw the 50-filing labelled set by a fixed rule (seed 20261031): 30 at random from the whole
            pool — so the share of debt filings is honest — and 20 at random from the filings with any
            debt vocabulary, so there are enough hard cases. Writes manifests/triage_labels.json with
            empty labels (the human-readable docs/triage_labels.md is written by `report`)
  run       run triage (rules, then qwen3:4b on the doubtful) over the whole pool
  report    score triage on the labelled set — the week 3 check is recall ≥ 95% — plus recall on every
            filing that Week 2's change search found announcing a bond change; writes docs/triage.md

Labels are filled in between `sample` and `run`, by reading each filing against the definition in
`graph/nodes/triage.py`, and are never changed after `run` (they are the answer key for triage).

Usage:  python scripts/triage_eval.py pool|sample|run|report [model]
"""

from __future__ import annotations

import csv
import json
import random
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

from ai_debt_tracker import config
from ai_debt_tracker.graph.nodes import timeline as tl
from ai_debt_tracker.graph.nodes import triage as tr
from ai_debt_tracker.mcp_servers.edgar_pit_core import PointInTimeEdgar, Refused

ROOT = Path(__file__).resolve().parents[1]
OUT = config.data_dir() / "week3"
POOL = OUT / "pool.json"
TEXTS = OUT / "texts"
LABELS = ROOT / "manifests" / "triage_labels.json"
SEED = 20261031
TEXT_CHARS = 20_000


def dev_episodes():
    with open(ROOT / "manifests" / "dev.csv", encoding="utf-8") as f:
        return [e for e in csv.DictReader(line for line in f if not line.startswith("#")) if e["universe"] == "ai25"]


def texts_for(pit, c: dict) -> dict[str, str]:
    """Start of the main document and of each press-release exhibit (what triage reads)."""
    path = TEXTS / f"{c['accession']}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for d in c["documents"]:
        t = d["type"]
        if t.startswith(("EX-4", "EX-10", "EX-1.")):
            continue   # indentures and agreements: long legal text, read by the event reader, not triage
        if len(out) >= 4:
            break
        try:
            out[t if t not in out else f"{t}#{len(out)}"] = pit.fetch(c["cik"], c["accession"], d["document"], 0, TEXT_CHARS)["text"]
        except Refused:
            continue
        except Exception as ex:  # noqa: BLE001
            print("   fetch failed", c["accession"], d["document"], type(ex).__name__, file=sys.stderr)
    TEXTS.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out), encoding="utf-8")
    return out


def pool() -> int:
    log = config.data_dir() / "logs" / "edgar_pit_week3.jsonl"
    seen, rows = set(), []
    for e in dev_episodes():
        cik = int(e["cik"])
        pit = PointInTimeEdgar.for_episode(cik, e["target_adsh"], log_path=log)
        cands = tl.timeline(pit, cik, e["window_open"], pit.cutoff_date, tl.issuing_subsidiaries(cik))
        new = 0
        for c in tl.to_json(cands):
            if c["accession"] in seen:
                continue
            seen.add(c["accession"])
            c["episode"] = e["episode_id"]
            c["company"] = e["company"]
            texts_for(pit, c)
            rows.append(c)
            new += 1
        print(f"{e['episode_id']:22s} {e['company'][:16]:16s} {len(cands):3d} candidates, {new:3d} new", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    POOL.write_text(json.dumps(rows, indent=0), encoding="utf-8")
    print(f"\npool: {len(rows)} filings; {dict(Counter(r['family'] for r in rows))}")
    return 0


def load_texts(acc: str) -> dict[str, str]:
    p = TEXTS / f"{acc}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def sample() -> int:
    if LABELS.exists() and any(x.get("relevant") is not None for x in json.loads(LABELS.read_text(encoding="utf-8"))["items"]):
        raise SystemExit("labels exist; the labelled set is not redrawn")
    rows = json.loads(POOL.read_text(encoding="utf-8"))
    rows.sort(key=lambda r: r["accession"])
    rng = random.Random(SEED)
    rand = rng.sample(rows, 30)
    taken = {r["accession"] for r in rand}
    debty = [r for r in rows if r["accession"] not in taken
             and tr.DEBT_WORDS.search(tr._strip_boilerplate(" ".join(load_texts(r["accession"]).values())))]
    hard = rng.sample(debty, 20)
    items = []
    for stratum, group in (("random", rand), ("debt-vocabulary", hard)):
        for r in group:
            items.append({"accession": r["accession"], "cik": r["cik"], "company": r["company"], "form": r["form"],
                          "items": r["items"], "filing_date": r["filing_date"], "stratum": stratum,
                          "documents": [d["type"] for d in r["documents"]],
                          "relevant": None, "event_type": None, "note": None})
    LABELS.write_text(json.dumps({"about": "Week 3 triage labelled set; see scripts/triage_eval.py", "seed": SEED,
                                  "definition": "graph/nodes/triage.py module docstring", "items": items}, indent=1),
                      encoding="utf-8")
    print(f"sampled {len(items)}: {Counter(i['form'] for i in items)}; debt-vocabulary pool {len(debty)} of {len(rows)}")
    return 0


def run(model: str) -> int:
    rows = json.loads(POOL.read_text(encoding="utf-8"))
    results, t0 = [], time.time()
    for i, r in enumerate(rows):
        res = tr.triage(r["form"], r["items"], load_texts(r["accession"]), r["accession"], model=model)
        d = tr.to_json(res)
        d.update({"company": r["company"], "filing_date": r["filing_date"], "family": r["family"]})
        results.append(d)
        if res.decided_by == "model":
            print(f"  [{i:4d}] model {r['company'][:14]:14s} {r['form']:6s} {','.join(r['items']):18s} -> "
                  f"{res.relevant!s:5s} {res.event_type:24s} {res.seconds:.1f}s", flush=True)
    (OUT / f"triage_{model.replace(':', '_')}.json").write_text(json.dumps(results, indent=0), encoding="utf-8")
    print(f"\n{len(results)} filings in {time.time() - t0:.0f}s; decided by {dict(Counter(r['decided_by'] for r in results))}")
    return 0


def labels_md() -> None:
    """docs/triage_labels.md — the labelled set for a human reader (the JSON is the source)."""
    d = json.loads(LABELS.read_text(encoding="utf-8"))
    lab = d["items"]
    n_rel = sum(bool(x["relevant"]) for x in lab)
    L = ["# Triage labelled set (week 3)\n",
         "> Generated by `scripts/triage_eval.py report` from `manifests/triage_labels.json` (the source). "
         f"Drawn by `triage_eval.py sample` (seed {d['seed']}): 30 filings at random from the dev pool and 20 at random "
         "from the filings that use any debt word. Definition: the docstring of `src/ai_debt_tracker/graph/nodes/triage.py`.\n",
         f"**Labelled by:** {d.get('labelled_by', 'not recorded')}. **On:** {d.get('labelled_on', 'not recorded')}. "
         "Labels are never changed after triage has run.\n",
         f"**{n_rel} of {len(lab)}** are debt-relevant.\n",
         "| # | Company | Form | Items | Filed | Stratum | Debt-relevant | Event | Why |", "|---|---|---|---|---|---|---|---|---|"]
    for i, x in enumerate(lab):
        L.append(f"| {i} | {x['company']} | {x['form']} | {', '.join(x['items']) or '—'} | {x['filing_date']} | {x['stratum']} | "
                 f"{'yes' if x['relevant'] else 'no'} | {x['event_type'] if x['relevant'] else '—'} | "
                 f"{(x['note'] or '').replace('|', '/')} |")
    (ROOT / "docs" / "triage_labels.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def report(model: str) -> int:
    res = {r["accession"]: r for r in json.loads((OUT / f"triage_{model.replace(':', '_')}.json").read_text(encoding="utf-8"))}
    lab = json.loads(LABELS.read_text(encoding="utf-8"))["items"]
    assert all(x["relevant"] is not None for x in lab), "label every item before scoring"
    labels_md()
    pos = [x for x in lab if x["relevant"]]
    neg = [x for x in lab if not x["relevant"]]
    tp = [x for x in pos if res[x["accession"]]["relevant"]]
    fp = [x for x in neg if res[x["accession"]]["relevant"]]
    ev_ok = [x for x in tp if res[x["accession"]]["event_type"] == x["event_type"]]
    by_stratum = defaultdict(lambda: Counter())
    for x in lab:
        s = by_stratum[x["stratum"]]
        s["n"] += 1
        s["pos"] += bool(x["relevant"])
        s["tp"] += bool(x["relevant"] and res[x["accession"]]["relevant"])
        s["fp"] += bool(not x["relevant"] and res[x["accession"]]["relevant"])
    # Week 2's announcements: every filing found announcing a bond change must be kept by triage
    changes = json.loads((config.data_dir() / "week2" / "changes_dev.json").read_text())
    ann = sorted({c["document"] for c in changes if c.get("document") and c["document"] in res})
    ann_kept = [a for a in ann if res[a]["relevant"]]
    allr = list(res.values())
    dec = Counter(r["decided_by"] for r in allr)
    secs = [r["seconds"] for r in allr if r["decided_by"] == "model"]
    recall = len(tp) / max(len(pos), 1)
    L = ["# Triage — which filings are about debt (week 3)\n",
         f"> Generated by `scripts/triage_eval.py report {model}`. Triage: `src/ai_debt_tracker/graph/nodes/triage.py` "
         "(rules first, the model only for the doubtful). Labelled set: `manifests/triage_labels.json` "
         "([`triage_labels.md`](triage_labels.md)). Every decision: `$AI_DEBT_DATA/week3/`.\n",
         "## The week 3 check\n",
         f"**Recall on the labelled set: {len(tp)} of {len(pos)} debt-relevant filings found = {recall:.0%}** "
         f"(pass line ≥ 95%, set in DESIGN.md §11). Precision: {len(tp)} of {len(tp) + len(fp)} filings it kept are "
         f"relevant ({len(tp) / max(len(tp) + len(fp), 1):.0%}). Event type right on {len(ev_ok)} of {len(tp)} found.\n",
         "| Stratum | Filings | Debt-relevant | Found | False alarms |", "|---|---|---|---|---|"]
    for k, s in by_stratum.items():
        L.append(f"| {k} | {s['n']} | {s['pos']} | {s['tp']} | {s['fp']} |")
    L += ["\nThe *random* stratum is a plain random draw from the pool, so its share of debt-relevant filings estimates "
          "the share in the whole window; the *debt-vocabulary* stratum adds the hard cases.\n",
          "## Every announcement Week 2 found\n",
          f"Of the {len(ann)} filings that Week 2's change search found announcing a new bond or an early repayment "
          f"(`docs/changes_dev.md`), triage keeps **{len(ann_kept)}**.\n"]
    for a in ann:
        if a not in ann_kept:
            r = res[a]
            what = sorted({f"{c['change']} {c.get('coupon_pct')}% {c.get('maturity_year')}" for c in changes if c.get("document") == a})
            L.append(f"- **dropped** {r['company']} {r.get('family', '')} {r['filing_date']} `{a}` (announces: {'; '.join(what)}) — "
                     f"{r['decided_by']}: {r['evidence'][:160] or 'no evidence quoted'}")
    L += ["",
          "## The whole dev pool\n",
          f"{len(allr)} candidate filings: decided by " + ", ".join(f"{k} {v}" for k, v in sorted(dec.items()))
          + f". The model was asked about {dec.get('model', 0)} ({dec.get('model', 0) / max(len(allr), 1):.0%}), "
          + (f"median {sorted(secs)[len(secs) // 2]:.1f} s each" if secs else "")
          + f"; model answers that did not parse (cut off mid-string), kept for the reader: "
          f"{sum(r['evidence'].startswith('[model answer did not parse') for r in allr)}. "
          f"Of the {sum(r['relevant'] for r in allr if r['decided_by'] == 'model')} filings the model kept, "
          f"{sum(r['evidence'].startswith('[quote not found') for r in allr)} quoted evidence that is not in the text "
          "(flagged in the record; the filing is still kept). "
          f"{sum(r['relevant'] for r in allr)} filings kept as debt-relevant "
          f"({sum(r['relevant'] for r in allr) / max(len(allr), 1):.0%}).\n",
          "| Rule | What it decides | Filings | Kept |", "|---|---|---|---|"]
    rule_text = {"rule R1": "8-K item 2.03 / 2.04", "rule R2": "424B cover: notes vs equity", "rule R3": "FWP term sheet for notes",
                 "rule R4": "debt announcement in the lead", "rule R5": "no debt vocabulary", "model": "doubtful → qwen3:4b (model judgment)"}
    for k in ("rule R1", "rule R2", "rule R3", "rule R4", "rule R5", "model"):
        rs = [r for r in allr if r["decided_by"] == k]
        L.append(f"| {k} | {rule_text[k]} | {len(rs)} | {sum(r['relevant'] for r in rs)} |")
    misses = [x for x in pos if not res[x["accession"]]["relevant"]]
    L += ["\n## Misses and false alarms on the labelled set\n"]
    for x in misses:
        r = res[x["accession"]]
        L.append(f"- **missed** {x['company']} {x['form']} {x['filing_date']} `{x['accession']}` ({x['event_type']}) — "
                 f"decided by {r['decided_by']}: {r['evidence'][:160]}")
    for x in fp:
        r = res[x["accession"]]
        L.append(f"- **false alarm** {x['company']} {x['form']} {x['filing_date']} `{x['accession']}` — {r['decided_by']}, "
                 f"called it {r['event_type']}: {r['evidence'][:160]}")
    if not misses and not fp:
        L.append("None.")
    wrong_ev = [x for x in tp if res[x["accession"]]["event_type"] != x["event_type"]]
    if wrong_ev:
        L += ["\nFound, but with a different event type from the label:\n"]
        for x in wrong_ev:
            r = res[x["accession"]]
            L.append(f"- {x['company']} {x['form']} {x['filing_date']} `{x['accession']}` — label {x['event_type']}, "
                     f"triage {r['event_type']} ({r['decided_by']})")
    L += ["\n## Notes on this run (2026-10-31)\n",
          "- **The first run crashed** at filing 123 of 593: a model answer ran past its 300-token cap and came back as "
          "unterminated JSON. Nothing from that run was saved or scored. Fix (in `triage.py`, before any scoring): an "
          "answer that does not parse keeps the filing, flagged — triage is a recall-first filter. Then a full rerun.",
          "- **This report found a Week 2 defect (P40).** Its first version showed 21 of 22 Week 2 announcements kept; the "
          "one 'dropped' was a Core Scientific earnings release that `explain_changes.py` had credited with the 0% 2031 "
          "convertibles because \"0%\" matched inside \"escalates 20%\" near \"Nov 2031\" in a lease table. The coupon "
          "must now start a number; the notes are credited to the December 2024 8-K that announced them (kept by rule R1). "
          "Week 2's counts did not change.",
          "- **Seen while labelling, not changed** (changing rules after reading the labelled set would tune triage to "
          "it): an 8-K printing `Item1.01` without a space defeats `_strip_boilerplate`, so its lead starts at the next "
          "item; a preliminary 424B2 whose cover leaves the coupon and year blank (`% Senior Notes due 20`) escapes rule R2 "
          "and was kept by R4 on the cross-reference \"Optional Redemption of the Notes\" — kept, but for the wrong reason "
          "(event type redemption). Both go to Week 4 with a fresh "
          "check."]
    L += ["\n## Who decided what\n",
          "Rule decisions are code. Model decisions are **model judgments** (P8), flagged `model_judgment: true` in every "
          "record, with a quoted piece of evidence checked against the text. The labels are Claude's reading of each "
          "filing against the definition (a model judgment too, made before triage was run, by a different model than the "
          "one under test).\n"]
    (ROOT / "docs" / "triage.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[3:12]))
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    model = sys.argv[2] if len(sys.argv) > 2 else "qwen3:4b"
    sys.exit({"pool": pool, "sample": sample}.get(cmd, lambda: None)() if cmd in ("pool", "sample")
             else run(model) if cmd == "run" else report(model))
