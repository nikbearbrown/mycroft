"""Make exactly ONE real call, then stop. Sprint 2's human gate.

Refuses to run unless the price table has been filled in, so the first live
call cannot happen before it can be honestly priced.

Runs the gate's own checks on the result: recomputes the cost from the price
table and compares it to what was logged, flags an empty response, and flags
truncation (tokens_out == max_tokens).

Catches ProviderError deliberately, so the error-path test shows a clean
classification instead of a traceback.

Usage:
    $env:GROQ_API_KEY="gsk_..."                  # PowerShell
    python scripts/gateway/first_live_call.py

    # error-path test -- expect a clean provider_error row, not a crash
    $env:GROQ_API_KEY="gsk_deliberately_invalid"
    python scripts/gateway/first_live_call.py
"""

from __future__ import annotations

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
from gateway.tiers import TierConfig

LOG_PATH = Path("logs/gateway/first-live-call.jsonl")
PROMPT = "Reply with exactly one word: ok"

# 16 was too small: gpt-oss models spend output budget on reasoning tokens
# before emitting visible content, so the first run returned empty text with
# tokens_out == max_tokens. 256 leaves room for reasoning plus an answer.
MAX_TOKENS = 256

TIER = "cheap"


def main() -> int:
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
    spec = tiers.spec(TIER)
    provider, model = spec["provider"], spec["model"]

    print("About to make ONE real call.")
    print(f"  tier        {TIER}")
    print(f"  provider    {provider}")
    print(f"  model       {model}")
    print(f"  prices      {prices.version}")
    print(f"  tiers       {tiers.version}")
    print(f"  max_tokens  {MAX_TOKENS}")
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
                             tier=TIER, prompt=PROMPT, max_tokens=MAX_TOKENS)
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
    if resp.tokens_out >= MAX_TOKENS:
        problems.append(
            f"tokens_out ({resp.tokens_out}) hit max_tokens ({MAX_TOKENS}) "
            f"-- response was truncated"
        )
    else:
        print(f"  tokens    {resp.tokens_out} out, under the {MAX_TOKENS} cap -- not truncated")

    # 4. latency sanity
    print(f"  latency   {result.record['latency_ms']}ms")

    print("\n--- request totals ---")
    print(json.dumps(request_totals(read_records(LOG_PATH)), indent=2))

    if problems:
        print("\nPROBLEMS FOUND -- do not clear the gate until these are understood:")
        for problem in problems:
            print(f"  - {problem}")
    else:
        print("\nAll automatic checks passed.")

    print(f"\nOne call made. Row appended to {LOG_PATH}")
    print("Still to verify by hand: Groq console usage shows this request.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())