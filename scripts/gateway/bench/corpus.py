"""Collect Mycroft's model requests into one corpus, wherever they come from.

Sprint 10. The plan was a recorder that captures live calls. The inventory
killed it: every run artifact in this repository says
`live_call_performed: false`. Every recipe is gated at Gate 5 and runs in
sample mode, and the only live model calls ever made here are the gateway's
own. There is nothing to record.

What does exist is requests that were fully prepared and never sent -- real
prompts, a named model, a chosen budget -- plus the gateway's own logbook,
which holds calls that really happened. Both are requests Mycroft wanted to
make, so both belong in the corpus, with a flag saying which is which. A
prepared request tells you what a recipe intends to ask; it does not tell you
what anything cost.

Two sources are understood today, and adding a third is a function:

  llm-handoff artifacts   logs/<recipe>/runs/<run>/llm-handoff/*.json
  the gateway's logbook   logs/gateway/runs/*.jsonl

Prompt text is NOT stored by default. A record carries the prompt's length and
its SHA-256, which is enough to size a request, price it, and spot duplicates,
and it keeps other people's data out of a file I would otherwise be committing.
Pass --with-text when a replay genuinely needs the words.

Usage:
    python scripts/gateway/bench/corpus.py                 # collect and summarise
    python scripts/gateway/bench/corpus.py --check         # also flag what the gateway cannot serve
    python scripts/gateway/bench/corpus.py --with-text     # include prompt text
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gateway.policy import Policy
from gateway.prices import PriceTable, UnknownModelPrice
from gateway.tiers import TierConfig

REPO_ROOT = Path(__file__).resolve().parents[3]
CORPUS_DIR = Path(__file__).with_name("corpus")

HANDOFF_GLOB = "logs/*/runs/*/llm-handoff/*.json"
LOGBOOK_GLOB = "logs/gateway/runs/*.jsonl"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _modified_on(path: Path) -> str:
    """The file's date, labelled as such -- it is not when the run happened."""
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).date().isoformat()


def from_handoff(path: Path, root: Path, *, with_text: bool) -> dict[str, Any] | None:
    """One prepared request. Returns None if the file is not a handoff artifact."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict) or "llm_needed" not in data:
        return None

    payload = data.get("payload") or {}
    messages = payload.get("messages") or []
    prompt = "\n".join(m.get("content", "") for m in messages if isinstance(m, dict))
    relative = path.relative_to(root).as_posix()
    parts = relative.split("/")

    record = {
        "source": relative,
        "source_kind": "llm_handoff",
        "recipe": parts[1] if len(parts) > 2 else None,
        "run": parts[3] if len(parts) > 4 else None,
        "file_modified_on": _modified_on(path),
        # The artifact's own words. False means the request was built and never
        # sent, which is the state of everything in this repository today.
        "live_call_performed": bool(data.get("live_call_performed")),
        "action": data.get("action"),
        "model_named": data.get("model_named_by_original"),
        "endpoint_named": data.get("endpoint_named_by_original"),
        "max_tokens": payload.get("max_tokens"),
        "messages": len(messages),
        "prompt_chars": len(prompt),
        "prompt_sha256": _sha(prompt) if prompt else None,
        "complete": bool(prompt),
        "tokens_in": None,
        "tokens_out": None,
        "cost_usd": None,
    }
    if with_text:
        record["prompt"] = prompt
    return record


def from_logbook(path: Path, root: Path) -> Iterator[dict[str, Any]]:
    """Calls that actually happened: the gateway's own rows."""
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        yield {
            "source": path.relative_to(root).as_posix(),
            "source_kind": "gateway_logbook",
            "recipe": row.get("caller"),
            "run": path.stem,
            "file_modified_on": _modified_on(path),
            "live_call_performed": True,
            "action": row.get("task_type"),
            "model_named": f"{row.get('provider')}:{row.get('model')}",
            "endpoint_named": None,
            "max_tokens": None,
            "messages": None,
            "prompt_chars": None,
            "prompt_sha256": None,
            "complete": True,
            "tokens_in": row.get("tokens_in"),
            "tokens_out": row.get("tokens_out"),
            "cost_usd": row.get("cost_usd"),
        }


def collect(root: Path = REPO_ROOT, *, with_text: bool = False,
            include_logbook: bool = True) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(root.glob(HANDOFF_GLOB)):
        record = from_handoff(path, root, with_text=with_text)
        if record is not None:
            records.append(record)
    if include_logbook:
        for path in sorted(root.glob(LOGBOOK_GLOB)):
            records.extend(from_logbook(path, root))
    return records


def summarise(records: list[dict[str, Any]]) -> dict[str, Any]:
    prepared = [r for r in records if not r["live_call_performed"]]
    live = [r for r in records if r["live_call_performed"]]
    sizes = sorted(r["prompt_chars"] for r in prepared if r["prompt_chars"])

    def tally(key: str, rows: list[dict[str, Any]]) -> dict[str, int]:
        out: dict[str, int] = {}
        for row in rows:
            out[str(row.get(key))] = out.get(str(row.get(key)), 0) + 1
        return dict(sorted(out.items(), key=lambda kv: -kv[1]))

    return {
        "records": len(records),
        "prepared_never_sent": len(prepared),
        "live_calls": len(live),
        "incomplete_payloads": sum(1 for r in prepared if not r["complete"]),
        "by_recipe": tally("recipe", records),
        "models_named": tally("model_named", prepared),
        "max_tokens_requested": tally("max_tokens", prepared),
        "prompt_chars": ({"min": sizes[0], "median": sizes[len(sizes) // 2],
                          "max": sizes[-1]} if sizes else None),
        "live_cost_usd": round(sum(r["cost_usd"] or 0 for r in live), 6),
    }


def check(records: list[dict[str, Any]], policy: Policy,
          prices: PriceTable) -> list[dict[str, Any]]:
    """What the gateway could not serve as asked. Reports; decides nothing."""
    budget = max(policy.max_tokens(t) for t in policy.tier_order)
    problems = []
    for record in records:
        if record["live_call_performed"]:
            continue
        model = record.get("model_named")
        if model:
            try:
                prices.rates("groq", model)
            except UnknownModelPrice:
                problems.append({"source": record["source"], "problem": "unpriced_model",
                                 "detail": model})
        asked = record.get("max_tokens")
        if isinstance(asked, int) and asked > budget:
            problems.append({"source": record["source"], "problem": "over_budget",
                             "detail": f"asks {asked}, largest tier budget is {budget}"})
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collect Mycroft's model requests into one corpus.")
    parser.add_argument("--with-text", action="store_true",
                        help="include prompt text (off by default)")
    parser.add_argument("--check", action="store_true",
                        help="also flag requests the gateway could not serve as asked")
    parser.add_argument("--no-logbook", action="store_true",
                        help="skip the gateway's own calls")
    args = parser.parse_args()

    records = collect(with_text=args.with_text, include_logbook=not args.no_logbook)
    if not records:
        print("No model requests found. Looked in:")
        print(f"  {HANDOFF_GLOB}\n  {LOGBOOK_GLOB}")
        return 1

    stats = summarise(records)
    print(f"{stats['records']} request records")
    print(f"  prepared but never sent : {stats['prepared_never_sent']}"
          f"  ({stats['incomplete_payloads']} with empty payloads)")
    print(f"  live calls              : {stats['live_calls']}"
          f"  (${stats['live_cost_usd']:.5f})")

    print("\nby recipe or caller:")
    for name, count in stats["by_recipe"].items():
        print(f"  {name or '(unknown)':<34}{count:>5}")

    if stats["models_named"]:
        print("\nmodels the prepared requests name:")
        for name, count in stats["models_named"].items():
            print(f"  {name:<34}{count:>5}")
        print(f"\nmax_tokens asked for: {stats['max_tokens_requested']}")
        print(f"prompt size (chars): {stats['prompt_chars']}")

    if args.check:
        policy = Policy.load(TierConfig.load())
        problems = check(records, policy, PriceTable.load())
        print(f"\nREQUESTS THE GATEWAY COULD NOT SERVE AS ASKED: {len(problems)}")
        for problem in problems[:12]:
            print(f"  {problem['problem']:<16}{problem['detail']}")
        if len(problems) > 12:
            print(f"  ... and {len(problems) - 12} more")

    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    out = CORPUS_DIR / f"{date.today().isoformat()}-corpus.jsonl"
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records),
                   encoding="utf-8")
    print(f"\ncorpus  {out}")
    if not args.with_text:
        print("Prompt text was not stored. Re-run with --with-text if a replay needs it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())