"""
CLI demo runner — no code editing required. Provider and API key come from
environment variables (see .env.example), never from editing this file.

Usage:
    python3 run_demo.py "What's our exposure to Example Industrial Holdings, and is leverage elevated?"
    python3 run_demo.py "Are there coverage concerns for Riverside Distribution Partners?"
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

from src.llm_providers import build_provider
from src.pipeline import build_default_pipeline


async def main():
    load_dotenv()

    if len(sys.argv) < 2:
        print('Usage: python3 run_demo.py "your question here"')
        sys.exit(1)
    query = sys.argv[1]

    provider_name = os.environ.get("PROVIDER", "claude")
    key_env_var = {
        "claude": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
    }.get(provider_name)
    api_key = os.environ.get(key_env_var, "")
    if not api_key:
        print(f"Set {key_env_var} in your .env file (see .env.example) — "
              f"or set PROVIDER to a provider you do have a key for.")
        sys.exit(1)

    llm = build_provider(provider_name, api_key)
    pipeline = build_default_pipeline(llm)

    result = await pipeline.run(query)

    print("\n--- Result ---")
    print(f"Verified: {result.passed}" + (" (escalated after regeneration)" if result.escalated else ""))
    print()
    print(result.verified_draft)


if __name__ == "__main__":
    asyncio.run(main())
