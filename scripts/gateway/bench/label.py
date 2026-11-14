"""Label the fixture set: interactively, or from an answer sheet.

Labels are human judgments -- the expected answer, and the expected tier (the
cheapest tier you expect to get it right). Deliberately NOT shown: the
router's decision, or a tier you gave the fixture earlier. Either would
anchor your judgment.

Two ways to work:

    # answer sheet (recommended): fixture text and your answer side by side
    python scripts/gateway/bench/label.py --template answers.json --ids a,b,c
    ... edit answers.json in your editor ...
    Remove-Item scripts/gateway/bench/manifest.json
    python scripts/gateway/bench/label.py --by "Your Name" --from answers.json

    # one fixture at a time, in the terminal
    python scripts/gateway/bench/label.py --by "Your Name"              # unreviewed only
    python scripts/gateway/bench/label.py --by "Your Name" --redo       # also your own
    python scripts/gateway/bench/label.py --by "Your Name" --ids a,b,c  # just these

A json task carries acceptable answers per field. The key check can only see
that a field is present, not that its value is right, so these are what make
extraction gradeable (Sprint 5).

Nothing is written until it validates. Writing labels refuses to run once the
set is frozen; writing an answer sheet does not, because it only reads.
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

HOW_TO_FILL = {
    "json": ("Fill 'values' with every wording you would accept as correct for "
             "that field. Leave a field's list empty to check only that the "
             "field is present. Fields are about what the speaker said -- "
             "'direction' means which way the number goes, not sentiment."),
    "label": "Set 'label' to one of the allowed labels listed above it.",
    "verdict": "Set 'label' to one of the allowed labels listed above it.",
    "text": ("Nothing to fill in here -- this answer is graded against the "
             "input itself. Just set the tier."),
}


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


def read_sheet(path: Path) -> list[dict[str, Any]]:
    """Load an answer sheet.

    utf-8-sig, not utf-8: PowerShell's Set-Content writes a byte-order mark and
    json.loads rejects it outright. utf-8-sig reads files with or without one.
    """
    return json.loads(path.read_text(encoding="utf-8-sig"))


# ---------------------------------------------------------------- answer sheet

def build_template(fixtures: list[dict[str, Any]], policy: Policy) -> list[dict[str, Any]]:
    """An answer sheet: the fixture's own text beside the answer to fill in.

    Every key starting with '_' is context for the reader and is discarded on
    the way back in. Only 'expected' and 'tier' are read.
    """
    sheet = []
    for fixture in fixtures:
        rule = policy.rule_for(fixture["task_type"])
        expected = copy.deepcopy(fixture["expected"])
        entry: dict[str, Any] = {
            "id": fixture["id"],
            "_task": f"{fixture['task_type']} ({fixture['difficulty']})",
            "_asks": rule["description"],
            "_input": fixture["input"],
        }
        if fixture.get("notes"):
            entry["_notes"] = fixture["notes"]
        if fixture.get("context"):
            entry["_passages"] = {str(n): p for n, p in enumerate(fixture["context"])}
        if rule["output"] in ("label", "verdict"):
            entry["_allowed_labels"] = list(rule["labels"])
        if rule["output"] == "json":
            values = {k: list((expected.get("values") or {}).get(k, []))
                      for k in expected["required_keys"]}
            expected["values"] = values
        entry["_how_to_fill"] = HOW_TO_FILL.get(rule["output"], HOW_TO_FILL["text"])
        entry["_tier_means"] = (f"cheapest tier you expect to get it right: "
                                f"{', '.join(policy.tier_order)}")
        entry["expected"] = expected
        entry["tier"] = fixture.get("expected_tier")
        sheet.append(entry)
    return sheet


def clean_expected(expected: dict[str, Any]) -> dict[str, Any]:
    """Drop the reader's context keys and any field left blank."""
    exp = {k: v for k, v in expected.items() if not k.startswith("_")}
    values = exp.get("values")
    if isinstance(values, dict):
        kept = {}
        for key, accepted in values.items():
            if isinstance(accepted, list):
                accepted = [s.strip() for s in accepted
                            if isinstance(s, str) and s.strip()]
            if accepted:
                kept[key] = accepted
        if kept:
            exp["values"] = kept
        else:
            exp.pop("values", None)
    return exp


def label_from_sheet(sheet: list[dict[str, Any]], fixtures: list[dict[str, Any]],
                     policy: Policy, *, by: str, on: str,
                     confirm=input) -> tuple[int, list[str]]:
    """Apply an edited answer sheet. Validates everything before writing anything."""
    by_id = {f["id"]: f for f in fixtures}
    problems = []
    staged: list[tuple[dict[str, Any], dict[str, Any]]] = []

    for entry in sheet:
        fixture_id = entry.get("id")
        fixture = by_id.get(fixture_id)
        if fixture is None:
            problems.append(f"{fixture_id!r}: no such fixture")
            continue
        tier = entry.get("tier")
        if tier not in policy.tier_order:
            problems.append(f"{fixture_id}: tier must be one of "
                            f"{policy.tier_order}, got {tier!r}")
            continue
        candidate = copy.deepcopy(fixture)
        apply_label(candidate, policy=policy, tier=tier, by=by, on=on,
                    expected=clean_expected(entry.get("expected") or {}))
        try:
            fx.validate([candidate], policy)
        except fx.FixtureError as exc:
            problems.append(str(exc))
            continue
        staged.append((fixture, candidate))

    if problems:
        return 0, problems

    # Count what actually differs, so a sheet applied unedited cannot look like
    # a successful relabelling. This happened four times on 2026-10-01.
    changed = [(f, c) for f, c in staged
               if f["expected"] != c["expected"]
               or f.get("expected_tier") != c["expected_tier"]]

    print(f"\n{len(staged)} fixture(s) in the sheet, {len(changed)} with changes. "
          f"Nothing is written yet.\n")
    for fixture, candidate in staged:
        differs = (fixture["expected"] != candidate["expected"]
                   or fixture.get("expected_tier") != candidate["expected_tier"])
        print("=" * 72)
        print(f"{fixture['id']}  {'CHANGED' if differs else 'unchanged'}  --  "
              f"{fixture['input'][:70]}"
              f"{'...' if len(fixture['input']) > 70 else ''}")
        print(f"  was: tier={fixture.get('expected_tier')}  "
              f"{json.dumps(fixture['expected'], ensure_ascii=False)}")
        print(f"  now: tier={candidate['expected_tier']}  "
              f"{json.dumps(candidate['expected'], ensure_ascii=False)}")
    print("=" * 72)

    if not changed:
        return 0, ["nothing in this sheet differs from the fixtures on disk -- "
                   "the sheet was applied unedited. Nothing written."]

    if confirm("\nWrite these? [y/N] ").strip().lower() not in ("y", "yes"):
        return 0, ["cancelled -- nothing written"]

    for fixture, candidate in staged:
        fixture.clear()
        fixture.update(candidate)
    save(fixtures)
    return len(changed), []


# ---------------------------------------------------------------- interactive

def _ask_json_expected(exp: dict[str, Any]) -> dict[str, Any]:
    """Required keys, then acceptable answers per key. Confirmed before it returns.

    Instructions print above the prompt, never on the input line -- an input
    line that explains itself invites you to type the explanation back.
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


def label_interactively(pending: list[dict[str, Any]], fixtures: list[dict[str, Any]],
                        policy: Policy, *, by: str, on: str) -> int:
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
        apply_label(candidate, policy=policy, tier=tier, by=by, on=on, expected=expected)
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
    return done


def main() -> int:
    parser = argparse.ArgumentParser(description="Label fixtures.")
    parser.add_argument("--by", help="your name, recorded as labeled_by")
    parser.add_argument("--redo", action="store_true",
                        help="also relabel fixtures you have already labeled")
    parser.add_argument("--ids", default="",
                        help="comma-separated fixture ids, e.g. sent-004,topic-001")
    parser.add_argument("--template", metavar="PATH",
                        help="write an answer sheet to PATH and exit")
    parser.add_argument("--from", dest="from_file", metavar="PATH",
                        help="apply an edited answer sheet")
    args = parser.parse_args()

    policy = Policy.load(TierConfig.load())
    fixtures = fx.validate(fx.load(), policy)

    if args.ids:
        wanted = _split(args.ids)
        unknown = sorted(set(wanted) - {f["id"] for f in fixtures})
        if unknown:
            print(f"Unknown fixture id(s): {', '.join(unknown)}. Nothing changed.")
            return 1
        selected = [f for f in fixtures if f["id"] in set(wanted)]
    else:
        selected = [f for f in fixtures
                    if f["labeled_by"] == fx.UNREVIEWED
                    or (args.redo and args.by and f["labeled_by"] == args.by)]

    # Writing an answer sheet only READS the fixtures, so a frozen set is no
    # reason to refuse it -- the freeze check belongs below, in front of the
    # paths that actually write labels. It sat above this branch until
    # 2026-10-01, where it silently blocked three attempts at the answer key.
    if args.template:
        path = Path(args.template)
        path.write_text(
            json.dumps(build_template(selected, policy), indent=2, ensure_ascii=False)
            + "\n", encoding="utf-8")
        print(f"Wrote {len(selected)} fixture(s) to {path}.")
        print("Edit 'expected' and 'tier' in that file, then unfreeze and run:")
        print(f"  Remove-Item {fx.MANIFEST_PATH}")
        print(f'  python scripts/gateway/bench/label.py --by "Your Name" '
              f'--from {path}')
        return 0

    if fx.MANIFEST_PATH.exists():
        print("The fixture set is frozen (manifest.json exists). Relabeling changes "
              "the locked set: bump the version and log it before editing.")
        return 1

    if not args.by:
        print("--by is required (your name is recorded as labeled_by).")
        return 1
    today = date.today().isoformat()

    if args.from_file:
        sheet = read_sheet(Path(args.from_file))
        done, problems = label_from_sheet(sheet, fixtures, policy, by=args.by, on=today)
        for problem in problems:
            print(f"  {problem}")
        if problems:
            print("Nothing written.")
            return 1
        print(f"\n{done} labeled.")
    else:
        done = label_interactively(selected, fixtures, policy, by=args.by, on=today)
        print(f"\n{done} labeled this session.")

    remaining = sum(1 for f in fixtures if f["labeled_by"] == fx.UNREVIEWED)
    print(f"{remaining} still unreviewed.")
    if remaining == 0:
        print("All reviewed. Lock the set with: "
              "python scripts/gateway/bench/audit.py --freeze")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())