"""
Orchestrator — ties Intake -> Retrieval -> Authorization Gate together in
strict, fail-fast sequence.

Architecture note: this is a single, linear pipeline, not a multi-agent
system — matching what Lloyds' public record actually supports for this
tool (a single assistant with a small number of confirmed functions, not
a documented multi-component architecture; contrast Athena's confirmed
but separately-described RAG mechanism).

Scope note: this pipeline models the transaction-lookup path in full
depth. A query classified as "coaching" is a real, Lloyds-confirmed
function (Section 3.2) that this scaffold deliberately does NOT model
end-to-end — it is out of scope for this reference implementation, which
is built around Section 4's transaction-lookup scenario specifically.
This is a stated scope decision, not an omission: coaching queries are
still correctly classified and reported, just not carried through
Retrieval or the Gate.
"""

from typing import Callable, Dict, List

from .gate import AuthorizationGate
from .intake import classify_query
from .models import PipelineResult, Query, TransactionRecord
from .retrieval import retrieve_and_match


class FinancialAssistantPipeline:
    def __init__(
        self,
        decision_fn: Callable[[dict], bool],
        transactions: Dict[str, List[TransactionRecord]],
    ):
        # Constructing the Gate here means a pipeline built without a
        # valid decision function fails once, immediately, at
        # construction -- not partway through processing a query, after
        # Intake and Retrieval have already done real work.
        self._gate = AuthorizationGate(decision_fn)
        self._transactions = transactions

    def process(self, query: Query) -> PipelineResult:
        classification = classify_query(query)

        if classification.query_type == "malformed_input":
            return PipelineResult(
                status="escalated_to_human",
                reason="malformed_query_input",
                detail="The query's text or claimed amount was not in a "
                       "usable format (e.g. missing, wrong type, or not a "
                       "real number). Added after an adversarial testing "
                       "pass found this crashed the pipeline outright in "
                       "an earlier version -- see README.",
            )

        if classification.query_type == "malformed_date":
            return PipelineResult(
                status="escalated_to_human",
                reason="unparseable_date_format",
                detail="The claimed date was not in a recognizable "
                       "YYYY-MM-DD format, so it could not be safely "
                       "checked against a transaction record. Deliberately "
                       "distinct from no_matching_record: 'the format was "
                       "unreadable' is not the same claim as 'we checked "
                       "and there was truly nothing that day' -- an "
                       "earlier version of this pipeline conflated the "
                       "two and silently reported a false no_matching_record "
                       "for a transaction that actually existed. See README.",
            )

        if classification.query_type == "unclassifiable":
            return PipelineResult(
                status="escalated_to_human",
                reason="unclassified_query",
                detail="Could not confidently classify the query as either "
                       "a transaction question or a coaching question.",
            )

        if classification.query_type == "coaching":
            # Deliberately not carried further -- see module docstring.
            return PipelineResult(
                status="recognized_not_modeled",
                reason="coaching_out_of_scope",
                detail="Classified as a coaching query. Lloyds confirms this "
                       "function exists (Section 3.2), but it is out of "
                       "scope for this reference implementation.",
            )

        # query_type == "transaction_lookup"
        if classification.extracted_amount is None or classification.extracted_date is None:
            return PipelineResult(
                status="escalated_to_human",
                reason="incomplete_claim_details",
                detail="Recognized as a transaction question, but the "
                       "customer did not supply both an amount and a date "
                       "to look up.",
            )

        retrieval = retrieve_and_match(classification, self._transactions)

        if retrieval.status == "no_matching_record":
            return PipelineResult(
                status="escalated_to_human",
                reason="no_matching_record",
                detail="No transaction record exists for the claimed date.",
            )

        if retrieval.status == "record_mismatch":
            return PipelineResult(
                status="escalated_to_human",
                reason="record_mismatch",
                detail="A transaction record exists for that date, but its "
                       "amount does not match what the customer described.",
            )

        # retrieval.status == "matched" -- and only now is the Gate consulted.
        gate_context = {
            "query_type": classification.query_type,
            "matched_record": retrieval.record,
            "claimed_amount": classification.extracted_amount,
            "claimed_date": classification.extracted_date,
        }
        gate_outcome = self._gate.evaluate(gate_context)

        if gate_outcome == "answered_directly":
            return PipelineResult(
                status="answered_directly",
                record=retrieval.record,
                detail=f"{retrieval.record.merchant}: £{retrieval.record.amount:.2f} "
                       f"on {retrieval.record.date} ({retrieval.record.description}).",
            )

        return PipelineResult(
            status="escalated_to_human",
            reason="gate_declined",
            detail="The transaction record matched, but the authorization "
                   "decision referred this query to human support.",
        )
