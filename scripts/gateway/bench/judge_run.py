"""Generate two answers per open-ended fixture, then judge them against each other.

Only `prose` tasks come here: summarization and rag_answer. Everything else has
an answer key and is graded directly by run.py -- a judge is for the cases where
no key can exist, not a substitute for one that can.

Per sample: one answer from the cheap tier, one from the mid tier, then two
judging calls on the strong tier with the answers swapped. The tiers are named
outright rather than routed, so these rows carry routing_reason "override" and
never look like policy traffic in the baseline.

`--samples N` repeats each fixture N times with freshly generated answers. The
models are not deterministic -- the same fixture judged on 2026-09-24 came back
`tie` once and `inconsistent` twice -- so one pass per fixture is a sample, not
a measurement. Samples from one fixture are NOT independent observations of
different tasks, and the report says so.

Pacing: the strong model's account cap is 1000 output tokens per minute
(policy.json explains the 896 budget). A judged pair spends at most 512, so the
run waits between comparisons rather than being rejected mid-sweep.

Usage:
    $env:GROQ_API_KEY="gsk_..."
    python scripts/gateway/bench/judge_run.py --dry-run             # cost bound, no calls
    python scripts/gateway/bench/judge_run.py --limit 2             # a cheap smoke test
    python scripts/gateway/bench/judge_run.py --samples 4           # 8 fixtures x 4 = 32 pairs
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
from gateway.bench.judge import compare, summarize
from gateway.client import GatewayClient
from gateway.logbook import Logbook
from gateway.policy import Policy
from gateway.prices import PriceTable
from gateway.tiers import TierConfig

RESULTS_DIR = Path(__file__).with_name("results")
LOG_DIR = Path("logs/gateway/runs")

JUDGE_MAX_TOKENS = 256
OPEN_ENDED = "prose"


def open_ended(items: list[dict[str, Any]], policy: Policy) -> list[dict[str, Any]]:
    """The fixtures with no answer key -- the only ones a judge belongs on."""
    return [f for f in items
            if policy.rule_for(f["task_type"])["output"] == OPEN_ENDED]


def _checker(rule: dict[str, Any], fixture: dict[str, Any], max_tokens: int):
    """The same free check the request path runs. Shape only, never correctness."""
    def check(response: LLMResponse) -> dict[str, Any]:
        return validators.check(
            rule["validator"], response.text,
            tokens_out=response.tokens_out, max_tokens=max_tokens,
            labels=rule.get("labels"),
            required_keys=fixture["expected"].get("required_keys"),
            input_text=fixture["input"], context=fixture.get("context"))
    return check


def answer(client: GatewayClient, *, fixture: dict[str, Any], rule: dict[str, Any],
           policy: Policy, tier: str, prompt: str, sample: int) -> dict[str, Any]:
    """One answer at one named tier. Returns the answer and what it cost."""
    max_tokens = policy.max_tokens(tier)
    call = client.call(
        task_type=fixture["task_type"], caller="bench/judge_run.py", tier=tier,
        prompt=prompt, max_tokens=max_tokens, routing_reason="override",
        check=_checker(rule, fixture, max_tokens),
        notes=f"judge_run answer at {tier} ({fixture['id']} sample {sample})")
    checked = call.validator_result or {}
    return {"tier": tier, "text": call.response.text.strip(),
            "passed_check": call.passed, "check_reason": checked.get("reason", ""),
            "cost_usd": float(call.record["cost_usd"]),
            "latency_ms": int(call.record["latency_ms"]),
            "request_id": call.request_id}


def cost_bound(items: list[dict[str, Any]], policy: Policy, tiers: TierConfig,
               prices: PriceTable, *, a_tier: str, b_tier: str, judge_tier: str,
               samples: int) -> float:
    """A loose UPPER bound: every call fills its whole token budget.

    Token counts are stood in for by character counts, as in run.py -- about
    four times too many, which is the direction an upper bound should err.
    """
    total = 0.0
    for fixture in items:
        rule = policy.rule_for(fixture["task_type"])
        prompt = prompts.build(rule, fixture["input"],
                               context=fixture.get("context"),
                               required_keys=fixture["expected"].get("required_keys"))
        for tier in (a_tier, b_tier):
            spec = tiers.spec(tier)
            total += prices.cost_usd(spec["provider"], spec["model"],
                                     len(prompt), policy.max_tokens(tier))

        # The judge reads the task, the input, and two answers at most their
        # budgets long. Twice, once each way round.
        spec = tiers.spec(judge_tier)
        judge_prompt = (len(prompt) + 4 * (policy.max_tokens(a_tier)
                                           + policy.max_tokens(b_tier)) + 500)
        total += 2 * prices.cost_usd(spec["provider"], spec["model"],
                                     judge_prompt, JUDGE_MAX_TOKENS)
    return total * samples


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Judge cheap answers against mid answers, both ways round.")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would run and the cost bound; make no calls")
    parser.add_argument("--limit", type=int, default=0, help="only the first N fixtures")
    parser.add_argument("--samples", type=int, default=1,
                        help="independently generated answer pairs per fixture")
    parser.add_argument("--a-tier", default="cheap", help="tier that writes answer A")
    parser.add_argument("--b-tier", default="mid", help="tier that writes answer B")
    parser.add_argument("--judge-tier", default="strong", help="tier that judges")
    parser.add_argument("--pace-seconds", type=float, default=35.0,
                        help="wait between comparisons, to stay under the judge "
                             "model's output-tokens-per-minute cap")
    args = parser.parse_args()

    if args.samples < 1:
        print("--samples must be at least 1.")
        return 1

    prices = PriceTable.load()
    if prices.version == "UNSET":
        print("prices.json has no real rates. Nothing was called.")
        return 1

    tiers = TierConfig.load()
    policy = Policy.load(tiers)

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

    items = open_ended(fx.validate(fx.load(), policy), policy)
    items.sort(key=lambda f: f["id"])
    if args.limit:
        items = items[:args.limit]
    if not items:
        print("No open-ended fixtures to judge.")
        return 1

    comparisons_planned = len(items) * args.samples
    bound = cost_bound(items, policy, tiers, prices, a_tier=args.a_tier,
                       b_tier=args.b_tier, judge_tier=args.judge_tier,
                       samples=args.samples)
    minutes = (comparisons_planned - 1) * args.pace_seconds / 60
    print(f"{len(items)} open-ended fixtures x {args.samples} sample(s) = "
          f"{comparisons_planned} comparisons, frozen {manifest['frozen_on']}")
    print(f"policy {policy.version} · tiers {tiers.version} · prices {prices.version}")
    print(f"{args.a_tier} vs {args.b_tier}, judged by {args.judge_tier}, "
          f"each pair both ways round")
    print(f"{comparisons_planned * 4} calls, costing at most ${bound:.4f}, "
          f"about {minutes:.0f} min of pacing")

    if args.dry_run:
        for fixture in items:
            print(f"  {fixture['id']:<12} {fixture['task_type']:<24}"
                  f"{fixture['difficulty']}")
        print("\nDry run: nothing was called.")
        return 0

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("\nGROQ_API_KEY is not set. Nothing was called.")
        return 1
    if input("\nType 'yes' to make these calls: ").strip().lower() != "yes":
        print("Cancelled. Nothing was called.")
        return 1

    run_id = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"{run_id}-judge.jsonl"

    client = GatewayClient(logbook=Logbook(log_path, prices),
                           adapters={"groq": GroqAdapter(api_key=api_key)},
                           tiers=tiers.as_client_map(),
                           policy_version=policy.version)

    rows: list[dict[str, Any]] = []
    comparisons = []
    skipped: list[dict[str, str]] = []
    print(f"\n{'pair':<16}{'A check':>9}{'B check':>9}{'result':>15}"
          f"{'answers $':>12}{'judge $':>11}")

    done = 0
    for sample in range(1, args.samples + 1):
        for fixture in items:
            if done and args.pace_seconds:
                time.sleep(args.pace_seconds)
            done += 1

            pair_id = f"{fixture['id']}#{sample}"
            rule = policy.rule_for(fixture["task_type"])
            prompt = prompts.build(
                rule, fixture["input"], context=fixture.get("context"),
                required_keys=fixture["expected"].get("required_keys"))
            try:
                a = answer(client, fixture=fixture, rule=rule, policy=policy,
                           tier=args.a_tier, prompt=prompt, sample=sample)
                b = answer(client, fixture=fixture, rule=rule, policy=policy,
                           tier=args.b_tier, prompt=prompt, sample=sample)
            except ProviderError as exc:
                # Judging needs both answers. One missing is a skipped pair,
                # reported as skipped -- never a verdict inferred from one side.
                skipped.append({"pair_id": pair_id, "error": str(exc)})
                print(f"{pair_id:<16}{'skipped -- ' + str(exc)[:55]}")
                continue

            try:
                comparison = compare(
                    client, fixture_id=pair_id, asks=rule["description"],
                    input_text=fixture["input"], answer_a=a["text"],
                    answer_b=b["text"], a_label=args.a_tier, b_label=args.b_tier,
                    context=fixture.get("context"), tier=args.judge_tier,
                    max_tokens=JUDGE_MAX_TOKENS)
            except ProviderError as exc:
                skipped.append({"pair_id": pair_id, "error": f"judge: {exc}"})
                print(f"{pair_id:<16}{'judge failed -- ' + str(exc)[:50]}")
                continue

            comparisons.append(comparison)
            answers_cost = a["cost_usd"] + b["cost_usd"]
            rows.append({
                "pair_id": pair_id, "id": fixture["id"], "sample": sample,
                "task_type": fixture["task_type"],
                "difficulty": fixture["difficulty"], "a": a, "b": b,
                "answers_cost_usd": answers_cost,
                **comparison.to_record(),
            })
            print(f"{pair_id:<16}"
                  f"{'ok' if a['passed_check'] else 'FAIL':>9}"
                  f"{'ok' if b['passed_check'] else 'FAIL':>9}"
                  f"{comparison.result:>15}{answers_cost:>12.6f}"
                  f"{comparison.cost_usd:>11.6f}")

    # -- what the run measured -------------------------------------------

    stats = summarize(comparisons)
    answers_total = sum(r["answers_cost_usd"] for r in rows)
    counts = stats["counts"]

    print(f"\ncompared {stats['comparisons']} over {len(items)} fixtures · "
          f"decided {stats['decided']} · inconsistent {counts['inconsistent']} · "
          f"unparsed {counts['unparsed']}")
    print(f"{args.a_tier} won {counts['a']} · {args.b_tier} won {counts['b']} · "
          f"tie {counts['tie']}")
    print(f"cost ${answers_total:.5f} answers + ${stats['cost_usd']:.5f} judging "
          f"= ${answers_total + stats['cost_usd']:.5f}")
    if skipped:
        print(f"\nskipped {len(skipped)}:")
        for row in skipped:
            print(f"  {row['pair_id']:<16} {row['error'][:90]}")

    print("\nThese verdicts are MODEL JUDGMENTS, not ground truth. An "
          "inconsistent\nresult means the judge changed its mind when the "
          "answers swapped places.\nSeveral samples of one fixture are not "
          "several independent tasks.")

    results_path = RESULTS_DIR / f"{run_id}-judge.json"
    results_path.write_text(json.dumps({
        "run_id": run_id, "run_on": date.today().isoformat(),
        "policy_version": policy.version, "tiers_version": tiers.version,
        "prices_version": prices.version,
        "fixtures_frozen_on": manifest["frozen_on"],
        "a_tier": args.a_tier, "b_tier": args.b_tier, "judge_tier": args.judge_tier,
        "judge_max_tokens": JUDGE_MAX_TOKENS,
        "fixtures": len(items), "samples": args.samples,
        "summary": stats, "answers_cost_usd": answers_total,
        "skipped": skipped, "rows": rows,
    }, indent=2) + "\n", encoding="utf-8")

    print(f"\nlogbook  {log_path}")
    print(f"results  {results_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())