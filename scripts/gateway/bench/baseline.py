"""The baseline: every fixture on every tier, several times each.

Every number this project has produced so far describes the gateway as
configured -- and policy sends 20 of the 24 fixtures to mid, so the cheap tier
has served four requests in its life. Nothing measured says what cheap can do
on the other twenty. This run removes the router from the picture: each
fixture is sent to each tier outright, repeatedly, and what comes back is
recorded per tier rather than per policy decision.

Repeats, because one pass is a sample. The same fixture judged on 2026-09-24
came back `tie` once and `inconsistent` twice, and answers are regenerated
every run -- so cost is reported as a spread and correctness as a rate.

The first call on each tier is a warmup and is excluded from the statistics.
It is still logged and still paid for; it is simply not evidence, because a
cold first call measures the provider's queue as much as the model.

Resumable, because the strong tier is capped near one call a minute and a
216-call sweep runs for hours. Rows are appended to a JSONL file as they
happen, and --resume skips what is already there. A run that dies at call 180
does not repay the first 179.

Pacing applies only to the tiers that need it (--pace-tiers), since pacing
cheap and mid would triple the wall clock for no reason.

Usage:
    $env:GROQ_API_KEY="gsk_..."
    python scripts/gateway/bench/baseline.py --dry-run
    python scripts/gateway/bench/baseline.py --limit 2 --repeats 1   # smoke test
    python scripts/gateway/bench/baseline.py                         # the baseline
    python scripts/gateway/bench/baseline.py --resume 2026-10-08T...
    python scripts/gateway/bench/baseline.py --report 2026-10-08T... # no calls
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gateway import prompts, validators
from gateway.adapters.base import LLMResponse, ProviderError
from gateway.adapters.groq import GroqAdapter
from gateway.bench import fixtures as fx
from gateway.bench.grading import grade_answer
from gateway.client import GatewayClient
from gateway.logbook import Logbook
from gateway.policy import Policy
from gateway.prices import PriceTable
from gateway.report import percentile
from gateway.tiers import TierConfig

RESULTS_DIR = Path(__file__).with_name("results")
LOG_DIR = Path("logs/gateway/runs")


def rows_path(run_id: str) -> Path:
    return RESULTS_DIR / f"{run_id}-baseline.jsonl"


def load_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in
            path.read_text(encoding="utf-8").splitlines() if line.strip()]


def append_row(path: Path, row: dict[str, Any]) -> None:
    """One row per call, written as it happens -- that is what makes resume work."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def plan(items: list[dict[str, Any]], tiers: list[str],
         repeats: int) -> list[tuple[dict[str, Any], str, int]]:
    """Every (fixture, tier, repeat) this run owes, tier-major so pacing batches."""
    return [(fixture, tier, repeat)
            for repeat in range(1, repeats + 1)
            for tier in tiers
            for fixture in items]


def cost_bound(items: list[dict[str, Any]], tier_names: list[str], policy: Policy,
               tiers: TierConfig, prices: PriceTable, repeats: int) -> float:
    """A loose UPPER bound: every call fills its whole token budget.

    Character counts stand in for token counts, as in run.py -- roughly four
    times too many, which is the direction an upper bound should err.
    """
    total = 0.0
    for fixture in items:
        rule = policy.rule_for(fixture["task_type"])
        prompt = prompts.build(rule, fixture["input"],
                               context=fixture.get("context"),
                               required_keys=fixture["expected"].get("required_keys"))
        for tier in tier_names:
            spec = tiers.spec(tier)
            total += prices.cost_usd(spec["provider"], spec["model"],
                                     len(prompt), policy.max_tokens(tier))
    return total * repeats


def one_call(client: GatewayClient, *, fixture: dict[str, Any], rule: dict[str, Any],
             policy: Policy, tier: str, prompt: str, repeat: int,
             warmup: bool) -> dict[str, Any]:
    """One forced-tier call, checked and graded. Raises ProviderError upward."""
    max_tokens = policy.max_tokens(tier)
    required_keys = fixture["expected"].get("required_keys")

    def check(response: LLMResponse) -> dict[str, Any]:
        return validators.check(
            rule["validator"], response.text,
            tokens_out=response.tokens_out, max_tokens=max_tokens,
            labels=rule.get("labels"), required_keys=required_keys,
            input_text=fixture["input"], context=fixture.get("context"))

    call = client.call(
        task_type=fixture["task_type"], caller="bench/baseline.py", tier=tier,
        prompt=prompt, max_tokens=max_tokens,
        # The tier is named outright, not chosen by policy. These rows must
        # never be mistaken for policy traffic in a later report.
        routing_reason="override",
        check=check,
        notes=f"baseline {fixture['id']} {tier} repeat {repeat}"
              + (" warmup" if warmup else ""))

    checked = call.validator_result or {}
    graded = grade_answer(fixture["expected"], checked, call.response.text)
    return {
        "id": fixture["id"], "task_type": fixture["task_type"],
        "difficulty": fixture["difficulty"],
        "expected_tier": fixture["expected_tier"],
        "tier": tier, "repeat": repeat, "warmup": warmup,
        "passed_check": call.passed, "check_reason": checked.get("reason", ""),
        "cost_usd": float(call.record["cost_usd"]),
        "latency_ms": int(call.record["latency_ms"]),
        "tokens_in": int(call.record["tokens_in"]),
        "tokens_out": int(call.record["tokens_out"]),
        "outcome": call.record["outcome"],
        "text": call.response.text,
        "request_id": call.request_id,
        **graded,
    }


def summarize(rows: list[dict[str, Any]], tier_names: list[str]) -> dict[str, Any]:
    """Per tier, and per task type within each tier. Warmups excluded."""
    data = [r for r in rows if not r.get("warmup") and not r.get("error")]

    def block(subset: list[dict[str, Any]]) -> dict[str, Any] | None:
        if not subset:
            return None
        graded = [r for r in subset if r.get("graded")]
        correct = [r for r in graded if r.get("correct")]
        passed = [r for r in subset if r.get("passed_check")]
        costs = [r["cost_usd"] for r in subset]
        latencies = [float(r["latency_ms"]) for r in subset]
        return {
            "calls": len(subset),
            "check_pass_rate": len(passed) / len(subset),
            "graded": len(graded),
            "correct": len(correct),
            "correct_rate": (len(correct) / len(graded)) if graded else None,
            "cost_usd_total": round(sum(costs), 6),
            "cost_usd_mean": round(sum(costs) / len(costs), 8),
            "cost_usd_min": round(min(costs), 8),
            "cost_usd_max": round(max(costs), 8),
            "p50_latency_ms": percentile(latencies, 50),
            "p95_latency_ms": percentile(latencies, 95),
        }

    per_tier = {}
    for tier in tier_names:
        subset = [r for r in data if r["tier"] == tier]
        per_tier[tier] = {
            "overall": block(subset),
            "by_task": {task: block([r for r in subset if r["task_type"] == task])
                        for task in sorted({r["task_type"] for r in data})},
        }
    return {"calls_counted": len(data),
            "warmups_excluded": len([r for r in rows if r.get("warmup")]),
            "errors": len([r for r in rows if r.get("error")]),
            "per_tier": per_tier}


def print_report(summary: dict[str, Any], tier_names: list[str]) -> None:
    print(f"\n{summary['calls_counted']} calls counted "
          f"({summary['warmups_excluded']} warmups and {summary['errors']} "
          f"errors excluded)\n")
    print(f"{'tier':<8}{'calls':>6}{'check ok':>10}{'correct':>16}"
          f"{'mean $':>11}{'p50 ms':>9}{'p95 ms':>9}")
    for tier in tier_names:
        block = summary["per_tier"][tier]["overall"]
        if not block:
            print(f"{tier:<8}{'no data':>6}")
            continue
        rate = ("-" if block["correct_rate"] is None
                else f"{block['correct']}/{block['graded']} "
                     f"({block['correct_rate']:.0%})")
        print(f"{tier:<8}{block['calls']:>6}{block['check_pass_rate']:>9.0%}"
              f"{rate:>16}{block['cost_usd_mean']:>11.6f}"
              f"{block['p50_latency_ms']:>9.0f}{block['p95_latency_ms']:>9.0f}")

    tasks = sorted(summary["per_tier"][tier_names[0]]["by_task"])
    for task in tasks:
        print(f"\n{task}")
        for tier in tier_names:
            block = summary["per_tier"][tier]["by_task"].get(task)
            if not block:
                continue
            rate = ("quality unmeasured" if block["correct_rate"] is None
                    else f"{block['correct']}/{block['graded']} correct "
                         f"({block['correct_rate']:.0%})")
            print(f"  {tier:<8}{block['calls']:>4} calls  "
                  f"check {block['check_pass_rate']:>4.0%}  {rate:<28}"
                  f"${block['cost_usd_mean']:.6f}  "
                  f"p50 {block['p50_latency_ms']:.0f} ms")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run every fixture on every tier, several times each.")
    parser.add_argument("--repeats", type=int, default=3,
                        help="runs per fixture per tier (default 3)")
    parser.add_argument("--tiers", default="",
                        help="comma-separated tiers (default: all, cheapest first)")
    parser.add_argument("--limit", type=int, default=0, help="only the first N fixtures")
    parser.add_argument("--dry-run", action="store_true",
                        help="show the plan and the cost bound; make no calls")
    parser.add_argument("--resume", metavar="RUN_ID",
                        help="continue a run, skipping calls already recorded")
    parser.add_argument("--report", metavar="RUN_ID",
                        help="print the report for a finished run; make no calls")
    parser.add_argument("--pace-tiers", default="strong",
                        help="tiers that need pacing (default: strong)")
    parser.add_argument("--pace-seconds", type=float, default=35.0,
                        help="wait between calls on a paced tier")
    parser.add_argument("--no-warmup", action="store_true",
                        help="do not make an excluded first call per tier")
    args = parser.parse_args()

    prices = PriceTable.load()
    if prices.version == "UNSET":
        print("prices.json has no real rates. Nothing was called.")
        return 1
    tiers = TierConfig.load()
    policy = Policy.load(tiers)
    tier_names = ([t.strip() for t in args.tiers.split(",") if t.strip()]
                  or list(policy.tier_order))
    unknown = [t for t in tier_names if t not in policy.tier_order]
    if unknown:
        print(f"Unknown tier(s): {unknown}. Known: {policy.tier_order}")
        return 1

    if args.report:
        rows = load_rows(rows_path(args.report))
        if not rows:
            print(f"No rows found for run {args.report}.")
            return 1
        print_report(summarize(rows, tier_names), tier_names)
        return 0

    if not fx.MANIFEST_PATH.exists():
        print("The fixture set is not frozen. Run audit.py --freeze first.")
        return 1
    manifest = json.loads(fx.MANIFEST_PATH.read_text(encoding="utf-8"))
    drift = fx.check_manifest(manifest)
    if drift:
        print("The fixture set has changed since it was frozen:")
        for line in drift:
            print(f"  - {line}")
        print("Re-freeze deliberately, or restore the files. Nothing was called.")
        return 1

    items = fx.validate(fx.load(), policy)
    items.sort(key=lambda f: f["id"])
    if args.limit:
        items = items[:args.limit]

    run_id = args.resume or datetime.now().strftime("%Y-%m-%dT%H%M%S")
    out_path = rows_path(run_id)
    existing = load_rows(out_path)
    done = {(r["id"], r["tier"], r["repeat"]) for r in existing if not r.get("warmup")}

    todo = [step for step in plan(items, tier_names, args.repeats)
            if (step[0]["id"], step[1], step[2]) not in done]
    paced = {t.strip() for t in args.pace_tiers.split(",") if t.strip()}
    paced_calls = sum(1 for _, tier, _ in todo if tier in paced)

    bound = cost_bound(items, tier_names, policy, tiers, prices, args.repeats)
    print(f"{len(items)} fixtures x {len(tier_names)} tiers x {args.repeats} "
          f"repeats = {len(items) * len(tier_names) * args.repeats} calls")
    print(f"policy {policy.version} · tiers {tiers.version} · prices "
          f"{prices.version} · fixtures frozen {manifest['frozen_on']}")
    if existing:
        print(f"resuming {run_id}: {len(done)} already recorded, {len(todo)} to go")
    print(f"at most ${bound:.4f}; pacing {paced} at {args.pace_seconds:.0f}s "
          f"= about {paced_calls * args.pace_seconds / 60:.0f} min")

    if args.dry_run:
        for tier in tier_names:
            spec = tiers.spec(tier)
            print(f"  {tier:<8}{spec['provider']}:{spec['model']:<24}"
                  f"max_tokens {policy.max_tokens(tier)}")
        print("\nDry run: nothing was called.")
        return 0

    if not todo:
        print("\nNothing left to run.")
        print_report(summarize(existing, tier_names), tier_names)
        return 0

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("\nGROQ_API_KEY is not set. Nothing was called.")
        return 1
    if input("\nType 'yes' to make these calls: ").strip().lower() != "yes":
        print("Cancelled. Nothing was called.")
        return 1

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"{run_id}-baseline.jsonl"
    client = GatewayClient(logbook=Logbook(log_path, prices),
                           adapters={"groq": GroqAdapter(api_key=api_key)},
                           tiers=tiers.as_client_map(),
                           policy_version=policy.version)

    warmed: set[str] = {r["tier"] for r in existing if r.get("warmup")}
    print(f"\n{'fixture':<12}{'tier':<8}{'rep':>4}{'check':>8}{'graded':>10}"
          f"{'cost':>11}{'ms':>7}")

    for n, (fixture, tier, repeat) in enumerate(todo):
        rule = policy.rule_for(fixture["task_type"])
        prompt = prompts.build(rule, fixture["input"],
                               context=fixture.get("context"),
                               required_keys=fixture["expected"].get("required_keys"))

        for warmup in ([True, False] if (not args.no_warmup and tier not in warmed)
                       else [False]):
            if warmup:
                warmed.add(tier)
            if (n or warmup) and tier in paced:
                time.sleep(args.pace_seconds)
            try:
                row = one_call(client, fixture=fixture, rule=rule, policy=policy,
                               tier=tier, prompt=prompt, repeat=repeat,
                               warmup=warmup)
            except ProviderError as exc:
                row = {"id": fixture["id"], "task_type": fixture["task_type"],
                       "tier": tier, "repeat": repeat, "warmup": warmup,
                       "error": str(exc), "graded": False, "correct": None}
                append_row(out_path, row)
                print(f"{fixture['id']:<12}{tier:<8}{repeat:>4}  ERROR "
                      f"{str(exc)[:60]}")
                continue

            append_row(out_path, row)
            graded = ("-" if not row["graded"]
                      else "correct" if row["correct"] else "WRONG")
            print(f"{fixture['id']:<12}{tier:<8}{repeat:>4}"
                  f"{'ok' if row['passed_check'] else 'FAIL':>8}"
                  f"{graded:>10}{row['cost_usd']:>11.6f}{row['latency_ms']:>7}"
                  + ("   (warmup, excluded)" if warmup else ""))

    rows = load_rows(out_path)
    summary = summarize(rows, tier_names)
    print_report(summary, tier_names)

    report_path = RESULTS_DIR / f"{run_id}-baseline.json"
    report_path.write_text(json.dumps({
        "run_id": run_id, "run_on": date.today().isoformat(),
        "policy_version": policy.version, "tiers_version": tiers.version,
        "prices_version": prices.version,
        "fixtures_frozen_on": manifest["frozen_on"],
        "tiers": tier_names, "repeats": args.repeats,
        "fixtures": len(items),
        "quality_note": "prose task types carry no correctness figure: no answer "
                        "key can exist for them and the model judge scored kappa "
                        "0.00 against a human (FINDINGS section 10)",
        "summary": summary,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"\nrows    {out_path}")
    print(f"report  {report_path}")
    print(f"logbook {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())