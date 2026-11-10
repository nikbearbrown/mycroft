"""Score answer pairs by hand, blind. The human half of Sprint 6.

The judge produced verdicts. Nothing yet says whether those verdicts are worth
anything, and the only way to find out is for a person to score the same pairs
independently and compare. This tool is the "independently" part, so it hides
three things on purpose:

  - which tier wrote which answer,
  - which answer the judge preferred,
  - how many times you have already picked one side.

Answers are shown in a random order per pair, and which one was shown first is
recorded, so order bias in the HUMAN can be measured the same way the judge's
was. Nothing here reads a verdict; agreement.py does that afterwards.

The task description comes from policy.json and the source text from the frozen
fixture set, rather than from the results file -- so "which answer does the task
better" can be judged against the task as defined and the passage the answer was
supposed to use.

Progress is saved after every pair, so you can stop and resume.

Usage:
    python scripts/gateway/bench/score.py --by "Your Name"
    python scripts/gateway/bench/score.py --by "Your Name" --results <path>
    python scripts/gateway/bench/score.py --by "Your Name" --limit 10
    python scripts/gateway/bench/score.py --by "Your Name" --redo
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gateway.bench import fixtures as fx
from gateway.policy import Policy
from gateway.tiers import TierConfig

RESULTS_DIR = Path(__file__).with_name("results")
SCORES_DIR = Path(__file__).with_name("scores")

PICKS = {"1": "first", "2": "second", "t": "tie"}


def latest_results(results_dir: Path = RESULTS_DIR) -> Path | None:
    """The newest judge run. Named by timestamp, so sorting by name is enough."""
    runs = sorted(results_dir.glob("*-judge.json"))
    return runs[-1] if runs else None


def scores_path(run_id: str, by: str, scores_dir: Path = SCORES_DIR) -> Path:
    slug = "".join(c if c.isalnum() else "-" for c in by.strip().lower()).strip("-")
    return scores_dir / f"{run_id}-{slug or 'scorer'}.json"


def load_scores(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    saved = json.loads(path.read_text(encoding="utf-8-sig"))
    return {row["pair_id"]: row for row in saved.get("scores", [])}


def save_scores(path: Path, *, run_id: str, by: str, results_file: str,
                scores: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "run_id": run_id,
        "scored_by": by,
        "results_file": results_file,
        "blind": True,
        "note": "tiers and judge verdicts were hidden while scoring",
        "scores": [scores[k] for k in sorted(scores)],
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def shown_order(pair_id: str, by: str) -> tuple[str, str]:
    """Which answer appears first. Seeded, so a resumed session shows the same order."""
    rng = random.Random(f"{by}|{pair_id}")
    return ("a", "b") if rng.random() < 0.5 else ("b", "a")


def resolve_pick(pick: str, order: tuple[str, str]) -> str:
    """Turn a choice about position into a choice about an answer."""
    if pick == "tie":
        return "tie"
    return order[0] if pick == "first" else order[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Score judged pairs by hand, blind.")
    parser.add_argument("--by", required=True, help="your name, recorded as scored_by")
    parser.add_argument("--results", help="a judge results file (default: the newest)")
    parser.add_argument("--redo", action="store_true",
                        help="score pairs you have already scored")
    parser.add_argument("--limit", type=int, default=0,
                        help="stop after N pairs this session")
    args = parser.parse_args()

    results_file = Path(args.results) if args.results else latest_results()
    if results_file is None or not results_file.exists():
        print("No judge results file found. Run judge_run.py first.")
        return 1

    data = json.loads(results_file.read_text(encoding="utf-8-sig"))
    rows = data.get("rows") or []
    if not rows:
        print(f"{results_file} has no rows to score.")
        return 1

    policy = Policy.load(TierConfig.load())
    by_fixture = {f["id"]: f for f in fx.validate(fx.load(), policy)}

    run_id = data["run_id"]
    out_path = scores_path(run_id, args.by)
    scores = load_scores(out_path)

    pending = [r for r in rows if args.redo or r["pair_id"] not in scores]
    if args.limit:
        pending = pending[:args.limit]

    if not pending:
        print(f"All {len(rows)} pairs already scored -> {out_path}")
        return 0

    # Shuffled so one fixture's samples do not arrive in a block: scoring four
    # versions of the same summary in a row invites scoring them against each
    # other instead of against the task.
    random.Random(f"{args.by}|{run_id}").shuffle(pending)

    print(f"{len(pending)} pair(s) to score, from {results_file.name}.")
    print("Two answers, random order. Which one does the task better?")
    print("Neither the model that wrote each answer nor the judge's verdict is")
    print("shown -- that is the point. 1, 2, t for tie, s to skip, q to quit.\n")

    done = 0
    for n, row in enumerate(pending, 1):
        fixture = by_fixture.get(row["id"])
        rule = policy.rule_for(row["task_type"])
        order = shown_order(row["pair_id"], args.by)
        first, second = row[order[0]]["text"], row[order[1]]["text"]

        print("=" * 72)
        print(f"[{n}/{len(pending)}]  {row['task_type']}")
        print(f"\nTASK: {rule['description']}")
        if fixture:
            print("\nINPUT:")
            for line in fixture["input"].splitlines():
                print(f"  {line}")
            for i, passage in enumerate(fixture.get("context") or []):
                print(f"  passage [{i}] {passage}")
        print("\nANSWER 1:")
        for line in first.splitlines():
            print(f"  {line}")
        print("\nANSWER 2:")
        for line in second.splitlines():
            print(f"  {line}")

        pick = ""
        while pick not in PICKS and pick not in ("s", "q"):
            print("\n  Which does the task better? 1, 2, t = tie, s = skip, q = quit")
            pick = input("  pick> ").strip().lower()
        if pick == "q":
            break
        if pick == "s":
            continue

        note = input("  why, in a few words (optional): ").strip()

        scores[row["pair_id"]] = {
            "pair_id": row["pair_id"],
            "fixture_id": row["id"],
            "task_type": row["task_type"],
            "shown_first": order[0],
            "picked_position": PICKS[pick],
            "pick": resolve_pick(PICKS[pick], order),
            "note": note,
            "scored_by": args.by,
            "scored_at": datetime.now(timezone.utc).isoformat(),
        }
        save_scores(out_path, run_id=run_id, by=args.by,
                    results_file=results_file.name, scores=scores)
        done += 1
        print("  saved.")

    remaining = len([r for r in rows if r["pair_id"] not in scores])
    print(f"\n{done} scored this session. {remaining} of {len(rows)} still unscored.")
    print(f"scores  {out_path}")
    if remaining == 0:
        print("\nAll scored. Measure agreement with:")
        print(f"  python scripts/gateway/bench/agreement.py --scores {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())