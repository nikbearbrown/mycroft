"""Label the fixture set, one fixture at a time.

Shows each fixture's task definition, its input, and its drafted expected
answer, then asks you to confirm or correct the answer and to set the
expected tier -- the cheapest tier you expect to get it right.

For a json task it also asks for acceptable answers per field. The key check
can only see that a field is present, not that its value is right, so these
are what make extraction gradeable (Sprint 5). Nothing is saved until you
have seen a summary of it and confirmed.

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


def _split(text: str) -> list[str]:
    return [part.strip() for part in text.split(",") if part.strip()]


def _ask_json_expected(exp: dict[str, Any]) -> dict[str, Any]:
    """Required keys, then the acceptable answers per key. Confirmed before it returns.

    The instructions are printed above the prompt, never on the input line --
    an input line that explains itself invites you to type the explanation back.
    """
    while True:
        print(f"  Required keys are: {', '.join(exp['required_keys'])}")
        print("  Press Enter to keep them, or type a replacement comma-separated list.")
        got = input("  keys> ").strip()
        keys = _split(got) if got else list(exp["required_keys"])

        print("\n  Now the acceptable answers for each field: every wording you would")
        print("  accept as right, comma-separated. Press Enter to leave a field blank")
        print("  (blank means only its presence is checked, not its value).")
        print("  Example, for a field holding a direction:  up, above, higher, raise")
        values = {k: list(v) for k, v in (exp.get("values") or {}).items() if k in keys}
        for key in keys:
            if values.get(key):
                print(f"    {key} currently: {', '.join(values[key])}")
            got = input(f"    {key}> ").strip()
            if got:
                values[key] = _split(got)

        updated = {**exp, "required_keys": keys}
        if values:
            updated["values"] = values
        else:
            updated.pop("values", None)

        print("\n  To be saved:")
        print(f"    required_keys: {', '.join(keys)}")
        for key in keys:
            accepted = values.get(key)
            shown = ", ".join(accepted) if accepted else "(blank -- value not checked)"
            print(f"    {key}: {shown}")
        if input("  Correct? [y/N] ").strip().lower() in ("y", "yes"):
            return updated
        print("  Starting this fixture's answer over.\n")


def _ask_expected(fixture: dict[str, Any], rule: dict[str, Any]) -> dict[str, Any] | None:
    """Confirm or correct the drafted answer. None means keep it."""
    exp = fixture["expected"]
    if rule["output"] in ("label", "verdict"):
        while True:
            print(f"  Expected answer is: {exp['label']}")
            print(f"  Press Enter to keep it, or type one of: {', '.join(rule['labels'])}")
            got = input("  answer> ").strip()
            if not got:
                return None
            if got in rule["labels"]:
                return {**exp, "label": got}
            print("    not a valid label")
    if rule["output"] == "json":
        return _ask_json_expected(exp)
    if rule["validator"] == "cites_context":
        while True:
            print(f"  Passage that answers it: {exp['cite']}")
            print("  Press Enter to keep it, or type a passage number.")
            got = input("  passage> ").strip()
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
        wanted = _split(args.ids)
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
            print(f"\n  Cheapest tier that gets this right: "
                  f"{', '.join(policy.tier_order)} -- or s to skip, q to quit.")
            tier = input("  tier> ").strip().lower()
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