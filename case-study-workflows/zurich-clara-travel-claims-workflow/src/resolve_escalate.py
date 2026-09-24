"""
WHAT THIS FILE DOES: Terminal stub. On resolution, marks the claim
resolved. On escalation, routes to a human reviewer with a specific named
reason attached -- never a generic "escalated" flag.

CONSTRUCTED stub. Does not model any real downstream Zurich/AgentricAI
process -- nothing is disclosed about what happens after Clara's stage.
Minimal by design, only so pipeline completion is observable in tests,
matching this series' established terminal-stub pattern (DBS, Lemonade).
"""


def resolve(claim_id, coverage_result):
    return {
        "status": "resolved",
        "claim_id": claim_id,
        "coverage_result": coverage_result,
    }


def escalate(claim_id, reason, detail=None):
    return {
        "status": "escalated",
        "claim_id": claim_id,
        "reason": reason,
        "detail": detail,
    }
