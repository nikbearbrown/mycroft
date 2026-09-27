"""
WHAT THIS FILE DOES: gates whether a synthesized draft proceeds to finalization.
This is the deliberately-absent-default component in this pipeline — same
pattern as this series' Lemonade Authorization Gate and HSBC Human Review Gate.

CONFIRMED / CONSTRUCTED: deliberately absent by design, not a gap to fill.
DBS's own governance language (Nimish Panchmatia, quoted in Section 4's framing
note: AI capability innovation currently outpaces governance and control roughly
five to one, and "we need to close this gap before we allow autonomy") is direct,
on-the-record grounds for shipping this gate with zero built-in approval
criteria. No confidence score, no dollar threshold, no severity rule is invented
here, clearly labeled or otherwise — inventing any default would imply a shape
of answer DBS's own disclosure does not support.

This gate requires an externally supplied decision function. It will not run
without one, and it will not accept an unrecognized answer from one either.
"""

from typing import Callable


VALID_OUTCOMES = ("cleared_for_finalization", "not_cleared_for_finalization")  # [DEV]

# Naming note (Design Decision 1, Addendum v2): these two outcomes are named from
# Section 4's own language ("finalises the memo"), not from this series' usual
# `not_authorized` convention. This gate does not authorize a credit decision —
# DBS's own Section 4, Step 5 hands the memo to a separate, undisclosed
# credit-approval process after this point. What this gate decides is narrower:
# whether the draft is fit to proceed into that process at all.


class HumanReviewGate:
    """
    Wraps an externally supplied decision function. Contains no approval logic
    of its own — see module docstring for why.
    """

    def __init__(self, decision_function: Callable[[dict], str]):
        if decision_function is None or not callable(decision_function):
            raise TypeError(
                "HumanReviewGate requires a callable decision_function at "
                "construction. This gate ships with no default approval logic "
                "by design — see module docstring."
            )
        self._decision_function = decision_function

    def review(self, draft: dict) -> str:
        """
        Calls the supplied decision_function with the draft and strictly
        validates its return value.

        Raises ValueError if the returned value is not exactly one of
        VALID_OUTCOMES (Design Decision 7, Addendum v3). This is distinct from
        the __init__ TypeError above: that one is misuse of the gate's
        construction API (nothing supplied at all); this one is an unrecognized
        outcome from a supplied function that otherwise runs. Left unvalidated,
        an unrecognized value would silently fail open — proceeding to
        finalization by default rather than by any deliberate answer, which is
        the exact failure mode this gate exists to prevent.
        """
        result = self._decision_function(draft)

        if result not in VALID_OUTCOMES:
            raise ValueError(
                f"decision_function returned {result!r}, which is not one of "
                f"the gate's recognized outcomes: {VALID_OUTCOMES}. The gate "
                "will not guess at what an unrecognized value should mean."
            )

        return result
