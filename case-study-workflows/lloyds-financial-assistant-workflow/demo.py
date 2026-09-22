"""
Runnable end-to-end demo.

The decision function below is a NAMED, LOGGED EXCEPTION to this
repository's own rule that every invented value carries a [DEV] marker.
A [DEV] marker signals a legitimate illustrative default worth tuning
toward a real value later. This policy has no relationship to any real
Lloyds authorization criteria at all -- it exists solely to make the
pipeline runnable end to end, the same treatment this series gave the
demo policies at Lemonade ("claims under $500 settle") and Zurich.

Do not read this function as a guess at what Lloyds' real boundary is.
"""

from lloyds_pipeline.mock_data import MOCK_TRANSACTIONS
from lloyds_pipeline.models import Query
from lloyds_pipeline.orchestrator import FinancialAssistantPipeline


def demo_policy(context: dict) -> bool:
    """Trivial, non-representative: answer directly whenever a record matched."""
    return context.get("matched_record") is not None


def run(label: str, query: Query) -> None:
    pipeline = FinancialAssistantPipeline(decision_fn=demo_policy, transactions=MOCK_TRANSACTIONS)
    result = pipeline.process(query)
    print(f"\n--- {label} ---")
    print(f"  status : {result.status}")
    print(f"  reason : {result.reason}")
    print(f"  detail : {result.detail}")


if __name__ == "__main__":
    # The Section 4 scenario: Fiona, a clean match.
    run("Fiona — clean transaction match",
        Query(raw_text="What was that £42.50 charge on 15 June?",
              claimed_amount=42.50, claimed_date="2026-06-15"))

    run("Unclassifiable query",
        Query(raw_text="Please update my postal address"))

    run("Coaching query (recognized, not modeled by this scaffold)",
        Query(raw_text="Can you help me build a monthly budget?"))

    run("Incomplete transaction details (no date given)",
        Query(raw_text="What was that charge for?", claimed_amount=42.50, claimed_date=None))

    run("No matching record",
        Query(raw_text="What was that payment?", claimed_amount=42.50, claimed_date="2020-01-01"))

    run("Record mismatch",
        Query(raw_text="What was that payment?", claimed_amount=1.00, claimed_date="2026-06-15"))
