"""
WHAT THIS FILE DOES: Gates a claim between Coverage Check and Resolve/
Escalate. Contains zero built-in approval criteria -- no dollar threshold,
no confidence cutoff, no claim-type restriction, under any label anywhere
in this file. Requires an externally supplied decision function at
construction or raises immediately. Strictly validates that function's
return value.

This is the third non-negotiable structural guarantee locked at /v1.
Directly grounded in Zurich's own confirmed language -- "keeping humans
in control where it matters most" states a category (some claims are
within Clara's resolution authority, some are not) without disclosing a
boundary. Inventing one, even labeled [DEV], would imply a shape of
answer ("probably severity-based," "probably a dollar amount") that
nothing in the public record supports.

Return-value naming (`resolved_by_human` / `escalated_to_human`) is this
build's own logged departure from the series' `not_authorized` default
and from DBS's `cleared_for_finalization` framing -- grounded in Zurich's
"keeping humans in control" phrase, which frames this as a control-locus
question rather than an authorization or finalization question.
"""

VALID_DECISIONS = {"resolved_by_human", "escalated_to_human"}


class AuthorizationGate:
    def __init__(self, decision_fn):
        if decision_fn is None:
            raise TypeError("AuthorizationGate requires an external decision_fn; none was supplied")
        self._decision_fn = decision_fn

    def decide(self, coverage_result):
        decision = self._decision_fn(coverage_result)
        if decision not in VALID_DECISIONS:
            raise ValueError(
                f"decision_fn returned {decision!r}; must be one of {VALID_DECISIONS}"
            )
        return decision


# ---------------------------------------------------------------------------
# Demo-only example policy. Explicitly NOT [DEV]-marked: this is not a
# labeled illustrative placeholder for a real threshold, it is a named,
# logged exception that exists solely so the pipeline is runnable
# end-to-end. It carries no claim to represent Clara's actual authority
# boundary, exactly as the Lemonade Gate's demo policy was handled.
# ---------------------------------------------------------------------------

def demo_decision_fn(coverage_result):
    """
    NAMED EXCEPTION, not [DEV]: auto-resolves only if the flight
    cancellation is covered and the tour reimbursement (if present) is
    covered or simply absent. Everything else escalates. This function
    makes no claim whatsoever about how Clara actually decides.
    """
    flight_covered = coverage_result.get("flight_cancellation_covered")
    tour_covered = coverage_result.get("tour_covered")

    if flight_covered and tour_covered in (True, None):
        return "resolved_by_human"
    return "escalated_to_human"
