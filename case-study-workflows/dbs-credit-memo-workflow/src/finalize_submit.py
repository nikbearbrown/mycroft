"""
WHAT THIS FILE DOES: represents the point where a human finalizes an
approved/cleared draft and hands it to DBS's existing credit-approval process.
This is a terminal stub — the pipeline's job ends here.

CONFIRMED / CONSTRUCTED: entirely CONSTRUCTED as a stub. Section 4, Step 5 of
the case study states this explicitly: DBS's relationship manager "submits it
through DBS's existing credit-approval process — a process this case study does
not describe in further detail, since DBS has not disclosed one specific to
agent-drafted memos." This module does not model that process, does not connect
to anything, and does not claim any downstream system exists in any particular
shape. It exists only to give the orchestrator's happy-path test an observable
terminal state to assert against (Design Decision 4, Addendum v1) — without a
return value here, a test cannot distinguish the pipeline completing from it
silently doing nothing.
"""

from typing import TypedDict


class FinalizeResult(TypedDict):
    status: str  # always "handoff_attempted" — see docstring below
    client_id: str
    memo_reference: str


def finalize(draft: dict) -> FinalizeResult:
    """
    [DEV] CONSTRUCTED stub. Does not submit anything anywhere. Returns a status
    object confirming a handoff was attempted and echoing the draft's
    identifying fields, so the pipeline's terminal state is observable and
    testable. This is not a claim about DBS's actual downstream process.
    """
    return FinalizeResult(
        status="handoff_attempted",
        client_id=draft["client_id"],
        memo_reference=f"MEMO-{draft['client_id']}",  # [DEV] synthetic, not a real ID scheme
    )
