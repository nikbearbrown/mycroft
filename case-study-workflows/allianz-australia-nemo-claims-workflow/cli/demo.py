"""
cli/demo.py

Command-line demo runner. Lets you pick a provider and a stub scenario,
run the pipeline, see the Audit summary, and (for scenarios that reach
human review) simulate a claims professional's decision through the
token-gated payout path.

Usage:
    python -m cli.demo --provider claude --scenario happy_path
    python -m cli.demo --provider openai --scenario uncovered_claim
    python -m cli.demo --provider gemini --scenario no_weather_match

Requires the API key for whichever --provider you choose to be set in
your environment (see .env.example). Provider verification status: see
README.md — these adapters are design-complete but have not been
runtime-tested against a live API in this build.
"""

import argparse
import sys

from config import WorkflowConfig, ConfigError
from providers import get_provider
from workflow.orchestrator import NemoOrchestrator, WorkflowHaltedError
from workflow.payout_gate import HumanReviewSystem, PayoutExecutionAPI
from data.stub_scenarios import ALL_SCENARIOS


def main():
    parser = argparse.ArgumentParser(description="Project Nemo reference workflow demo")
    parser.add_argument("--provider", choices=["claude", "openai", "gemini"], default=None,
                         help="Overrides NEMO_PROVIDER from environment/config, if given.")
    parser.add_argument("--scenario", choices=list(ALL_SCENARIOS.keys()), default="happy_path")
    parser.add_argument("--auto-approve", action="store_true",
                         help="Skip the interactive human-review prompt and auto-approve, for scripted demos.")
    args = parser.parse_args()

    try:
        config = WorkflowConfig.from_env()
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.provider:
        config.provider_name = args.provider

    try:
        provider = get_provider(config)
    except ConfigError as e:
        print(f"Provider error: {e}", file=sys.stderr)
        sys.exit(1)

    scenario = ALL_SCENARIOS[args.scenario]
    print(f"--- Running scenario: {scenario.name} (provider: {config.provider_name}) ---")
    print(f"Expected outcome (per this scenario's fixture): {scenario.expected_outcome}\n")

    orchestrator = NemoOrchestrator(provider, threshold_aud=config.threshold_aud)

    try:
        result = orchestrator.run(
            scenario.raw_claim_event,
            scenario.policy_record,
            scenario.meteorological_data,
            scenario.claim_history_summary,
        )
    except WorkflowHaltedError as e:
        print(f"WORKFLOW HALTED at '{e.stage}': {e.reason}")
        return

    print("=== AUDIT SUMMARY (for human review) ===")
    print(result.audit_summary)
    print(f"\nRecommended settlement (AUD): {result.recommended_amount_aud}")

    # --- Human checkpoint ---
    if args.auto_approve:
        approved = True
        print("\n[--auto-approve set] Auto-approving for demo purposes.")
    else:
        answer = input("\nApprove this payout? [y/N]: ").strip().lower()
        approved = answer == "y"

    review_system = HumanReviewSystem()
    token = review_system.submit_decision(result.claim_id, approved, reviewer_id="demo-reviewer")

    if not approved:
        print("Claim declined by human reviewer. No payout executed.")
        return

    payout_api = PayoutExecutionAPI()
    confirmation = payout_api.execute_payout(result.claim_id, result.recommended_amount_aud, token)
    print(f"Payout executed: {confirmation}")


if __name__ == "__main__":
    main()
