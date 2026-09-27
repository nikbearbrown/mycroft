"""
WHAT THIS FILE DOES: stands in for the "70+ tasks" DBS describes its specialised
agents performing to synthesise a review-ready first draft of a credit memo.
Also contains the data-gap-detection check that determines whether synthesis
can proceed to a complete draft or must flag a gap instead.

CONFIRMED / CONSTRUCTED: the capacity itself — agents synthesising raw data into
a review-ready draft — is CONFIRMED, sourced to DBS's 19 August 2026 newsroom
release. Everything about *how* that happens here is CONSTRUCTED. DBS discloses
no breakdown of what the 70+ tasks individually are, so this module deliberately
does not decompose into named sub-functions — it is one function, treated as a
single confirmed capability, not a simulated multi-agent pipeline. Attempting to
model 70 discrete steps would invent a task list DBS has never published.

The data-gap check (folded in here per Design Decision 3, Addendum v1) exists
only because DBS describes the output as "review-ready," which implies some
completeness check precedes review — DBS never states this mechanism exists,
so it is CONSTRUCTED and marked [DEV].

Per Design Decision 6 (Addendum v3), this function is pure: it receives an
already-fetched client_record as an argument and performs no data lookups of
its own. mock_data.py is called by orchestrator.py, not by this module.
"""

from typing import TypedDict, Optional


# [DEV] CONSTRUCTED. The fields this deterministic stand-in checks for before
# considering a draft complete. DBS discloses no such completeness criteria —
# this list exists only to give the gap-flagging path something concrete to
# check, consistent with mock_data.py's deliberately incomplete CLIENT-003.
REQUIRED_SYNTHESIS_FIELDS = [
    "client_name",
    "existing_facility_type",
    "existing_facility_limit",
    "requested_facility_limit",
    "credit_rating",
]


class DraftResult(TypedDict):
    status: str  # "complete" or "gap_flagged"
    draft: Optional[dict]
    gap_reason: Optional[str]


def synthesize_draft(client_record: dict) -> DraftResult:
    """
    Synthesises a first-draft credit memo from an already-fetched client_record.

    If any REQUIRED_SYNTHESIS_FIELDS value is missing or None in client_record,
    returns a gap_flagged result rather than silently producing an incomplete
    draft — this is the [DEV] completeness check the module docstring describes.

    This function does not model DBS's actual 70+ tasks, does not call any
    external system, and does not fetch its own data — see module docstring.
    """
    missing = [
        field for field in REQUIRED_SYNTHESIS_FIELDS
        if field not in client_record or client_record[field] is None
    ]

    if missing:
        return DraftResult(
            status="gap_flagged",
            draft=None,
            gap_reason=(
                f"Required field(s) unresolved for synthesis: {', '.join(missing)}"
            ),
        )

    # [DEV] CONSTRUCTED. A deterministic, illustrative draft object — not a
    # claim about the structure of DBS's actual credit memos, which are not
    # publicly disclosed. This exists only to give downstream stages (human
    # review, finalize/submit) something concrete to operate on.
    draft = {
        "client_id": client_record["client_id"],
        "client_name": client_record["client_name"],
        "facility_type": client_record["existing_facility_type"],
        "current_limit": client_record["existing_facility_limit"],
        "requested_limit": client_record["requested_facility_limit"],
        "credit_rating": client_record["credit_rating"],
        "memo_summary": (
            f"Draft memo for {client_record['client_name']}: request to expand "
            f"{client_record['existing_facility_type']} facility from "
            f"{client_record['existing_facility_limit']} to "
            f"{client_record['requested_facility_limit']}. "
            f"Current credit rating: {client_record['credit_rating']}."
        ),
    }

    return DraftResult(status="complete", draft=draft, gap_reason=None)
