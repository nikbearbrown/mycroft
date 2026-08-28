"""Run the LLM adjudicator over the golden set, then measure lift and throughput.

    python -m scripts.run_adjudication --check    # is a backend up, and which model
    python -m scripts.run_adjudication --run      # call the model, cache every reply
    python -m scripts.run_adjudication --score    # metrics from the cache, no model

The run and the scoring are separate on purpose. Every reply is cached to
docs/_adjudication_results.json with the model name, digest and quantisation
that produced it, so the numbers in docs/entity_resolution.md section 9 can be
recomputed by anyone without a GPU, and so a later model swap is visible as a
diff rather than as a silently different metric (P3).

--------------------------------------------------------------------------
What is being compared
--------------------------------------------------------------------------
  B_matcher_v1   Week 4's deterministic matcher. The baseline.
  C_v2_band      deterministic, with the model consulted only in the 0.80-0.90
                 review band and on unresolved names. The shipping candidate.
  D_v2_all       deterministic, with the model overruling everything short of
                 an exact LEI or alias match. An ablation.
  E_llm_only     the model alone, ignoring the deterministic matcher entirely.
                 Not a shipping option; it says what the model can do unaided.

The model is called once per issuer string and the reply is reused across all
four systems, because the prompt depends only on (name, title, filer). One run,
four measurements.
"""

from __future__ import annotations

import argparse
import collections
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.resolve.adjudicate import (  # noqa: E402
    AUTO_ACCEPT,
    POLICY_ALL,
    POLICY_BAND,
    POLICY_LLM_ONLY,
    POLICY_VETO,
    RESPONSE_SCHEMA,
    REVIEW_FLOOR,
    Adjudication,
    adjudicate,
    build_prompt,
    resolve_v2,
    would_consult,
)
from src.resolve.llm import DEFAULT_MODEL, load_backend  # noqa: E402
from src.resolve.match import resolve  # noqa: E402
from scripts.score_matcher import score  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "golden_set_v1.json"
CACHE = ROOT / "docs" / "_adjudication_results.json"
METRICS = ROOT / "docs" / "_adjudication_metrics.json"


def load_fixture() -> list:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["entries"]


KEY_SEP = " || "  # readable in the cache file, and absent from every issuer name


def key_of(entry) -> str:
    return f"{entry['issuer_name']}{KEY_SEP}{entry['issuer_title']}"


# --------------------------------------------------------------------------
# Run
# --------------------------------------------------------------------------


def run(model: str, limit: int | None = None, only_consulted: bool = False) -> dict:
    entries = load_fixture()
    backend = load_backend(model=model, schema=RESPONSE_SCHEMA)
    if not backend.available():
        sys.exit(
            f"no Ollama server on {backend.host}. Start one with `ollama serve`, "
            f"then `ollama pull {model}`."
        )
    installed = backend.installed_models()
    if not any(m == model or m.startswith(model.split(":")[0]) for m in installed):
        sys.exit(f"{model} is not installed. Have: {installed or 'nothing'}")

    identity = backend.describe()
    print(f"model   {identity['model']}  {identity.get('parameter_size')} "
          f"{identity.get('quantization')}  digest {identity['digest']}")
    print("warming...", end=" ", flush=True)
    warm_seconds = backend.warm()
    print(f"{warm_seconds:.1f}s")

    todo = entries
    if only_consulted:
        todo = [
            e for e in entries
            if would_consult(e["issuer_name"], e["issuer_title"], policy=POLICY_BAND)
        ]
    if limit:
        todo = todo[:limit]

    print(f"adjudicating {len(todo)} of {len(entries)} issuer strings\n")
    results, started = {}, time.perf_counter()
    for i, entry in enumerate(todo, 1):
        verdict = adjudicate(
            backend, entry["issuer_name"], entry["issuer_title"], entry.get("filer_families")
        )
        results[key_of(entry)] = {
            "id": entry["id"],
            "issuer_name": entry["issuer_name"],
            "issuer_title": entry["issuer_title"],
            "filer": entry.get("filer_families"),
            "company": verdict.company,
            "share_class": verdict.share_class,
            "confidence": verdict.confidence,
            "reason": verdict.reason,
            "seconds": round(verdict.seconds, 3),
            "prompt_tokens": verdict.prompt_tokens,
            "completion_tokens": verdict.completion_tokens,
            "error": verdict.error,
            "raw": verdict.raw[:400],
        }
        if i % 20 == 0 or i == len(todo):
            rate = i / (time.perf_counter() - started)
            print(f"  {i:>4}/{len(todo)}  {rate:.2f} rows/s")

    elapsed = time.perf_counter() - started
    payload = {
        "run": {
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "host": backend.host,
            "machine": f"{platform.system()} {platform.machine()}",
            **identity,
            "warm_seconds": round(warm_seconds, 2),
            "entries_adjudicated": len(todo),
            "wall_seconds": round(elapsed, 1),
            "temperature": 0,
            "seed": 7,
            "schema_constrained": True,
        },
        "results": results,
    }
    CACHE.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"\nwrote {CACHE.relative_to(ROOT)}  ({elapsed:.0f}s, "
          f"{len(todo) / elapsed:.2f} rows/s)")
    return payload


# --------------------------------------------------------------------------
# Score
# --------------------------------------------------------------------------


def _cached_adjudication(record) -> Adjudication:
    return Adjudication(
        company=record["company"],
        share_class=record["share_class"],
        confidence=record["confidence"],
        reason=record["reason"],
        seconds=record["seconds"],
        prompt_tokens=record["prompt_tokens"],
        completion_tokens=record["completion_tokens"],
        error=record["error"],
    )


def _predictor(cache, policy):
    def predict(entry):
        record = cache.get(key_of(entry))
        verdict = _cached_adjudication(record) if record else None
        return resolve_v2(
            entry["issuer_name"], entry["issuer_title"], None,
            entry.get("filer_families"), backend=None, policy=policy,
            adjudication=verdict,
        ).company
    return predict


def confidence_profile(payload, entries, broke_ids) -> dict:
    """What the model's own confidence is worth, counted rather than asserted.

    Added after the fact, and the reason is worth recording: the first draft of
    section 9.4 said the model returned 1.000 on "308 of 322" answers and that
    "nine of the fourteen" wrong ones came back at 0.95 or above. Both numbers
    were typed by hand and both were wrong -- 315 and 11. A figure generated
    straight from the cache disagreed with the prose, which is how it surfaced.
    A number in a report that no script produced is a P3 violation whether or
    not it happens to be right, so the number now comes from here.

    Two different denominators live in this block and they are not
    interchangeable:
      disagreements   the model's own answer vs the label, over every scorable
                      string -- the E_llm_only error set (fp + fn).
      band_breaks     the strings the band policy got wrong that the matcher
                      alone got right. A subset, and the narrower claim.
    """
    by_id = {r["id"]: r for r in payload["results"].values()}
    disagreements = []
    for entry in entries:
        record = by_id.get(entry["id"])
        if record is None or entry["company"] == "UNKNOWN":
            continue
        truth = None if entry["company"] == "NOT_IN_UNIVERSE" else entry["company"]
        if (record["company"] or None) != truth:
            disagreements.append(record["confidence"])
    breaks = [by_id[i]["confidence"] for i in broke_ids if i in by_id]
    at_least = lambda values, floor: sum(1 for c in values if c >= floor)  # noqa: E731
    return {
        "answers": len(by_id),
        "distribution": {
            str(value): count
            for value, count in sorted(
                collections.Counter(r["confidence"] for r in by_id.values()).items(),
                reverse=True,
            )
        },
        "at_full_confidence": sum(1 for r in by_id.values() if r["confidence"] >= 1.0),
        "disagreements": len(disagreements),
        "disagreements_at_95_plus": at_least(disagreements, 0.95),
        "disagreements_at_full": at_least(disagreements, 1.0),
        "band_breaks": len(breaks),
        "band_breaks_at_95_plus": at_least(breaks, 0.95),
        "band_breaks_at_full": at_least(breaks, 1.0),
    }


def throughput(payload, entries) -> dict:
    """What a full re-resolution would cost, in wall-clock seconds."""
    records = [r for r in payload["results"].values() if not r["error"]]
    seconds = [r["seconds"] for r in records]
    tokens = sum(r["prompt_tokens"] + r["completion_tokens"] for r in records)
    total = sum(seconds) or 1e-9
    mean = total / len(seconds) if seconds else 0.0

    consulted = [
        e for e in entries
        if would_consult(e["issuer_name"], e["issuer_title"], policy=POLICY_BAND)
    ]
    return {
        "calls_measured": len(records),
        "errors": len(payload["results"]) - len(records),
        "mean_seconds_per_call": round(mean, 3),
        "median_seconds_per_call": round(sorted(seconds)[len(seconds) // 2], 3)
        if seconds else None,
        "slowest_seconds": round(max(seconds), 3) if seconds else None,
        "tokens_total": tokens,
        "tokens_per_second": round(tokens / total, 1),
        "warm_seconds": payload["run"]["warm_seconds"],
        "golden_set_strings": len(entries),
        "strings_consulted_under_band_policy": len(consulted),
        "band_policy_consult_rate": round(len(consulted) / len(entries), 4),
        "seconds_for_full_golden_set_llm_only": round(mean * len(entries), 1),
        "seconds_for_full_golden_set_band_policy": round(mean * len(consulted), 1),
    }


def score_all(write: bool = True) -> dict:
    if not CACHE.exists():
        sys.exit(f"no cache at {CACHE.relative_to(ROOT)} -- run with --run first")
    payload = json.loads(CACHE.read_text(encoding="utf-8"))
    cache = payload["results"]
    entries = load_fixture()
    hard = [e for e in entries if e["evidence_class"] not in ("E2_self_name", "E0_none")]
    subsets = {"all": entries, "hard": hard}

    systems = {
        "B_matcher_v1": lambda e: resolve(e["issuer_name"], e["issuer_title"]).company,
        "C_v2_band": _predictor(cache, POLICY_BAND),
        "D_v2_all": _predictor(cache, POLICY_ALL),
        "E_llm_only": _predictor(cache, POLICY_LLM_ONLY),
        "F_v2_veto": _predictor(cache, POLICY_VETO),
    }
    weights = {"macro": lambda e: 1, "micro": lambda e: e["holdings"]}

    run_info = payload["run"]
    print(f"model {run_info['model']} ({run_info.get('parameter_size')}, "
          f"{run_info.get('quantization')}) · {run_info['entries_adjudicated']} calls "
          f"· {run_info['wall_seconds']}s wall\n")

    print("1. COMPANY RESOLUTION")
    print(f"   {'subset':6} {'system':14} {'weighting':10} {'P':>7} {'R':>7} {'F1':>7}"
          f"   {'tp':>5} {'fp':>4} {'fn':>4}")
    results = {"subsets": {}}
    for subset_name, subset in subsets.items():
        results["subsets"][subset_name] = {}
        for system_name, predict in systems.items():
            entry = {}
            for weighting, weight in weights.items():
                scored = score(subset, predict, weight)
                entry[weighting] = scored
                o = scored["overall"]
                fmt = lambda v: f"{v:.4f}" if v is not None else "   -  "  # noqa: E731
                print(f"   {subset_name:6} {system_name:14} {weighting:10} "
                      f"{fmt(o['precision']):>7} {fmt(o['recall']):>7} {fmt(o['f1']):>7}"
                      f"   {o['tp']:>5} {o['fp']:>4} {o['fn']:>4}")
            results["subsets"][subset_name][system_name] = entry
        print()

    # ---- lift, stated as the plan asks
    base = results["subsets"]["all"]["B_matcher_v1"]["macro"]["overall"]
    print("2. LIFT OVER THE DETERMINISTIC BASELINE (all, macro)")
    lift = {}
    for system_name in ("C_v2_band", "D_v2_all", "E_llm_only", "F_v2_veto"):
        current = results["subsets"]["all"][system_name]["macro"]["overall"]
        delta = {
            metric: round((current[metric] or 0) - (base[metric] or 0), 4)
            for metric in ("precision", "recall", "f1")
        }
        lift[system_name] = delta
        sign = lambda v: f"{v:+.4f}"  # noqa: E731
        print(f"   {system_name:14} precision {sign(delta['precision'])}   "
              f"recall {sign(delta['recall'])}   F1 {sign(delta['f1'])}")
    results["lift_vs_baseline_all_macro"] = lift

    # ---- where the model was actually consulted, and what it did there
    policy_under_test = POLICY_BAND
    consulted, changed, broke, fixed = [], [], [], []
    for entry in entries:
        if not would_consult(entry["issuer_name"], entry["issuer_title"],
                             policy=policy_under_test):
            continue
        consulted.append(entry)
        record = cache.get(key_of(entry))
        if not record:
            continue
        before = resolve(entry["issuer_name"], entry["issuer_title"]).company
        after = resolve_v2(
            entry["issuer_name"], entry["issuer_title"], None, entry.get("filer_families"),
            policy=policy_under_test, adjudication=_cached_adjudication(record),
        ).company
        truth = None if entry["company"] == "NOT_IN_UNIVERSE" else entry["company"]
        if entry["company"] == "UNKNOWN":
            truth = "UNKNOWN"
        if before == after:
            continue
        row = {"id": entry["id"], "issuer_name": entry["issuer_name"],
               "truth": entry["company"], "before": before, "after": after,
               "reason": record["reason"][:160]}
        changed.append(row)
        if before == truth and after != truth:
            broke.append(row)
        elif before != truth and after == truth:
            fixed.append(row)

    print(f"\n3. WHAT THE MODEL CHANGED, under the band policy")
    print(f"   consulted on {len(consulted)} of {len(entries)} strings; "
          f"changed {len(changed)}; fixed {len(fixed)}; broke {len(broke)}")
    for row in changed:
        mark = "FIXED " if row in fixed else ("BROKE " if row in broke else "moved ")
        print(f"     {mark}{row['issuer_name'][:40]:42} {str(row['before'])[:22]:24}"
              f" -> {str(row['after'])[:22]}")
    results["band_policy_changes"] = {
        "consulted": len(consulted), "changed": changed, "fixed": fixed, "broke": broke,
    }

    veto_consulted = [
        e for e in entries
        if would_consult(e["issuer_name"], e["issuer_title"], policy=POLICY_VETO)
    ]
    results["veto_policy_consulted"] = len(veto_consulted)
    print(f"\n   under the veto policy the model is consulted on "
          f"{len(veto_consulted)} strings, not {len(consulted)}")

    conf = confidence_profile(payload, entries, {row["id"] for row in broke})
    results["confidence"] = conf
    print(f"\n   confidence: {conf['at_full_confidence']} of {conf['answers']} answers at "
          f"1.000; of {conf['disagreements']} answers that disagree with the label, "
          f"{conf['disagreements_at_95_plus']} came back at 0.95 or above")

    tp = throughput(payload, entries)
    results["throughput"] = tp
    print(f"\n4. THROUGHPUT")
    print(f"   {tp['mean_seconds_per_call']}s mean per call, "
          f"{tp['median_seconds_per_call']}s median, {tp['slowest_seconds']}s slowest")
    print(f"   {tp['tokens_per_second']} tokens/s · {tp['errors']} errors "
          f"of {len(payload['results'])} calls")
    print(f"   band policy consults {tp['strings_consulted_under_band_policy']} of "
          f"{tp['golden_set_strings']} strings "
          f"({tp['band_policy_consult_rate'] * 100:.1f}%) -> "
          f"{tp['seconds_for_full_golden_set_band_policy']}s per full re-resolution")

    results["run"] = run_info
    if write:
        METRICS.write_text(json.dumps(results, indent=1), encoding="utf-8")
        print(f"\nwrote {METRICS.relative_to(ROOT)}")
    return results


def check(model: str) -> None:
    backend = load_backend(model=model, schema=RESPONSE_SCHEMA)
    print(f"host    {backend.host}")
    print(f"up      {backend.available()}")
    if backend.available():
        print(f"models  {backend.installed_models()}")
    entries = load_fixture()
    consulted = sum(
        1 for e in entries
        if would_consult(e["issuer_name"], e["issuer_title"], policy=POLICY_BAND)
    )
    print(f"\ngolden set: {len(entries)} strings, {consulted} would reach the model "
          f"under the band policy (score < {AUTO_ACCEPT} or unresolved; "
          f"review floor {REVIEW_FLOOR})")
    system, user = build_prompt(
        entries[0]["issuer_name"], entries[0]["issuer_title"],
        entries[0].get("filer_families"),
    )
    print(f"\nprompt is {len(system) + len(user)} characters; sample user block:\n")
    print("\n".join("    " + line for line in user.split("\n")))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--score", action="store_true")
    ap.add_argument("--limit", type=int, help="adjudicate only the first N (smoke test)")
    ap.add_argument("--only-consulted", action="store_true",
                    help="skip strings the band policy would never send")
    args = ap.parse_args()

    if args.check:
        check(args.model)
        return
    if args.run:
        run(args.model, limit=args.limit, only_consulted=args.only_consulted)
    if args.score or (args.run and not args.limit):
        score_all()
    if not (args.check or args.run or args.score):
        ap.error("give --check, --run or --score")


if __name__ == "__main__":
    main()
