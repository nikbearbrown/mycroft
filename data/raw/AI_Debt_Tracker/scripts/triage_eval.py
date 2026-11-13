"""Week 3: build the triage evaluation (DESIGN.md §11 week 3) and score triage against it.

  pool      every candidate filing in every **dev** episode's window, for the 25 AI companies and
            their issuing subsidiaries, from the `timeline` node through `edgar_pit` at each episode's
            cut-off; the start of each readable document is cached as text
  sample 3  draw the 50-filing labelled set by a fixed rule (seed 20261031): 30 at random from the whole
            pool — so the share of debt filings is honest — and 20 at random from the filings with any
            debt vocabulary, so there are enough hard cases. Writes manifests/triage_labels.json with
            empty labels (the human-readable docs/triage_labels.md is written by `report`)
  sample 4  Week 4's fresh set: the same rule, seed 20261107, from the filings not in Week 3's set
            (manifests/triage_labels_w4.json)
  run       run triage (rules, then qwen3:4b on the doubtful) over the whole pool (Week 4: into week4/)
  report    score triage on the labelled sets — the week 4 check is recall ≥ 95% on the fresh set — plus
            recall on every filing that Week 2's change search found announcing a bond change; writes
            docs/triage.md, docs/triage_labels.md and docs/triage_labels_w4.md

Labels are filled in between `sample` and `run`, by reading each filing against the definition in
`graph/nodes/triage.py`, and are never changed after `run` (they are the answer key for triage).

Usage:  python scripts/triage_eval.py pool | sample 3|4 | run [model] | report [model]
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
OUT4 = config.data_dir() / "week4"
OUT5 = config.data_dir() / "week5"
POOL = OUT / "pool.json"
TEXTS = OUT / "texts"
LABELS = ROOT / "manifests" / "triage_labels.json"
LABELS_W4 = ROOT / "manifests" / "triage_labels_w4.json"
LABELS_W5 = ROOT / "manifests" / "triage_labels_w5.json"
SEED = 20261031
SETS = {"3": (LABELS, SEED), "4": (LABELS_W4, 20261107), "5": (LABELS_W5, 20261113)}
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


def sample(week: str = "3") -> int:
    """Draw a labelled set. Week 3: seed 20261031 from the whole pool. Week 4 (the fresh check): seed
    20261107, by the same rule, from the filings *not* in Week 3's set — Week 3's set was read while
    labelling and two rule weaknesses seen there were fixed, so it is a calibration set now."""
    path, seed = SETS[week]
    if path.exists() and any(x.get("relevant") is not None for x in json.loads(path.read_text(encoding="utf-8"))["items"]):
        raise SystemExit("labels exist; the labelled set is not redrawn")
    rows = json.loads(POOL.read_text(encoding="utf-8"))
    if week != "3":
        earlier = [SETS[w][0] for w in sorted(SETS) if int(w) < int(week)]
        before = {x["accession"] for f in earlier for x in json.loads(f.read_text(encoding="utf-8"))["items"]}
        rows = [r for r in rows if r["accession"] not in before]
    if int(week) >= 5:
        # P45: one document filed under several accessions is one filing; a copy of a filing already labelled
        # is not fresh. Keep the first copy of each document, and drop it if any copy was in an earlier set.
        rows.sort(key=lambda r: (r["accepted"], r["accession"]))
        everything = sorted(json.loads(POOL.read_text(encoding="utf-8")), key=lambda r: (r["accepted"], r["accession"]))
        kept = tl.drop_duplicate_documents(everything, lambda r: " ".join(load_texts(r["accession"]).values()))
        dup_of_before = {r["accession"] for r in kept
                         if r["accession"] in before or any(a["accession"] in before for a in r.get("also_filed_as", []))}
        kept_acc = {r["accession"] for r in kept} - dup_of_before
        rows = [r for r in rows if r["accession"] in kept_acc]
    rows.sort(key=lambda r: r["accession"])
    rng = random.Random(seed)
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
    path.write_text(json.dumps({"about": f"Week {week} triage labelled set; see scripts/triage_eval.py", "seed": seed,
                                "definition": "graph/nodes/triage.py module docstring", "items": items}, indent=1),
                    encoding="utf-8")
    print(f"sampled {len(items)}: {Counter(i['form'] for i in items)}; debt-vocabulary pool {len(debty)} of {len(rows)}")
    return 0


def run(model: str) -> int:
    """Triage the whole dev pool. Week 5's run is written to `$AI_DEBT_DATA/week5/`, so Week 3's and Week 4's
    runs (with the rules as they were) stay as they were recorded."""
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
    OUT5.mkdir(parents=True, exist_ok=True)
    (OUT5 / f"triage_{model.replace(':', '_')}.json").write_text(json.dumps(results, indent=0), encoding="utf-8")
    print(f"\n{len(results)} filings in {time.time() - t0:.0f}s; decided by {dict(Counter(r['decided_by'] for r in results))}")
    return 0


def labels_md(week: str = "3") -> None:
    """docs/triage_labels.md (Week 3's set) or docs/triage_labels_w4.md — the labelled set for a human
    reader (the JSON is the source)."""
    path, _ = SETS[week]
    d = json.loads(path.read_text(encoding="utf-8"))
    lab = d["items"]
    n_rel = sum(bool(x["relevant"]) for x in lab)
    how = ("30 filings at random from the dev pool and 20 at random from the filings that use any debt word" if week == "3"
           else "by the same rule, from the dev filings not in Week 3's set: 30 at random and 20 at random from those "
                "that use any debt word" if week == "4"
           else "by the same rule, from the dev filings not in Week 3's or Week 4's sets, one copy per document (P45): "
                "30 at random and 20 at random from those that use any debt word")
    L = [f"# Triage labelled set (week {week})\n",
         f"> Generated by `scripts/triage_eval.py report` from `manifests/{path.name}` (the source). "
         f"Drawn by `triage_eval.py sample {week}` (seed {d['seed']}): {how}. Definition: the docstring of "
         "`src/ai_debt_tracker/graph/nodes/triage.py`.\n",
         f"**Labelled by:** {d.get('labelled_by', 'not recorded')}. **On:** {d.get('labelled_on', 'not recorded')}. "
         "Labels are never changed after triage has run.\n",
         f"**{n_rel} of {len(lab)}** are debt-relevant.\n",
         "| # | Company | Form | Items | Filed | Stratum | Debt-relevant | Event | Why |", "|---|---|---|---|---|---|---|---|---|"]
    for i, x in enumerate(lab):
        L.append(f"| {i} | {x['company']} | {x['form']} | {', '.join(x['items']) or '—'} | {x['filing_date']} | {x['stratum']} | "
                 f"{'yes' if x['relevant'] else 'no'} | {x['event_type'] if x['relevant'] else '—'} | "
                 f"{(x['note'] or '').replace('|', '/')} |")
    name = "triage_labels.md" if week == "3" else f"triage_labels_w{week}.md"
    (ROOT / "docs" / name).write_text("\n".join(L) + "\n", encoding="utf-8")


def score(lab: list[dict], res: dict) -> dict:
    pos = [x for x in lab if x["relevant"]]
    neg = [x for x in lab if not x["relevant"]]
    tp = [x for x in pos if res[x["accession"]]["relevant"]]
    fp = [x for x in neg if res[x["accession"]]["relevant"]]
    by_stratum = defaultdict(Counter)
    for x in lab:
        s = by_stratum[x["stratum"]]
        s["n"] += 1
        s["pos"] += bool(x["relevant"])
        s["tp"] += bool(x["relevant"] and res[x["accession"]]["relevant"])
        s["fp"] += bool(not x["relevant"] and res[x["accession"]]["relevant"])
    return {"pos": pos, "neg": neg, "tp": tp, "fp": fp, "by_stratum": by_stratum,
            "misses": [x for x in pos if not res[x["accession"]]["relevant"]],
            "ev_ok": [x for x in tp if res[x["accession"]]["event_type"] == x["event_type"]],
            "wrong_ev": [x for x in tp if res[x["accession"]]["event_type"] != x["event_type"]],
            "recall": len(tp) / max(len(pos), 1), "precision": len(tp) / max(len(tp) + len(fp), 1)}


def _set_section(title: str, s: dict, res: dict) -> list[str]:
    L = [f"## {title}\n",
         f"**Recall: {len(s['tp'])} of {len(s['pos'])} debt-relevant filings found = {s['recall']:.0%}** "
         f"(pass line ≥ 95%, DESIGN.md §11). Precision: {len(s['tp'])} of {len(s['tp']) + len(s['fp'])} filings it kept "
         f"are relevant ({s['precision']:.0%}). Event type right on {len(s['ev_ok'])} of {len(s['tp'])} found.\n",
         "| Stratum | Filings | Debt-relevant | Found | False alarms |", "|---|---|---|---|---|"]
    for k, v in s["by_stratum"].items():
        L.append(f"| {k} | {v['n']} | {v['pos']} | {v['tp']} | {v['fp']} |")
    L.append("")
    for x in s["misses"]:
        r = res[x["accession"]]
        L.append(f"- **missed** {x['company']} {x['form']} {x['filing_date']} `{x['accession']}` ({x['event_type']}) — "
                 f"decided by {r['decided_by']}: {r['evidence'][:160]}")
    for x in s["fp"]:
        r = res[x["accession"]]
        L.append(f"- **false alarm** {x['company']} {x['form']} {x['filing_date']} `{x['accession']}` — {r['decided_by']}, "
                 f"called it {r['event_type']}: {r['evidence'][:160]}")
    for x in s["wrong_ev"]:
        r = res[x["accession"]]
        L.append(f"- found with a different event type: {x['company']} {x['form']} {x['filing_date']} `{x['accession']}` — "
                 f"label {x['event_type']}, triage {r['event_type']} ({r['decided_by']})")
    if not (s["misses"] or s["fp"] or s["wrong_ev"]):
        L.append("No misses, false alarms or event-type differences.")
    return L + [""]


WEEK3_NOTES = [
    "- **The first run crashed** at filing 123 of 593: a model answer ran past its 300-token cap and came back as "
    "unterminated JSON. Nothing from that run was saved or scored. Fix (in `triage.py`, before any scoring): an "
    "answer that does not parse keeps the filing, flagged — triage is a recall-first filter. Then a full rerun.",
    "- **The Week 3 report found a Week 2 defect (P40).** Its first version showed 21 of 22 Week 2 announcements kept; "
    "the one 'dropped' was a Core Scientific earnings release that `explain_changes.py` had credited with the 0% 2031 "
    "convertibles because \"0%\" matched inside \"escalates 20%\" near \"Nov 2031\" in a lease table. The coupon must now "
    "start a number; the notes are credited to the December 2024 8-K that announced them (kept by rule R1).",
    "- **Seen while labelling Week 3's set, fixed in Week 4**: an 8-K printing `Item1.01` without a space defeated "
    "`_strip_boilerplate`; a preliminary 424B2 whose cover leaves the coupon and year blank (`% Senior Notes due 20`) "
    "escaped rule R2 and was kept by R4 for the wrong reason. Because those fixes came from reading Week 3's set, that set "
    "is a calibration set from Week 4 on, and Week 4 drew a fresh one."]


def report(model: str) -> int:
    """docs/triage.md. The check is recall ≥ 95% on the *fresh* labelled set — Week 5's, from Week 5's run (rules as
    fixed in Week 5: P45, P46). Week 3's and Week 4's sets are re-scored on the same run as calibrations, and the
    earlier runs are quoted as recorded."""
    name = f"triage_{model.replace(':', '_')}.json"
    res = {r["accession"]: r for r in json.loads((OUT5 / name).read_text(encoding="utf-8"))}
    res4 = {r["accession"]: r for r in json.loads((OUT4 / name).read_text(encoding="utf-8"))}
    res3 = {r["accession"]: r for r in json.loads((OUT / name).read_text(encoding="utf-8"))}
    lab3 = json.loads(LABELS.read_text(encoding="utf-8"))["items"]
    lab4 = json.loads(LABELS_W4.read_text(encoding="utf-8"))["items"]
    lab5 = json.loads(LABELS_W5.read_text(encoding="utf-8"))["items"]
    assert all(x["relevant"] is not None for x in lab3 + lab4 + lab5), "label every item before scoring"
    labels_md("3")
    labels_md("4")
    labels_md("5")
    s5, s4, s3 = score(lab5, res), score(lab4, res), score(lab3, res)
    s4_then, s3_then = score(lab4, res4), score(lab3, res3)
    # Week 2's announcements: every filing found announcing a bond change must be kept by triage
    changes = json.loads((config.data_dir() / "week2" / "changes_dev.json").read_text())
    ann = sorted({c["document"] for c in changes if c.get("document") and c["document"] in res})
    ann_kept = [a for a in ann if res[a]["relevant"]]
    allr = list(res.values())
    dec = Counter(r["decided_by"] for r in allr)
    secs = [r["seconds"] for r in allr if r["decided_by"] == "model"]
    changed = [a for a in res if a in res4 and (res[a]["relevant"], res[a]["decided_by"]) != (res4[a]["relevant"], res4[a]["decided_by"])]
    flips = Counter((res4[a]["relevant"], res[a]["relevant"]) for a in changed)
    L = ["# Triage — which filings are about debt\n",
         f"> Generated by `scripts/triage_eval.py report {model}`. Triage: `src/ai_debt_tracker/graph/nodes/triage.py` "
         "(rules first, the model only for the doubtful). Labelled sets: `manifests/triage_labels_w5.json` "
         "([`triage_labels_w5.md`](triage_labels_w5.md)), `manifests/triage_labels_w4.json` "
         "([`triage_labels_w4.md`](triage_labels_w4.md)) and `manifests/triage_labels.json` "
         "([`triage_labels.md`](triage_labels.md)). Every decision: `$AI_DEBT_DATA/week5/` (Week 5's run); "
         "`$AI_DEBT_DATA/week4/` and `$AI_DEBT_DATA/week3/` keep the earlier runs as recorded.\n"]
    L += _set_section("The triage check, third time — Week 5's fresh labelled set", s5, res)
    L += [f"The fresh set has **{len(s5['pos'])} debt-relevant filings** ({s5['by_stratum']['random']['pos']} of 30 at "
          f"random, {s5['by_stratum']['debt-vocabulary']['pos']} of 20 among filings with debt words). It was drawn after "
          "the P45 and P46 fixes, from the filings in neither earlier set, one copy per document (P45).\n"]
    L += _set_section("Week 4's labelled set, re-scored on Week 5's run (calibration since the P46 fix)", s4, res)
    L += [f"Week 4's own run, as recorded (the Week 4 check): recall {len(s4_then['tp'])} of {len(s4_then['pos'])}, "
          f"precision {len(s4_then['tp'])} of {len(s4_then['tp']) + len(s4_then['fp'])}.\n"]
    L += _set_section("Week 3's labelled set, re-scored on Week 5's run (calibration)", s3, res)
    L += [f"Week 3's own run, as recorded: recall {len(s3_then['tp'])} of {len(s3_then['pos'])}, precision "
          f"{len(s3_then['tp'])} of {len(s3_then['tp']) + len(s3_then['fp'])}, event type {len(s3_then['ev_ok'])} of "
          f"{len(s3_then['tp'])}.\n",
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
          "## The whole dev pool (Week 5's run)\n",
          f"{len(allr)} candidate filings: decided by " + ", ".join(f"{k} {v}" for k, v in sorted(dec.items()))
          + f". The model was asked about {dec.get('model', 0)} ({dec.get('model', 0) / max(len(allr), 1):.0%}), "
          + (f"median {sorted(secs)[len(secs) // 2]:.1f} s each" if secs else "")
          + f"; model answers that did not parse, kept for the reader: "
          f"{sum(r['evidence'].startswith('[model answer did not parse') for r in allr)}. "
          f"Of the {sum(r['relevant'] for r in allr if r['decided_by'] == 'model')} filings the model kept, "
          f"{sum(r['evidence'].startswith('[quote not found') for r in allr)} quoted evidence that is not in the text "
          "(flagged in the record; the filing is still kept). "
          f"{sum(r['relevant'] for r in allr)} filings kept as debt-relevant "
          f"({sum(r['relevant'] for r in allr) / max(len(allr), 1):.0%}).\n",
          f"Against Week 4's run, {len(changed)} filing{'s were' if len(changed) != 1 else ' was'} decided differently (by a different rule, or the other way): "
          + ", ".join(f"{n} {'kept' if a else 'dropped'} → {'kept' if b else 'dropped'}" for (a, b), n in sorted(flips.items()))
          + ". The model is run at temperature 0, but a filing that moves from a rule to the model (or back) can change.\n",
          "| Rule | What it decides | Filings | Kept |", "|---|---|---|---|"]
    rule_text = {"rule R1": "8-K item 2.03 / 2.04", "rule R2": "424B cover: notes vs equity", "rule R3": "FWP term sheet for notes",
                 "rule R4": "debt announcement in the lead", "rule R5": "no debt vocabulary", "model": "doubtful → qwen3:4b (model judgment)"}
    for k in ("rule R1", "rule R2", "rule R3", "rule R4", "rule R5", "model"):
        rs = [r for r in allr if r["decided_by"] == k]
        L.append(f"| {k} | {rule_text[k]} | {len(rs)} | {sum(r['relevant'] for r in rs)} |")
    L += ["\n## Notes\n"] + WEEK3_NOTES + [
          "- **Week 4's fresh set was labelled before Week 4's run**; the labels file's hash is recorded in "
          "`manifests/week4_gate.json`.",
          "- **The week 4 check does not pass (8 of 9).** The miss is IBM's preliminary euro prospectus (Feb 2025): its cover "
          "leaves even the century of the year blank (`€ % Notes due`), so the Week 4 blank-cover pattern (`% Notes due 20`) "
          "does not fire, and rule R2 then finds \"Preferred Stock\" in the cover's table of contents and calls it an equity "
          "offering. Recorded as P46 and **not fixed against this set** — a fix found here would make it a calibration set. It "
          "goes to Week 5 with a third fresh check. The Week 3 pattern this resembles was fixed for one blank form and not "
          "for its neighbour.",
          "- **One document is in both labelled sets.** Dell's October 2024 pricing term sheet was filed twice, under each "
          "co-issuer's CIK, with different accession numbers; the timeline removes co-filings by accession, so both copies "
          "are in the pool, and the fresh draw picked the second copy. Recorded as P45 (a timeline defect) and left in the set "
          "as drawn.",
          "- **The false alarms, and one probable labelling error.** Three are borderline by the labels' own convention: an "
          "earnings release recapping a note conversion (rule R4), a fee-table refiling for a share offering that names the "
          "concurrent notes (rule R2), and a warrant issued for a loan announced earlier (model). The fourth is probably the "
          "label's fault: Applied Digital's January 2025 earnings release says a subsidiary *closed* a $150 m senior secured "
          "financing with Macquarie, and the label (written from the release's lead and three debt-word passages) does not "
          "mention it. Labels are not changed after the run, so it stays a false alarm here; counted as relevant, precision "
          "would be 9 of 12 and recall 9 of 10."]
    L += ["- **Week 5: P46 and P45 fixed, then a third fresh set.** The blank-cover pattern now takes `% Notes due` with "
          "anything after it, and a base prospectus's contents list (\"Description of Preferred Stock\") no longer counts "
          "as a share sale. Co-filed copies of one document are one filing (same day, form, file name and text). Week 4's "
          "set, where P46 was found, is a calibration from now on (9 of 9 above).",
          "- **Week 5's fresh set was labelled before Week 5's run** (git blob `9d88931006c11346804e4cdbb16a3095d6ce7b4d`, "
          "unchanged after the run; `manifests/week5_gate.json`). Week 4's run over the same pool existed but was not read "
          "while labelling.",
          "- **The check passes: 15 of 15.** It is still small: one miss would have been 93%, below the line.",
          "- **Three false alarms, two of them new rule weaknesses (logged, not fixed against this set):** rule R4's "
          "tender pattern fired on a third party's *mini-tender for Alphabet's shares* (P53: a tender for shares is not a "
          "debt tender); rule R3 kept Cipher Mining's FWP for a borrowed-share offering because it names the concurrent "
          "convertible notes (P54: an FWP offering shares is not a note term sheet; Week 4's labels treat that as not "
          "relevant). The third is the model's: Intel's sale of Altera, where the debt commitment letter is the *buyer's*.",
          "- **Event types: 12 of 15.** Three closing 8-Ks under item 2.03 were typed as repayments because their text "
          "also mentions repaying or redeeming other debt with the proceeds; `event_from_text` takes the first pattern "
          "that matches anywhere in the filing. The event reader does not use triage's event type, so this costs nothing "
          "downstream yet."]
    L += ["\n## Who decided what\n",
          "Rule decisions are code. Model decisions are **model judgments** (P8), flagged `model_judgment: true` in every "
          "record, with a quoted piece of evidence checked against the text. The labels are Claude's reading of each "
          "filing against the definition (a model judgment too, made before triage was run on that set, by a different "
          "model than the one under test).\n"]
    (ROOT / "docs" / "triage.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[1:16]))
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    if cmd == "pool":
        sys.exit(pool())
    if cmd == "sample":
        sys.exit(sample(arg or "3"))
    sys.exit(run(arg or "qwen3:4b") if cmd == "run" else report(arg or "qwen3:4b"))
