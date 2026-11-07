"""Week 4: the event reader against baselines B1 (regex) and B2 (one model call) — DESIGN.md §11 week 4.

The week 4 check: **the reader beats B1 on field accuracy on the labelled documents.** The labelled
documents are the 24 debt-relevant filings of Week 3's triage set (`manifests/triage_labels.json`);
what each one announces — instrument by instrument: action, kind, currency, principal, coupon,
maturity year — is labelled in `manifests/reader_truth.json`, **before** any of the three methods is
run on them.

  dev <method>     develop on the Week 1 bake-off documents (truth from the next report's XBRL plus the
                   recorded corrections), leaving out the 4 that are also in the evaluation set
  view             print each evaluation filing's debt passages, for labelling the truth
  run <method>     run reader | b1 | b2 on the 24 evaluation filings → $AI_DEBT_DATA/week4/reader_<method>.json
  report           score every method that has run; writes docs/reader.md

Every document is opened through `edgar_pit` at its episode's cut-off (the `docs` store), exactly as
the agent will read it. The reader and B2 use `qwen3:4b` through Ollama, temperature 0.

**Scoring.** In each filing, true and predicted instruments are paired one to one (Hungarian
assignment on how many fields agree). Fields: coupon (±0.005 pp, P17), maturity year, principal (same
currency, within 1%) — together the *field accuracy* — and the action (new / exit / amend), shown
apart. A predicted instrument paired with nothing, or agreeing on no field, is an *extra*.

Usage:  python scripts/reader_eval.py dev|run reader|b1|b2   ·   view   ·   report
"""

from __future__ import annotations

import csv
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

from ai_debt_tracker import config
from ai_debt_tracker.documents.store import DocumentStore
from ai_debt_tracker.eval.baselines import regex_reader, single_call
from ai_debt_tracker.graph.nodes import reader as rd
from ai_debt_tracker.ledger.parsers import rates_match
from ai_debt_tracker.mcp_servers.edgar_pit_core import PointInTimeEdgar

ROOT = Path(__file__).resolve().parents[1]
OUT = config.data_dir() / "week4"
POOL = config.data_dir() / "week3" / "pool.json"
BAKEOFF = config.data_dir() / "week1" / "bakeoff" / "set.json"
LABELS = ROOT / "manifests" / "triage_labels.json"
TRUTH = ROOT / "manifests" / "reader_truth.json"
LOG = config.data_dir() / "logs" / "edgar_pit_week4.jsonl"
METHODS = ("b1", "b2", "reader")
NAMES = {"b1": "B1 regex", "b2": "B2 one call, model types the numbers", "reader": "Event reader (points, code parses)"}


def episodes() -> dict:
    with open(ROOT / "manifests" / "dev.csv", encoding="utf-8") as f:
        return {e["episode_id"]: e for e in csv.DictReader(line for line in f if not line.startswith("#"))}


def eval_set() -> list[dict]:
    pool = {r["accession"]: r for r in json.loads(POOL.read_text(encoding="utf-8"))}
    lab = json.loads(LABELS.read_text(encoding="utf-8"))["items"]
    return [pool[x["accession"]] | {"label": x} for x in lab if x["relevant"]]


def reading_docs(row: dict) -> list[dict]:
    """The documents the reader reads: the main document and the press-release exhibits (EX-99).
    Indentures and agreements (EX-4, EX-10, EX-1) are left to a later round (ablation A2)."""
    form = row["form"]
    main = [d for d in row["documents"] if d["type"] == form or d["type"].startswith(form[:4])][:1]
    ex99 = [d for d in row["documents"] if d["type"].startswith("EX-99")]
    return [d for d in main + ex99 if d["document"].lower().endswith((".htm", ".html", ".txt"))]


_pits: dict = {}


def pit_for(cik: int, episode: str) -> PointInTimeEdgar:
    """The episode's point-in-time view. Its cut-off is pinned to the *parent* company's target report;
    filings of an issuing subsidiary (Dell International, Broadcom's issuer) are read through it."""
    if episode not in _pits:
        e = episodes()[episode]
        _pits[episode] = PointInTimeEdgar.for_episode(int(e["cik"]), e["target_adsh"], log_path=LOG)
    return _pits[episode]


def call(prompt, schema, model, num_predict, num_ctx):
    content, _ = rd.call_model(prompt, schema, model, num_predict=num_predict, num_ctx=num_ctx)
    return content


def predict(method: str, cik: int, episode: str, accession: str, form: str, docs: list[dict]) -> dict:
    pit = pit_for(cik, episode)
    t0 = time.time()
    if method == "reader":
        store = DocumentStore(pit)
        parsed = [store.open(f"{cik}/{accession}/{d['document']}") for d in docs]
        r = rd.read_filing(parsed, accession, form)
        return {"instruments": [rd.asdict(e) for e in r.events], "seconds": r.seconds, "passages": r.passages,
                "error": r.error, "raw": r.raw}
    if method == "b1":
        store = DocumentStore(pit)
        texts = []
        for d in docs:
            doc = store.open(f"{cik}/{accession}/{d['document']}")
            texts += [s["text"] for s in doc.sentences] + [" | ".join(r) for t in doc.tables for r in t.rows]
        return {"instruments": regex_reader.extract(texts), "seconds": round(time.time() - t0, 2)}
    texts = [pit.fetch(cik, accession, d["document"], 0, single_call.VISIBLE_CHARS)["text"] for d in docs]
    ins, secs, bad = single_call.extract(texts, call)
    return {"instruments": ins, "seconds": secs, "unparsed": bad}


# ------------------------------------------------------------------------------------ scoring
def _agree(t: dict, p: dict) -> dict:
    out = {}
    if t.get("coupon_pct") is not None:
        out["coupon"] = p.get("coupon_pct") is not None and rates_match(t["coupon_pct"], p["coupon_pct"])
    if t.get("maturity_year"):
        out["maturity"] = p.get("maturity_year") == t["maturity_year"]
    if t.get("principal"):
        out["principal"] = bool(p.get("principal")) and (p.get("currency") or "USD") == (t.get("currency") or "USD") \
            and abs(p["principal"] - t["principal"]) <= 0.01 * t["principal"]
    out["action"] = p.get("action_class") == t["action_class"]
    return out


def _numeric(t: dict, p: dict) -> int:
    """Fields that agree. A true instrument that states no value (a blank preliminary prospectus, a term
    in an exhibit not read) is matched by a prediction with the same action that invents no value."""
    if t.get("coupon_pct") is None and not t.get("maturity_year") and not t.get("principal"):
        empty = p.get("coupon_pct") is None and not p.get("maturity_year") and not p.get("principal")
        return int(empty and p.get("action_class") == t["action_class"])
    return sum(v for k, v in _agree(t, p).items() if k != "action")


def score_filing(truth: list[dict], pred: list[dict]) -> dict:
    tally = Counter()
    pairs = []
    if truth and pred:
        gain = np.array([[_numeric(t, p) + 0.5 * _agree(t, p)["action"] for p in pred] for t in truth])
        rows, cols = linear_sum_assignment(-gain)
        pairs = [(r, c) for r, c in zip(rows, cols) if gain[r, c] > 0]
    paired = {r: c for r, c in pairs}
    numeric = _numeric
    counted = 0
    for i, t in enumerate(truth):
        hit = i in paired and numeric(t, pred[paired[i]]) > 0
        if t.get("optional") and not hit:
            continue                     # disclosed in passing: counted only when a method reports it
        counted += 1
        a = _agree(t, pred[paired[i]]) if i in paired else {k: False for k in _agree(t, {})}
        for k, v in a.items():
            tally[f"{k}_n"] += 1
            tally[f"{k}_ok"] += bool(v)
        tally["found"] += hit
    useful = {c for r, c in pairs if numeric(truth[r], pred[c]) > 0}
    tally["truth"] += counted
    tally["pred"] += len(pred)
    tally["extra"] += len(pred) - len(useful)
    return dict(tally)


def summary(per: list[dict]) -> dict:
    t = Counter()
    for x in per:
        t.update(x)
    fields_ok = sum(t[f"{f}_ok"] for f in ("coupon", "maturity", "principal"))
    fields_n = sum(t[f"{f}_n"] for f in ("coupon", "maturity", "principal"))
    return {**t, "fields_ok": fields_ok, "fields_n": fields_n, "field_rate": fields_ok / max(fields_n, 1)}


# ------------------------------------------------------------------------------------ dev (bake-off)
def dev(method: str) -> int:
    from bakeoff import apply_corrections
    ev = {r["accession"] for r in eval_set()}
    items = {it["item_id"]: it for it in json.loads(BAKEOFF.read_text(encoding="utf-8"))}
    apply_corrections(items)
    per, rows = [], []
    for it in items.values():
        if it["accession"] in ev:
            continue
        truth = [{"action_class": t["action"], "currency": t["currency"], "principal": t["principal"],
                  "coupon_pct": t["coupon_pct"], "maturity_year": t["maturity_year"]} for t in it["truth"]]
        p = predict(method, it["cik"], it["episode"], it["accession"], it["form"], [{"document": it["document"]}])
        s = score_filing(truth, p["instruments"])
        per.append(s)
        rows.append({"item": it["item_id"], "company": it["company"], "score": s, **p})
        print(f"  {it['company'][:14]:14s} {it['family']:12s} truth {s['truth']} pred {s['pred']} extra {s['extra']} "
              f"fields {sum(s.get(f + '_ok', 0) for f in ('coupon', 'maturity', 'principal'))}/"
              f"{sum(s.get(f + '_n', 0) for f in ('coupon', 'maturity', 'principal'))} {p['seconds']:.1f}s", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"dev_{method}.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    s = summary(per)
    print(f"\nDEV {method}: {len(per)} documents; fields {s['fields_ok']}/{s['fields_n']} = {s['field_rate']:.0%}; "
          f"coupon {s['coupon_ok']}/{s['coupon_n']} maturity {s['maturity_ok']}/{s['maturity_n']} "
          f"principal {s['principal_ok']}/{s['principal_n']} action {s['action_ok']}/{s['action_n']}; extra {s['extra']}")
    return 0


# ------------------------------------------------------------------------------------ evaluation
def view() -> int:
    """For labelling: the debt passages of each evaluation filing, as the reader would select them,
    plus every sentence that names an amount and a debt word (so the labeller sees more than the reader)."""
    for i, row in enumerate(eval_set()):
        pit = pit_for(row["cik"], row["episode"])
        store = DocumentStore(pit)
        print(f"\n######## [{i}] {row['company']} {row['form']} {row['filing_date']} {row['accession']} "
              f"label={row['label']['event_type']}")
        for k, d in enumerate(reading_docs(row)):
            doc = store.open(f"{row['cik']}/{row['accession']}/{d['document']}")
            print(f"  -- d{k} {d['type']} {d['document']}: {len(doc.sentences)} sentences, {len(doc.tables)} tables")
            for s in doc.sentences[:400]:
                t = s["text"]
                if rd.DEBT_A.search(t) and (rd.AMOUNT_A.search(t) or rd.RATE_A.search(t)):
                    print(f"     [{s['id']}] {t[:300]}")
            for tb in doc.tables[:30]:
                for j, r in enumerate(tb.rows[:25]):
                    t = " | ".join(r)
                    if rd.TERM_ROW.search(t) or rd.RATE_A.search(t):
                        print(f"     [{tb.id}.r{j}] {t[:300]}")
    return 0


def run(method: str) -> int:
    assert TRUTH.exists(), "label the truth (manifests/reader_truth.json) before running any method on the set"
    rows = []
    for row in eval_set():
        p = predict(method, row["cik"], row["episode"], row["accession"], row["form"], reading_docs(row))
        rows.append({"accession": row["accession"], "company": row["company"], "form": row["form"], **p})
        print(f"  {row['company'][:14]:14s} {row['form']:6s} {len(p['instruments'])} instruments {p['seconds']:.1f}s"
              + (f" ERROR {p['error']}" if p.get("error") else ""), flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"reader_{method}.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    return 0


def truth_check() -> dict:
    """A machine check of the hand-labelled truth: every new bond labelled with a coupon and a year should
    appear in the episode's target report (the next 10-Q/10-K, its own XBRL — the answer key) with the
    same coupon (P17 tolerance) and year, unless it settled after that report's period. Counts, and the
    ones not found, for the report."""
    pool = {r["accession"]: r for r in json.loads(POOL.read_text(encoding="utf-8"))}
    eps = episodes()
    found, missing, n, p_n, p_ok = 0, [], 0, 0, 0
    for f in json.loads(TRUTH.read_text(encoding="utf-8"))["filings"]:
        e = eps[pool[f["accession"]]["episode"]]
        path = config.data_dir() / "answer_key" / e["cik"] / f"{e['target_adsh']}.json"
        key = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"instruments": []}
        for t in f["instruments"]:
            if t.get("optional") or t["action_class"] != "new" or t.get("coupon_pct") is None or not t.get("maturity_year"):
                continue
            n += 1
            same = [i for i in key["instruments"] if i.get("rate") is not None and rates_match(i["rate"], t["coupon_pct"])
                    and i.get("maturity_year") == t["maturity_year"]]
            found += bool(same)
            faces = [i["face"] for i in same if i.get("face") and (i.get("face_uom") or "USD") == t["currency"]]
            if faces and t.get("principal"):
                p_n += 1
                p_ok += any(abs(x - t["principal"]) <= 0.01 * t["principal"] for x in faces)
            if not same:
                missing.append(f"{f['company']} {t['coupon_pct']}% {t['maturity_year']} (target {e['target_period']})")
    return {"n": n, "found": found, "missing": missing, "principal_n": p_n, "principal_ok": p_ok}


NOTES = [
    "- **The check passes, and B2 is better at numbers.** The one-call baseline B2 — the model typing each value as a "
    "number — read 160 of 160 fields on this set (and 130 of 132 on the development documents). The reader read 157 of "
    "167. On pricing documents like these, a 4B model reading numbers is already reliable; what the reader adds is not "
    "accuracy but **provenance**: every value it reports was found in a cited passage and parsed by code, and a value "
    "the model 'copied' but no passage contains is refused. None of B2's numbers is tied to a sentence.",
    "- **What the refusal caught.** Of the 24 dropped copies, **8 are currency signs the model rewrote while 'copying'**: "
    "\"$1,500,000,000\" where Alphabet's 8-K says \"€1,500,000,000\" (five tranches), Digital Realty's €850 m and "
    "Equinix's €600 m likewise, and Equinix's CHF 100 m as \"$100 million\". Refused, those principals are missing "
    "rather than wrong. The prompt's own example amount is in dollars; that is the likely pull. The other **16 are the "
    "word \"null\" written as text** for a value the filing does not state — a bookkeeping bug (the schema allows a "
    "string), with no effect on any score, since the field is empty either way; fixed in code for the next run.",
    "- **Three reader defects, recorded and not fixed against this set** (fixing them here would turn it into a "
    "calibration set): (1) the currency sign rewritten when copying; (2) passage selection dropped Super Micro's "
    "\"$500 million term loan facility\" sentence — an amount and a debt word but no rate or year scores below the "
    "threshold — so that filing had no passages at all; (3) on a preliminary prospectus with every term blank (Equinix, "
    "Aug 2024) the model listed the cover's table of *existing* notes: 15 of the reader's 29 extras.",
    "- **Development, before the evaluation set was touched**: three rounds on the 25 bake-off documents not in this set. "
    "Round 1: 95% of fields, 25 extras. Round 2 (prompt: what not to list, what each action means; code: a tranche "
    "repeated without its amount is merged): 9 extras, but two long prospectuses ran past the output cap. Round 3 (code: "
    "a cut-off answer keeps the instruments it completed, flagged): 96%, 10 extras. Then frozen and run here once.",
    "- **Small and easy.** 24 filings, most of them pricing documents of large investment-grade issuers; 62 of the 66 "
    "instruments are new notes. Loans, amendments and redemptions — where reading is harder — are 4. EX-4/EX-10 "
    "exhibits are not read yet (Applied Digital's note terms live only there).",
    "- **Who decided what.** Which instruments a filing announces, and each one's action, are model judgments (P8), "
    "flagged in every event. The truth is Claude's reading, checked by machine only for new bonds' coupon, year and "
    "principal against the next report.\n"]


def truth_md(meta: dict) -> None:
    """docs/reader_truth.md — the truth, for a human reader (the JSON is the source)."""
    L = ["# Event-reader truth (week 4)\n",
         "> Generated by `scripts/reader_eval.py report` from `manifests/reader_truth.json` (the source). "
         f"Labelled by {meta['labelled_by']}, on {meta['labelled_on']}, before any method was run on these filings.\n",
         f"**Rules:** {meta['rules']}\n",
         "| # | Company | Form | Filed | Action | Kind | Currency | Principal | Coupon | Maturity | Note |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, f in enumerate(meta["filings"]):
        for j, t in enumerate(f["instruments"]):
            L.append(f"| {i} | {f['company']} | {f['form']} | {f['filing_date']} | {t['action_class']}"
                     f"{' (optional)' if t.get('optional') else ''} | {t['kind']} | {t['currency']} | "
                     f"{_fmt(t['principal'], 'principal')} | {_fmt(t['coupon_pct'], 'coupon')} | "
                     f"{_fmt(t['maturity_year'], 'year')} | {f['note'].replace('|', '/') if j == 0 else ''} |")
    (ROOT / "docs" / "reader_truth.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def _fmt(v, kind):
    if v is None:
        return "—"
    if kind == "principal":
        return f"{v / 1e6:,.1f} m" if v < 1e9 else f"{v / 1e9:,.3g} bn"
    return f"{v:g}" if kind == "coupon" else str(v)


def report() -> int:
    truth = {t["accession"]: t for t in json.loads(TRUTH.read_text(encoding="utf-8"))["filings"]}
    runs = {m: {r["accession"]: r for r in json.loads((OUT / f"reader_{m}.json").read_text(encoding="utf-8"))}
            for m in METHODS if (OUT / f"reader_{m}.json").exists()}
    res, per_filing = {}, {}
    for m, rr in runs.items():
        per = []
        for acc, t in truth.items():
            s = score_filing(t["instruments"], rr[acc]["instruments"])
            per.append(s)
            per_filing.setdefault(acc, {})[m] = s
        secs = sorted(r["seconds"] for r in rr.values())
        res[m] = summary(per) | {"median_s": secs[len(secs) // 2], "max_s": secs[-1],
                                 "errors": sum(bool(r.get("error")) for r in rr.values()),
                                 "unparsed": sum(r.get("unparsed", 0) for r in rr.values())}
    n_ins = sum(len(t["instruments"]) for t in truth.values())
    kinds = Counter(i["action_class"] for t in truth.values() for i in t["instruments"])
    meta = json.loads(TRUTH.read_text(encoding="utf-8"))
    L = ["# The event reader against B1 and B2 (week 4)\n",
         "> Generated by `scripts/reader_eval.py report`. Reader: `src/ai_debt_tracker/graph/nodes/reader.py`; B1: "
         "`eval/baselines/regex_reader.py`; B2: `eval/baselines/single_call.py`. Truth: `manifests/reader_truth.json` "
         "([`reader_truth.md`](reader_truth.md)). Every answer: `$AI_DEBT_DATA/week4/`.\n",
         "## The week 4 check\n"]
    if "reader" in res and "b1" in res:
        r, b = res["reader"], res["b1"]
        verdict = "**passes**" if r["field_rate"] > b["field_rate"] else "**does not pass**"
        L.append(f"The reader reads **{r['fields_ok']} of {r['fields_n']} fields** right ({r['field_rate']:.0%}); B1 reads "
                 f"{b['fields_ok']} of {b['fields_n']} ({b['field_rate']:.0%}). The check (the reader beats B1 on field "
                 f"accuracy, DESIGN.md §11) {verdict}.\n")
    L += [f"**The set:** the {len(truth)} debt-relevant filings of Week 3's labelled triage set, announcing {n_ins} "
          f"instruments ({', '.join(f'{k} {v}' for k, v in kinds.most_common())}). Labelled by {meta['labelled_by']}, "
          f"on {meta['labelled_on']}, before any method was run on them.\n",
          (lambda c: f"**A machine check of that truth:** of the {c['n']} new bonds it labels with a coupon and a year, "
                     f"**{c['found']}** appear in the company's next 10-Q/10-K XBRL (the answer key) with the same coupon and "
                     f"year, and where the key states a face amount in the same currency the labelled principal agrees on "
                     f"**{c['principal_ok']} of {c['principal_n']}**."
                     + (f" Not found: {'; '.join(c['missing'])}." if c["missing"] else "") + " Loans, amendments, exits and "
                     "values left blank are checked only by the reading.\n")(truth_check()),
          "| Method | Fields right | Coupon | Maturity | Principal | Action | Instruments found | Extra | Median s / filing | Max s |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for m in METHODS:
        if m not in res:
            continue
        s = res[m]
        L.append(f"| {NAMES[m]} | **{s['fields_ok']}/{s['fields_n']} = {s['field_rate']:.0%}** | {s['coupon_ok']}/{s['coupon_n']} | "
                 f"{s['maturity_ok']}/{s['maturity_n']} | {s['principal_ok']}/{s['principal_n']} | {s['action_ok']}/{s['action_n']} | "
                 f"{s['found']}/{s['truth']} | {s['extra']} | {s['median_s']:.1f} | {s['max_s']:.1f} |")
    L.append("\n*Fields right* counts coupon + maturity year + principal over the true instruments that state them. "
             "*Instruments found*: true instruments paired with a prediction that agrees on at least one field. "
             "*Extra*: predictions that are no true instrument (or agree on nothing).\n")
    if "reader" in runs:
        c = Counter()
        for r in runs["reader"].values():
            for e in r["instruments"]:
                for f, v in e["cites"].items():
                    c[v["found"]] += 1
                c["dropped"] += len(e["dropped"])
        L += ["## Where the reader's numbers come from\n",
              f"Every value the reader reports was parsed by code from words in the filing. Of the values it pointed at, "
              f"**{c['cited']}** were in the passage it cited and **{c['relocated']}** were in a different passage than the "
              f"one cited (kept, with the true id). **{c['dropped']}** copied values were in no passage at all and were "
              "dropped rather than used.\n"]
    L += ["## Filing by filing\n", "| # | Company | Form | True | " + " | ".join(NAMES[m].split(' ')[0] for m in METHODS if m in res)
          + " |", "|---|---|---|---|" + "---|" * len(res)]
    for i, (acc, t) in enumerate(truth.items()):
        cells = []
        for m in METHODS:
            if m in res:
                s = per_filing[acc][m]
                ok = sum(s.get(f + "_ok", 0) for f in ("coupon", "maturity", "principal"))
                n = sum(s.get(f + "_n", 0) for f in ("coupon", "maturity", "principal"))
                cells.append(f"{ok}/{n}" + (f", +{s['extra']}" if s["extra"] else ""))
        L.append(f"| {i} | {t['company']} | {t['form']} | {len(t['instruments'])} | " + " | ".join(cells) + " |")
    L.append("\nEach cell: fields right / fields stated, and `+n` extra instruments.\n")
    L += ["## What the numbers say\n"] + NOTES
    truth_md(meta)
    (ROOT / "docs" / "reader.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:14]))
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    arg = sys.argv[2] if len(sys.argv) > 2 else "reader"
    sys.exit(dev(arg) if cmd == "dev" else run(arg) if cmd == "run" else view() if cmd == "view" else report())
