"""Label the fixture set, one fixture at a time.

Shows each fixture's task definition, its input, and its drafted expected
answer, then asks you to confirm or correct the answer and to set the
expected tier -- the cheapest tier you expect to get it right.

Deliberately NOT shown: the router's decision for the fixture, or a tier you
gave it earlier. Either would anchor your judgment.

Usage:
    python scripts/gateway/bench/label.py --by "Your Name"              # unreviewed only
    python scripts/gateway/bench/label.py --by "Your Name" --redo       # also your own labels
    python scripts/gateway/bench/label.py --by "Your Name" --ids a,b,c  # just these fixtures

Progress is saved after every fixture, so you can stop and resume.
Refuses to run once the set is frozen (manifest.json exists).
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gateway.bench import fixtures as fx
from gateway.policy import Policy
from gateway.tiers import TierConfig


def apply_label(fixture: dict[str, Any], *, policy: Policy, tier: str, by: str,
                on: str, expected: dict[str, Any] | None = None) -> dict[str, Any]:
    """Record a human label on one fixture. Pass `expected` to correct the answer."""
    if tier not in policy.tier_order:
        raise ValueError(f"tier must be one of {policy.tier_order}, got {tier!r}")
    if not by.strip() or by == fx.UNREVIEWED:
        raise ValueError("labeled_by must be your name")
    if expected is not None:
        fixture["expected"] = expected
    fixture["expected_tier"] = tier
    fixture["labeled_by"] = by
    fixture["labeled_on"] = on
    return fixture


def save(fixtures: list[dict[str, Any]], fixtures_dir: Path = fx.FIXTURES_DIR) -> None:
    """Rewrite each fixture file, one fixture per line, in its original order."""
    by_file: dict[str, list[dict[str, Any]]] = {}
    for fixture in fixtures:
        by_file.setdefault(fixture["_file"], []).append(fixture)
    for name, rows in by_file.items():
        lines = [json.dumps({k: v for k, v in r.items() if k != "_file"},
                            ensure_ascii=False) for r in rows]
        (fixtures_dir / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _ask_expected(fixture: dict[str, Any], rule: dict[str, Any]) -> dict[str, Any] | None:
    """Confirm or correct the drafted answer. None means keep it."""
    exp = fixture["expected"]
    if rule["output"] in ("label", "verdict"):
        while True:
            got = input(f"  Expected label [{exp['label']}] -- Enter to keep, "
                        f"or one of {', '.join(rule['labels'])}: ").strip()
            if not got:
                return None
            if got in rule["labels"]:
                return {**exp, "label": got}
            print("    not a valid label")
    if rule["output"] == "json":
        got = input(f"  Required keys [{', '.join(exp['required_keys'])}] -- "
                    f"Enter to keep, or a comma-separated list: ").strip()
        if not got:
            return None
        return {**exp, "required_keys": [k.strip() for k in got.split(",") if k.strip()]}
    if rule["validator"] == "cites_context":
        while True:
            got = input(f"  Passage that answers it [{exp['cite']}] -- Enter to keep, "
                        f"or a passage number: ").strip()
            if not got:
                return None
            if got.isdigit() and int(got) < len(fixture["context"]):
                return {**exp, "cite": int(got)}
            print("    not a valid passage number")
    return None  # summarization: the answer is graded against the input itself


def main() -> int:
    parser = argparse.ArgumentParser(description="Label fixtures one at a time.")
    parser.add_argument("--by", required=True, help="your name, recorded as labeled_by")
    parser.add_argument("--redo", action="store_true",
                        help="also relabel fixtures you have already labeled")
    parser.add_argument("--ids", default="",
                        help="comma-separated fixture ids to (re)label, e.g. sent-004,topic-001")
    args = parser.parse_args()

    if fx.MANIFEST_PATH.exists():
        print("The fixture set is frozen (manifest.json exists). Relabeling changes "
              "the locked set: bump the version and log it before editing.")
        return 1

    policy = Policy.load(TierConfig.load())
    fixtures = fx.validate(fx.load(), policy)

    if args.ids:
        wanted = [i.strip() for i in args.ids.split(",") if i.strip()]
        unknown = sorted(set(wanted) - {f["id"] for f in fixtures})
        if unknown:
            print(f"Unknown fixture id(s): {', '.join(unknown)}. Nothing changed.")
            return 1
        pending = [f for f in fixtures if f["id"] in set(wanted)]
    else:
        pending = [f for f in fixtures
                   if f["labeled_by"] == fx.UNREVIEWED
                   or (args.redo and f["labeled_by"] == args.by)]
    today = date.today().isoformat()

    print(f"{len(pending)} fixture(s) to label. Type q at a tier prompt to stop; "
          f"progress is saved.")
    print("Tier = the cheapest tier you expect to get it RIGHT. "
          "The router's choice is not shown, on purpose.\n")

    done = 0
    for i, fixture in enumerate(pending, 1):
        rule = policy.rule_for(fixture["task_type"])
        print("=" * 72)
        print(f"[{i}/{len(pending)}] {fixture['id']}  {fixture['task_type']}  "
              f"({fixture['difficulty']})")
        print(f"  TASK: {rule['description']}")
        if fixture.get("notes"):
            print(f"  notes: {fixture['notes']}")
        print(f"\n  INPUT ({len(fixture['input']):,} chars):")
        for line in fixture["input"].splitlines():
            print(f"    {line}")
        for n, passage in enumerate(fixture.get("context") or []):
            print(f"    passage {n}: {passage}")
        print()

        expected = _ask_expected(fixture, rule)

        tier = ""
        while tier not in policy.tier_order and tier not in ("q", "s"):
            tier = input(f"  Cheapest tier that gets this right "
                         f"({'/'.join(policy.tier_order)}), s=skip, q=quit: ").strip().lower()
        if tier == "q":
            break
        if tier == "s":
            continue

        candidate = copy.deepcopy(fixture)
        apply_label(candidate, policy=policy, tier=tier, by=args.by,
                    on=today, expected=expected)
        try:
            fx.validate([candidate], policy)
        except fx.FixtureError as exc:
            print(f"  not saved: {exc}")
            continue
        fixture.clear()
        fixture.update(candidate)
        save(fixtures)
        done += 1
        print("  saved.")

    remaining = sum(1 for f in fixtures if f["labeled_by"] == fx.UNREVIEWED)
    print(f"\n{done} labeled this session, {remaining} still unreviewed.")
    if remaining == 0:
        print("All reviewed. Lock the set with: "
              "python scripts/gateway/bench/audit.py --freeze")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())