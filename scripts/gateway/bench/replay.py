"""Replay Mycroft's prepared requests through the gateway, without calling anything.

Sprint 11. Sprint 10 found 16 requests in `contradiction-detection-agent` that
were fully prepared and never sent, and two reasons the gateway could not serve
them as written. This asks the next question: if those requests went through
the gateway as it is configured today, what would happen to each one, and what
would it cost?

Nothing is called. The router is a pure function of task type and input length,
and the price table is arithmetic, so a request's fate can be computed from its
size alone. This is the same technique the Sprint 8 decision used.

One thing this CANNOT do is compare against what the recipe would have cost.
The model it names, `llama-3.3-70b-versatile`, has no published per-token rate
(FINDINGS section 4), so there is no number to compare against. A saving cannot
be claimed here, only a cost stated.

Two cost figures are reported for every request, and the gap between them is
the honest width of the estimate:

  upper bound -- one token per character in, the full token budget out. The
    convention used in run.py's cost ceiling: loose, never an underestimate.
  estimate -- four characters per token in, the budget out. Closer to what
    English costs, and still generous on output.

Usage:
    python scripts/gateway/bench/replay.py
    python scripts/gateway/bench/replay.py --corpus <path>
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gateway.policy import Policy, UnknownTaskType
from gateway.prices import PriceTable, UnknownModelPrice
from gateway.router import InputTooLarge, PinnedTask, route
from gateway.tiers import TierConfig

CORPUS_DIR = Path(__file__).with_name("corpus")
RESULTS_DIR = Path(__file__).with_name("results")

# A human mapping from a recipe's own word for what it is doing to the task
# type the policy knows. It is a judgment, not a measurement: the prompt in
# `llm_review_of_flags` asks a model to review contradiction flags, which is
# what `contradiction_detection` is for. An action with no mapping is reported
# as unmapped, never guessed -- guessing here would route real work by
# coincidence.
ACTION_TO_TASK = {
    "llm_review_of_flags": "contradiction_detection",
}

CHARS_PER_TOKEN = 4  # English, roughly. Used only for the estimate.


def latest_corpus(corpus_dir: Path = CORPUS_DIR) -> Path | None:
    files = sorted(corpus_dir.glob("*-corpus.jsonl"))
    return files[-1] if files else None


def load_corpus(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in
            path.read_text(encoding="utf-8").splitlines() if line.strip()]


def replay_one(record: dict[str, Any], *, policy: Policy, tiers: TierConfig,
               prices: PriceTable) -> dict[str, Any]:
    """What the gateway would do with one prepared request."""
    out: dict[str, Any] = {
        "source": record["source"],
        "recipe": record.get("recipe"),
        "action": record.get("action"),
        "prompt_chars": record.get("prompt_chars"),
        "model_named": record.get("model_named"),
        "max_tokens_asked": record.get("max_tokens"),
        "task_type": None,
        "tier": None,
        "escalate_to": None,
        "max_tokens_served": None,
        "cost_upper_bound_usd": None,
        "cost_estimate_usd": None,
        "problems": [],
    }

    task_type = ACTION_TO_TASK.get(record.get("action"))
    if task_type is None:
        out["problems"].append("unmapped_action")
        return out
    out["task_type"] = task_type

    chars = record.get("prompt_chars") or 0
    if not chars:
        out["problems"].append("empty_payload")
        return out

    try:
        # The router reads length, not words, so a placeholder of the right
        # size routes exactly as the real prompt would -- and the corpus does
        # not carry the real prompt, on purpose.
        decision = route(task_type=task_type, text="x" * chars,
                         policy=policy, tiers=tiers)
    except (UnknownTaskType, PinnedTask, InputTooLarge) as exc:
        out["problems"].append(f"not_routable: {exc}")
        return out

    out["tier"] = decision.tier
    out["escalate_to"] = decision.escalate_to
    out["max_tokens_served"] = decision.max_tokens

    spec = tiers.spec(decision.tier)
    try:
        out["cost_upper_bound_usd"] = prices.cost_usd(
            spec["provider"], spec["model"], chars, decision.max_tokens)
        out["cost_estimate_usd"] = prices.cost_usd(
            spec["provider"], spec["model"],
            max(1, chars // CHARS_PER_TOKEN), decision.max_tokens)
    except UnknownModelPrice as exc:
        out["problems"].append(f"tier_unpriced: {exc}")

    # What the recipe asked for, against what the gateway would give it.
    named = record.get("model_named")
    if named:
        try:
            prices.rates("groq", named)
        except UnknownModelPrice:
            out["problems"].append("named_model_unpriced")

    asked = record.get("max_tokens")
    if isinstance(asked, int) and asked > decision.max_tokens:
        out["problems"].append(
            f"budget_cut: asked {asked}, would get {decision.max_tokens}")

    return out


def summarise(rows: list[dict[str, Any]]) -> dict[str, Any]:
    served = [r for r in rows if r["tier"] and r["cost_upper_bound_usd"] is not None]
    problems: dict[str, int] = {}
    for row in rows:
        for problem in row["problems"]:
            key = problem.split(":")[0]
            problems[key] = problems.get(key, 0) + 1
    return {
        "requests": len(rows),
        "routable": len(served),
        "by_tier": {t: sum(1 for r in served if r["tier"] == t)
                    for t in sorted({r["tier"] for r in served})},
        "problems": dict(sorted(problems.items(), key=lambda kv: -kv[1])),
        "cost_upper_bound_usd": round(sum(r["cost_upper_bound_usd"] for r in served), 6),
        "cost_estimate_usd": round(sum(r["cost_estimate_usd"] for r in served), 6),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay prepared requests through the gateway. No calls.")
    parser.add_argument("--corpus", help="a corpus JSONL (default: the newest)")
    args = parser.parse_args()

    corpus_file = Path(args.corpus) if args.corpus else latest_corpus()
    if corpus_file is None or not corpus_file.exists():
        print("No corpus found. Run bench/corpus.py first.")
        return 1

    records = [r for r in load_corpus(corpus_file)
               if not r.get("live_call_performed")]
    if not records:
        print(f"{corpus_file.name} holds no prepared requests to replay.")
        return 1

    tiers = TierConfig.load()
    policy = Policy.load(tiers)
    prices = PriceTable.load()

    rows = [replay_one(r, policy=policy, tiers=tiers, prices=prices) for r in records]
    stats = summarise(rows)

    print(f"corpus  {corpus_file.name}")
    print(f"policy {policy.version} · tiers {tiers.version} · prices {prices.version}")
    print(f"\n{stats['requests']} prepared requests, {stats['routable']} routable\n")

    print(f"{'source':<26}{'chars':>7}{'tier':>8}{'serves':>8}{'asked':>7}"
          f"{'est $':>10}{'max $':>10}")
    for row in rows:
        name = Path(row["source"]).name
        if row["tier"] is None:
            print(f"{name:<26}{row['prompt_chars'] or 0:>7}"
                  f"{'  -- ' + ', '.join(row['problems']):<33}")
            continue
        print(f"{name:<26}{row['prompt_chars']:>7}{row['tier']:>8}"
              f"{row['max_tokens_served']:>8}{row['max_tokens_asked'] or '-':>7}"
              f"{row['cost_estimate_usd']:>10.6f}{row['cost_upper_bound_usd']:>10.6f}")

    print(f"\nrouted to: {stats['by_tier']}")
    print(f"whole batch: ${stats['cost_estimate_usd']:.6f} estimated, "
          f"${stats['cost_upper_bound_usd']:.6f} upper bound")

    print(f"\nproblems: {stats['problems']}")
    print("\nWhat this cannot say: the recipe names llama-3.3-70b-versatile,")
    print("which has no published per-token rate, so there is no figure to")
    print("compare against. The gateway's cost is stated; no saving is claimed.")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"{date.today().isoformat()}-replay.json"
    out.write_text(json.dumps({
        "replayed_on": date.today().isoformat(),
        "corpus": corpus_file.name,
        "policy_version": policy.version,
        "tiers_version": tiers.version,
        "prices_version": prices.version,
        "action_to_task": ACTION_TO_TASK,
        "chars_per_token_estimate": CHARS_PER_TOKEN,
        "summary": stats,
        "rows": rows,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nreport  {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())