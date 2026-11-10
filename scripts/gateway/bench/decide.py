"""Sprint 8: compare routing policies and decide, against thresholds fixed in August.

Every policy here is replayed against the Sprint 7 baseline rather than run
live. The baseline recorded cost, latency, check result and correctness for
every fixture on every tier, so a policy's behaviour is a lookup, not a new
call. That is cheaper, and it is also better evidence: each policy is judged
on the same answers, so a difference between two policies cannot be run-to-run
noise.

The thresholds, fixed in August before any of this was measured:

    at least 20% cheaper at equal quality, and no more than 20% slower.

Fitting and evaluation are kept apart. The task-type table and the break-even
rule are both derived FROM the baseline, so scoring them on the same rows
would be marking their own homework. Repeats 1-2 fit; the held-out repeat
evaluates. With three repeats that is a thin holdout, and the report says so.

The break-even rule, held back since Sprint 3 for want of measured pass rates:
starting cheap costs c_cheap, plus c_mid again whenever the cheap answer fails
its check. So cheap is worth starting iff

    c_cheap + (1 - p_cheap) * c_mid  <  c_mid      i.e.   c_cheap < p_cheap * c_mid

with p_cheap the measured check-pass rate. A second gate applies first: cheap
is only eligible if its measured correctness is no worse than mid's, because a
cheaper wrong answer is not cheaper.

Usage:
    python scripts/gateway/bench/decide.py
    python scripts/gateway/bench/decide.py --rows <baseline jsonl>
    python scripts/gateway/bench/decide.py --holdout 3
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import date
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gateway.policy import Policy
from gateway.report import percentile
from gateway.tiers import TierConfig

RESULTS_DIR = Path(__file__).with_name("results")

CHEAPER_THRESHOLD = 0.20   # must be at least this much cheaper
SLOWER_THRESHOLD = 0.20    # may be at most this much slower


def latest_rows(results_dir: Path = RESULTS_DIR) -> Path | None:
    runs = sorted(results_dir.glob("*-baseline.jsonl"))
    return runs[-1] if runs else None


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in
            path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [r for r in rows if not r.get("warmup") and not r.get("error")]


def measure(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    """Per task type, per tier: what the fit split says each tier does."""
    out: dict[str, dict[str, dict[str, Any]]] = {}
    for task in sorted({r["task_type"] for r in rows}):
        out[task] = {}
        for tier in sorted({r["tier"] for r in rows}):
            subset = [r for r in rows if r["task_type"] == task and r["tier"] == tier]
            if not subset:
                continue
            graded = [r for r in subset if r.get("graded")]
            out[task][tier] = {
                "calls": len(subset),
                "pass_rate": sum(1 for r in subset if r["passed_check"]) / len(subset),
                "correct_rate": (sum(1 for r in graded if r["correct"]) / len(graded)
                                 if graded else None),
                "mean_cost": statistics.mean(r["cost_usd"] for r in subset),
            }
    return out


# -- the policies --------------------------------------------------------

Policy_fn = Callable[[str], tuple[str, str | None]]  # task type -> (start, escalate_to)


def fixed(tier: str) -> Policy_fn:
    return lambda task: (tier, None)


def from_policy_file(policy: Policy) -> Policy_fn:
    """What the gateway does today: policy.json's start tier and escalation target."""
    def choose(task: str) -> tuple[str, str | None]:
        rule = policy.rule_for(task)
        return rule["start_tier"], rule.get("escalate_to")
    return choose


def task_table(fit: dict[str, Any], tier_order: list[str]) -> Policy_fn:
    """Best measured tier per task type: highest correctness, cheapest tie-break.

    Where nothing is gradeable -- summarization -- there is no quality signal
    to choose on, so it falls to the cheapest tier and the report flags it.
    """
    chosen: dict[str, str] = {}
    for task, tiers in fit.items():
        gradeable = {t: m for t, m in tiers.items() if m["correct_rate"] is not None}
        if gradeable:
            best = max(m["correct_rate"] for m in gradeable.values())
            candidates = {t: m for t, m in gradeable.items()
                          if abs(m["correct_rate"] - best) < 1e-9}
        else:
            candidates = tiers
        chosen[task] = min(candidates, key=lambda t: candidates[t]["mean_cost"])
    return lambda task: (chosen.get(task, tier_order[0]), None)


def break_even(fit: dict[str, Any], *, cheap: str = "cheap",
               mid: str = "mid") -> Policy_fn:
    """Start cheap only where the measured numbers say it pays. Escalate once."""
    chosen: dict[str, tuple[str, str | None]] = {}
    for task, tiers in fit.items():
        if cheap not in tiers or mid not in tiers:
            chosen[task] = (mid if mid in tiers else cheap, None)
            continue
        c, m = tiers[cheap], tiers[mid]

        # Quality gate first: a cheaper wrong answer is not cheaper.
        quality_ok = (c["correct_rate"] is None or m["correct_rate"] is None
                      or c["correct_rate"] >= m["correct_rate"])
        pays = c["mean_cost"] < c["pass_rate"] * m["mean_cost"]
        chosen[task] = ((cheap, mid) if (quality_ok and pays) else (mid, None))
    return lambda task: chosen.get(task, (mid, None))


# -- replay --------------------------------------------------------------

def simulate(choose: Policy_fn, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Replay one policy over the held-out rows. One simulated request per repeat."""
    index = {(r["id"], r["tier"], r["repeat"]): r for r in rows}
    keys = sorted({(r["id"], r["repeat"]) for r in rows})

    costs, latencies, correct, graded, escalated, missing = [], [], 0, 0, 0, 0
    for fixture_id, repeat in keys:
        task = next(r["task_type"] for r in rows if r["id"] == fixture_id)
        start, escalate_to = choose(task)
        first = index.get((fixture_id, start, repeat))
        if first is None:
            missing += 1
            continue

        cost, latency, final = first["cost_usd"], first["latency_ms"], first
        if not first["passed_check"] and escalate_to:
            second = index.get((fixture_id, escalate_to, repeat))
            if second is not None:
                cost += second["cost_usd"]
                latency += second["latency_ms"]
                final = second
                escalated += 1

        costs.append(cost)
        latencies.append(float(latency))
        if final.get("graded"):
            graded += 1
            correct += bool(final.get("correct"))

    return {
        "requests": len(costs),
        "missing_rows": missing,
        "total_cost_usd": round(sum(costs), 6),
        "mean_cost_usd": round(statistics.mean(costs), 8) if costs else None,
        "p50_latency_ms": percentile(latencies, 50) if latencies else None,
        "p95_latency_ms": percentile(latencies, 95) if latencies else None,
        "graded": graded,
        "correct": correct,
        "correct_rate": (correct / graded) if graded else None,
        "escalations": escalated,
    }


def verdict(candidate: dict[str, Any], incumbent: dict[str, Any]) -> dict[str, Any]:
    """Apply the August thresholds. No judgment beyond the arithmetic.

    `cheaper_by` is positive when the candidate costs less; `slower_by` is
    positive when it takes longer. Both are reported in words as well as
    numbers, because a signed percentage against a word like "cost" is read
    backwards by half the people who see it.
    """
    cheaper = 1 - (candidate["mean_cost_usd"] / incumbent["mean_cost_usd"])
    slower = (candidate["p50_latency_ms"] / incumbent["p50_latency_ms"]) - 1
    quality_held = (candidate["correct_rate"] is not None
                    and incumbent["correct_rate"] is not None
                    and candidate["correct_rate"] >= incumbent["correct_rate"])
    return {
        "cheaper_by": cheaper,
        "slower_by": slower,
        "quality_held": quality_held,
        "meets_cost_threshold": cheaper >= CHEAPER_THRESHOLD,
        "meets_latency_threshold": slower <= SLOWER_THRESHOLD,
        "ship": bool(quality_held and cheaper >= CHEAPER_THRESHOLD
                     and slower <= SLOWER_THRESHOLD),
    }


def in_words(v: dict[str, Any]) -> str:
    """"31% cheaper, 31% faster" -- never a bare signed percentage."""
    cost = (f"{v['cheaper_by']:.0%} cheaper" if v["cheaper_by"] >= 0
            else f"{-v['cheaper_by']:.0%} dearer")
    speed = (f"{v['slower_by']:.0%} slower" if v["slower_by"] > 0
             else f"{-v['slower_by']:.0%} faster")
    return f"{cost}, {speed}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare routing policies against the baseline and decide.")
    parser.add_argument("--rows", help="a baseline JSONL (default: the newest)")
    parser.add_argument("--holdout", type=int, default=0,
                        help="repeat number to evaluate on (default: the last)")
    args = parser.parse_args()

    rows_file = Path(args.rows) if args.rows else latest_rows()
    if rows_file is None or not rows_file.exists():
        print("No baseline rows found. Run baseline.py first.")
        return 1

    rows = load_rows(rows_file)
    repeats = sorted({r["repeat"] for r in rows})
    holdout = args.holdout or repeats[-1]
    if holdout not in repeats:
        print(f"Repeat {holdout} is not in this run ({repeats}).")
        return 1

    fit_rows = [r for r in rows if r["repeat"] != holdout]
    eval_rows = [r for r in rows if r["repeat"] == holdout]
    fit = measure(fit_rows)

    tiers = TierConfig.load()
    policy = Policy.load(tiers)
    order = list(policy.tier_order)

    candidates: dict[str, Policy_fn] = {
        "current policy": from_policy_file(policy),
        **{f"always {t}": fixed(t) for t in order},
        "task-type table": task_table(fit, order),
        "break-even": break_even(fit),
    }

    print(f"baseline {rows_file.name}")
    print(f"fit on repeats {[r for r in repeats if r != holdout]}, "
          f"evaluated on repeat {holdout} ({len(eval_rows)} rows held out)")
    print(f"thresholds: at least {CHEAPER_THRESHOLD:.0%} cheaper at equal "
          f"quality, at most {SLOWER_THRESHOLD:.0%} slower\n")

    print("what each policy picks per task type:")
    for task in sorted(fit):
        picks = []
        for name, choose in candidates.items():
            if name.startswith("always"):
                continue
            start, escalate_to = choose(task)
            picks.append(f"{name}: {start}" + (f"->{escalate_to}" if escalate_to else ""))
        print(f"  {task:<26}" + " · ".join(picks))

    results = {name: simulate(choose, eval_rows) for name, choose in candidates.items()}
    incumbent = results["current policy"]

    print(f"\n{'policy':<18}{'reqs':>5}{'mean $':>11}{'p50 ms':>8}"
          f"{'correct':>14}{'esc':>5}  vs current")
    for name, stats in results.items():
        v = verdict(stats, incumbent)
        rate = ("-" if stats["correct_rate"] is None
                else f"{stats['correct']}/{stats['graded']} "
                     f"({stats['correct_rate']:.0%})")
        shown = ("incumbent" if name == "current policy"
                 else in_words(v) + ("   SHIP" if v["ship"] else ""))
        print(f"{name:<18}{stats['requests']:>5}{stats['mean_cost_usd']:>11.6f}"
              f"{stats['p50_latency_ms']:>8.0f}{rate:>14}"
              f"{stats['escalations']:>5}  {shown}")

    passing = [n for n, s in results.items()
               if n != "current policy" and verdict(s, incumbent)["ship"]]
    print()
    if passing:
        best = min(passing, key=lambda n: results[n]["mean_cost_usd"])
        v = verdict(results[best], incumbent)
        print(f"MEETS THE THRESHOLDS: {', '.join(passing)}")
        print(f"Cheapest of those: {best} -- {in_words(v)}, quality held "
              f"({results[best]['correct']}/{results[best]['graded']} against the "
              f"incumbent's {incumbent['correct']}/{incumbent['graded']}).")
    else:
        print("NOTHING MEETS THE THRESHOLDS. The honest recommendation is to keep "
              "the current policy.")

    print("\nCaveats that travel with this: summarization has no correctness "
          "figure\nand is routed on cost alone; the holdout is one repeat of "
          "three and every\npolicy but one scores the same, so it has little "
          "power to separate quality;\nand the fixtures are 24 synthetic cases "
          "on one provider.")

    out = RESULTS_DIR / f"{date.today().isoformat()}-decision.json"
    out.write_text(json.dumps({
        "decided_on": date.today().isoformat(),
        "baseline_rows": rows_file.name,
        "holdout_repeat": holdout,
        "thresholds": {"cheaper_by_at_least": CHEAPER_THRESHOLD,
                       "slower_by_at_most": SLOWER_THRESHOLD},
        "fit": fit,
        "results": results,
        "verdicts": {n: verdict(s, incumbent) for n, s in results.items()},
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nreport  {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())