"""Make exactly ONE real call, then stop. Sprint 2's human gate.

Refuses to run unless the price table has been filled in, so the first live
call cannot happen before it can be honestly priced.

Runs the gate's own checks on the result:
  - recomputes the cost from the price table and compares it to the log
  - flags an empty response
  - flags truncation (tokens_out == max_tokens)
  - flags reasoning that leaked into the answer text
  - checks the answer is actually "ok" -- the prompt asks for exactly that
Exits non-zero if any check fails, so the exit status never says "pass"
when the output lists problems.

The answer check exists because the others were not enough: on 2026-09-10
the strong tier returned its whole <think> reasoning block plus "ok", and
every earlier check passed. The response was well-formed and wrong.

Catches ProviderError deliberately, so the error-path test shows a clean
classification instead of a traceback.

Usage:
    $env:GROQ_API_KEY="gsk_..."                          # PowerShell

    python scripts/gateway/first_live_call.py            # cheap tier
    python scripts/gateway/first_live_call.py mid
    python scripts/gateway/first_live_call.py strong
    python scripts/gateway/first_live_call.py strong --max-tokens 1024

    # error-path test -- expect a clean provider_error row, not a crash
    $env:GROQ_API_KEY="gsk_deliberately_invalid"
    python scripts/gateway/first_live_call.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gateway.adapters.base import ProviderError
from gateway.adapters.groq import GroqAdapter
from gateway.client import GatewayClient
from gateway.logbook import Logbook
from gateway.prices import PriceTable
from gateway.report import read_records, request_totals
from gateway.tiers import TierConfig, UnknownTierName

LOG_PATH = Path("logs/gateway/first-live-call.jsonl")
PROMPT = "Reply with exactly one word: ok"
EXPECTED_ANSWER = "ok"

# 16 was too small: gpt-oss models spend output budget on reasoning tokens
# before emitting visible content, so the first run returned empty text with
# tokens_out == max_tokens. 256 leaves room for reasoning plus an answer.
# Override with --max-tokens if a tier reasons for longer.
DEFAULT_MAX_TOKENS = 256


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Make one gated live call.")
    parser.add_argument("tier", nargs="?", default="cheap",
                        help="tier name from tiers.json (default: cheap)")
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS,
                        help=f"output token budget (default: {DEFAULT_MAX_TOKENS})")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tier_name = args.tier
    max_tokens = args.max_tokens

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("GROQ_API_KEY is not set. Nothing was called.")
        return 1

    prices = PriceTable.load()
    if prices.version == "UNSET":
        print("prices.json still has version 'UNSET'. Fill in real rates with a")
        print("source URL and the date read, then bump the version. Nothing was called.")
        return 1

    tiers = TierConfig.load()
    try:
        spec = tiers.spec(tier_name)
    except UnknownTierName:
        print(f"Unknown tier {tier_name!r}. Known tiers: {', '.join(tiers.names)}.")
        print("Nothing was called.")
        return 1
    provider, model = spec["provider"], spec["model"]

    print("About to make ONE real call.")
    print(f"  tier        {tier_name}")
    print(f"  provider    {provider}")
    print(f"  model       {model}")
    print(f"  prices      {prices.version}")
    print(f"  tiers       {tiers.version}")
    print(f"  max_tokens  {max_tokens}")
    print(f"  prompt      {PROMPT!r}")
    if input("\nType 'yes' to proceed: ").strip().lower() != "yes":
        print("Cancelled. Nothing was called.")
        return 1

    client = GatewayClient(
        logbook=Logbook(LOG_PATH, prices),
        adapters={"groq": GroqAdapter(api_key=api_key)},
        tiers=tiers.as_client_map(),
        policy_version="0.0.0-sprint2-gate",
    )

    try:
        result = client.call(task_type="gate_check", caller="first_live_call.py",
                             tier=tier_name, prompt=PROMPT, max_tokens=max_tokens)
    except ProviderError as exc:
        # This is the error-path test succeeding, not the script failing.
        print("\n--- provider failed, classified cleanly ---")
        print(f"  kind     {exc.kind}")
        print(f"  provider {exc.provider}")
        print(f"  model    {exc.model}")
        print(f"  message  {exc}")

        rows = read_records(LOG_PATH)
        print(f"\nRow written: {rows[-1]['outcome']!r} with "
              f"{rows[-1]['latency_ms']}ms and cost {rows[-1]['cost_usd']}")
        print("\nERROR PATH OK -- the failure was classified and logged, not crashed.")
        return 0

    # ---- the gate's own checks -----------------------------------------

    resp = result.response
    text = resp.text.strip()

    print("\n--- response ---")
    print(repr(text) if text else "(EMPTY)")

    print("\n--- logbook row ---")
    print(json.dumps(result.record, indent=2, sort_keys=True))

    print("\n--- checks ---")
    problems: list[str] = []

    # 1. cost arithmetic, recomputed independently of what was logged
    rate_in, rate_out = prices.rates(provider, model)
    expected = (resp.tokens_in / 1000.0) * rate_in + (resp.tokens_out / 1000.0) * rate_out
    logged = result.record["cost_usd"]
    print(f"  cost      {resp.tokens_in}/1000 x {rate_in} + "
          f"{resp.tokens_out}/1000 x {rate_out} = {expected:.10f}")
    print(f"            logged: {logged:.10f}")
    if abs(expected - logged) > 1e-12:
        problems.append(f"cost mismatch: computed {expected}, logged {logged}")
    else:
        print("            MATCHES")

    # 2. empty response -- provider succeeded, answer is unusable
    if not text:
        problems.append("response text is EMPTY despite outcome 'ok'")

    # 3. truncation -- a deterministic, free quality signal
    if resp.tokens_out >= max_tokens:
        problems.append(
            f"tokens_out ({resp.tokens_out}) hit max_tokens ({max_tokens}) "
            f"-- response was truncated"
        )
    else:
        print(f"  tokens    {resp.tokens_out} out, under the {max_tokens} cap -- not truncated")

    # 4. reasoning leak -- the adapter should have stripped it. This should
    # never fire; it is here in case the adapter regresses.
    if "<think" in text.lower():
        problems.append("reasoning trace leaked into the response text")

    # 5. the answer itself. The prompt asks for exactly one word, "ok", so
    # anything else is wrong -- however well-formed. A deterministic
    # validator in miniature, and the check that catches a leaked <think>.
    normalized = text.lower().strip(" .!\"'")
    if text and normalized != EXPECTED_ANSWER:
        shown = text if len(text) <= 80 else text[:77] + "..."
        problems.append(f"answer {shown!r} is not the expected {EXPECTED_ANSWER!r}")
    elif text:
        print(f"  answer    {text!r} -- matches expected")

    # 6. latency sanity
    print(f"  latency   {result.record['latency_ms']}ms")

    print("\n--- request totals ---")
    print(json.dumps(request_totals(read_records(LOG_PATH)), indent=2))

    print(f"\nOne call made. Row appended to {LOG_PATH}")

    if problems:
        print("\nPROBLEMS FOUND -- do not clear the gate until these are understood:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print("\nAll automatic checks passed.")
    print("Still to verify by hand: Groq console usage shows this request.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())