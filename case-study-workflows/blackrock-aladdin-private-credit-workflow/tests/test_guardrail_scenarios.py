"""
Runnable, key-free demonstration of the guardrail's three real behaviors,
using fake LLM providers instead of live API calls — no API keys needed.
This is also the actual dry-run scenarios from this repo's design docs,
executed for real rather than traced by hand.

Run directly: python3 tests/test_guardrail_scenarios.py
"""
import asyncio
import json
import sys
sys.path.insert(0, ".")

from src.llm_providers import LLMProvider
from src.orchestrator import QueryOrchestrator
from src.registry_filter import ToolRegistryFilter
from src.adapters import PrivateCreditAdapter, PortfolioHoldingsAdapter
from src.benchmark_calculator import BenchmarkCalculator
from src.synthesizer import ResponseSynthesizer
from src.guardrail import GuardrailChecker
from src.pipeline import PrivateCreditQueryPipeline


class FakeIntentLLM(LLMProvider):
    """Returns canned JSON for orchestrator parsing, skips synthesis calls."""
    def __init__(self, intent_json, synth_responses):
        self.intent_json = intent_json
        self.synth_responses = list(synth_responses)  # queue: first call, second call (regen), ...

    def complete(self, prompt, system="", max_tokens=1024):
        if "extract" in system.lower() or "borrower_or_entity" in system:
            return json.dumps(self.intent_json)
        return self.synth_responses.pop(0)


async def run_case(label, intent_json, synth_responses, expect_passed, expect_escalated):
    print(f"\n=== {label} ===")
    llm = FakeIntentLLM(intent_json, synth_responses)
    calc = BenchmarkCalculator()
    pipeline = PrivateCreditQueryPipeline(
        llm=llm,
        orchestrator=QueryOrchestrator(llm),
        registry_filter=ToolRegistryFilter(),
        adapters={
            "private_credit": PrivateCreditAdapter(),
            "portfolio_holdings": PortfolioHoldingsAdapter(),
        },
        calc=calc,
        synthesizer=ResponseSynthesizer(),
        guardrail=GuardrailChecker(),
        audit_log=None,
    )
    result = await pipeline.run(intent_json["raw_query_placeholder"])
    print("passed:", result.passed, "| escalated:", result.escalated)
    print("unverified_figures:", result.unverified_figures)
    print("final draft:\n", result.verified_draft)

    assert result.passed == expect_passed, f"Expected passed={expect_passed}, got {result.passed}"
    assert result.escalated == expect_escalated, f"Expected escalated={expect_escalated}, got {result.escalated}"
    print(f"✓ assertions held for: {label}")


async def main():
    # Case A: clean draft, correctly rounded figures, no hallucination.
    # Tests the tolerance rule handles legitimate rounding, and that a
    # threshold constant mentioned for context (e.g. "the 6.0x reference
    # threshold") isn't wrongly flagged as an invented figure.
    await run_case(
        "Case A: clean asset, correctly rounded draft",
        {
            "borrower_or_entity": "Example Industrial Holdings",
            "requested_metrics": ["position_size", "leverage_ratio"],
            "fund_scope": None,
            "raw_query_placeholder": "What's our exposure to Example Industrial Holdings, and is leverage elevated?",
        },
        synth_responses=[
            "Example Industrial Holdings shows a leverage ratio of 2.95x, which is not "
            "elevated relative to the 6.0x reference threshold. Our position has a market "
            "value of $18.3M, representing 3.2% of the portfolio."
        ],
        expect_passed=True,
        expect_escalated=False,
    )

    # Case B: first draft hallucinates a DSCR figure (0.9x instead of the
    # actual 1.14x). Tests that the guardrail catches it, regenerates once,
    # and the second draft is correct — including a figure ("down 17.4%")
    # whose sign is conveyed in words, not a literal minus sign.
    await run_case(
        "Case B: distressed asset, first draft hallucinates DSCR, regeneration fixes it",
        {
            "borrower_or_entity": "Riverside Distribution Partners",
            "requested_metrics": ["valuation_trend", "debt_service_coverage", "position_size"],
            "fund_scope": None,
            "raw_query_placeholder": "How is our position in Riverside Distribution Partners performing, and are there any coverage concerns?",
        },
        synth_responses=[
            # First draft: hallucinated DSCR (0.9x is not a real computed value)
            "Riverside Distribution Partners shows leverage of 7.5x (elevated), valuation "
            "down 17.4% over the prior period, and a debt service coverage ratio of 0.9x, "
            "indicating a coverage concern. Our position has a market value of $5.9M.",
            # Second draft (after regeneration prompt): corrected DSCR
            "Riverside Distribution Partners shows leverage of 7.5x (elevated), valuation "
            "down 17.4% over the prior period, and a debt service coverage ratio of 1.14x, "
            "indicating a coverage concern. Our position has a market value of $5.9M.",
        ],
        expect_passed=True,
        expect_escalated=False,
    )

    # Case C: distressed asset, hallucination persists even after regeneration.
    # Tests guaranteed visible escalation — never a silent bad number.
    await run_case(
        "Case C: distressed asset, hallucination persists after regeneration — must escalate",
        {
            "borrower_or_entity": "Riverside Distribution Partners",
            "requested_metrics": ["debt_service_coverage"],
            "fund_scope": None,
            "raw_query_placeholder": "Are there coverage concerns for Riverside Distribution Partners?",
        },
        synth_responses=[
            "Riverside Distribution Partners has a debt service coverage ratio of 0.9x.",
            "Riverside Distribution Partners has a debt service coverage ratio of 0.85x.",  # still wrong
        ],
        expect_passed=False,
        expect_escalated=True,
    )

    print("\nAll scenarios behaved as expected.")


asyncio.run(main())
