#!/usr/bin/env python3
"""
Test script: verify LangFuse integration end-to-end.

This runs a real EDGAR fetch + mock LLM through the financial grader,
generating a full trace (tool call + LLM call spans) that should appear
in the LangFuse dashboard at http://localhost:3000.

Usage:
  python test_langfuse_integration.py

Then check http://localhost:3000 → Traces → find one named "analyze_ticker".
"""

import os
import sys
import uuid
import time

from adapters.mock_adapter import make_mock_adapter
from financial_grader import analyze_ticker, lookup_cik
from schemas import AgentID, ParseStatus

def main():
    print("LangFuse Integration Test")
    print("=" * 60)

    # Check environment
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
    host = os.environ.get("LANGFUSE_HOST", "http://localhost:3000")

    if not public_key or not secret_key:
        print("\n⚠️  LANGFUSE_PUBLIC_KEY and/or LANGFUSE_SECRET_KEY not set.")
        print("   Tracing will be disabled (SDK logs a warning but continues).\n")
        print("   To set them:")
        print("   1. Start LangFuse: cd .langfuse && docker-compose up -d")
        print("   2. Visit http://localhost:3000 and log in")
        print("   3. Copy API keys from Settings → Projects → API Keys")
        print("   4. Add to .env:")
        print("      LANGFUSE_PUBLIC_KEY=pk_...")
        print("      LANGFUSE_SECRET_KEY=sk_...")
        print("   5. Re-run this script\n")
        will_trace = False
    else:
        print(f"✓ LangFuse configured:")
        print(f"  Host: {host}")
        print(f"  Public Key: {public_key[:20]}...")
        will_trace = True

    print("\n" + "=" * 60)
    print("Running financial grader (AAPL)...")
    print("=" * 60 + "\n")

    try:
        cik = lookup_cik("AAPL")
        print(f"✓ Resolved AAPL → CIK {cik}")

        run_id = uuid.uuid4()
        print(f"✓ Run ID: {run_id}")

        result = analyze_ticker(
            "AAPL",
            cik,
            make_mock_adapter("none"),
            run_id=run_id,
        )

        obj = result.reasoning_objects[0]
        print(f"✓ Analysis complete:")
        print(f"    Agent: {obj.agent_id.value}")
        print(f"    Status: {obj.parse_status.value}")
        print(f"    Confidence: {obj.confidence_score}")

        # Show a snippet of the conclusion
        if obj.conclusion:
            snippet = obj.conclusion[:100].replace("\n", " ")
            print(f"    Conclusion: {snippet}...")

        print("\n" + "=" * 60)
        if will_trace:
            print("✓ Trace should appear in LangFuse dashboard in a few seconds.")
            print(f"  Go to: http://localhost:3000")
            print(f"  Look for a trace named 'analyze_ticker'")
            print(f"  It should show nested spans for:")
            print(f"    - fetch_company_facts (tool call)")
            print(f"    - llm_call:AAPL (generation — the LLM call)")
            print("\n  Spans capture:")
            print(f"    • Latency (how long each took)")
            print(f"    • Inputs & outputs (what data flowed)")
            print(f"    • Errors (if any step failed)")
            print(f"    • Trace relationships (parent/child)")
        else:
            print("ℹ  Tracing is disabled (no credentials configured).")
            print("   The analysis still works, but no traces are sent to LangFuse.")

        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
