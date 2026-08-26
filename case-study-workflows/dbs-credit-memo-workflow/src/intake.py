"""
WHAT THIS FILE DOES: validates that a memo request contains the minimum fields
needed before Draft Synthesis runs. This is the first stage in the pipeline;
nothing downstream is called if intake is incomplete.

CONFIRMED / CONSTRUCTED: the required field list (client_id, facility_type,
requested_action) is entirely CONSTRUCTED — DBS's own disclosure describes no
request schema, no intake interface, and no specific fields a relationship
manager would supply. Section 4, Step 1 of the case study states directly that
"DBS has not disclosed how a memo request is actually initiated." This module
assumes only that some triggering action with identifiable content exists,
since a memo has to start somewhere — it does not claim DBS's actual intake
mechanism looks like this.
"""

from typing import TypedDict


REQUIRED_FIELDS = ["client_id", "facility_type", "requested_action"]  # [DEV]


class IntakeResult(TypedDict):
    status: str  # "complete" or "incomplete"
    missing_fields: list[str]
    request: dict


def validate_intake(request: dict) -> IntakeResult:
    """
    Checks that all REQUIRED_FIELDS are present and non-empty in the request.

    Returns an IntakeResult status object rather than raising — an incomplete
    request is a normal, expected domain outcome (per Design Decision 2), not a
    programmer error, so callers should branch on `status`, not catch an
    exception.
    """
    missing = [
        field for field in REQUIRED_FIELDS
        if field not in request or request[field] in (None, "")
    ]

    if missing:
        return IntakeResult(
            status="incomplete",
            missing_fields=missing,
            request=request,
        )

    return IntakeResult(
        status="complete",
        missing_fields=[],
        request=request,
    )
