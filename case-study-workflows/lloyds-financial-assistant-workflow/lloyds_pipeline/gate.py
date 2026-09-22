"""
Authorization Gate — Step 4 of the illustrated workflow (Section 4).

This is the repository's central design decision, following the same
pattern this series used for Lemonade's Authorization Gate and Zurich's
Authorization Gate for Clara.

Lloyds confirms a CATEGORY: the assistant can "refer to expert human
support when needed." It discloses no BOUNDARY: no confidence score, no
transaction-value threshold, no topic restriction defines "needed."

Consistent with that finding, this Gate ships with ZERO default
authorization criteria, under no [DEV] label, anywhere in this file. It
raises an error at construction if no external decision function is
supplied, and it strictly validates whatever that function returns.
Inventing a labeled placeholder here — e.g. "auto-answer if the record
matched and the amount is under some cutoff" — would have implied a shape
of answer ("it's probably a value threshold") that nothing in the public
record supports.
"""

from typing import Callable


class AuthorizationGate:
    """
    Requires a real, externally supplied decision function to do anything.

    The supplied function receives a dict describing the matched
    transaction context and must return a bool:
      - True  -> the assistant is authorized to answer Fiona directly
      - False -> the query is referred to human support

    This Gate has no opinion of its own about what should make that
    function return True. It only enforces the contract.
    """

    def __init__(self, decision_fn: Callable[[dict], bool]):
        if decision_fn is None or not callable(decision_fn):
            raise TypeError(
                "AuthorizationGate requires a callable decision_fn. "
                "No default authorization criteria are built into this "
                "Gate — Lloyds has not disclosed any, and this scaffold "
                "does not invent one. See README.md."
            )
        self._decision_fn = decision_fn

    def evaluate(self, context: dict) -> str:
        """
        Returns "answered_directly" or "escalated_to_human" (matching
        Lloyds' own "refer to expert human support" phrasing, rather than
        importing a "not_authorized" framing the confirmed record doesn't
        use — a deliberate naming choice, logged here rather than made
        silently).
        """
        result = self._decision_fn(context)
        if not isinstance(result, bool):
            raise ValueError(
                f"decision_fn must return a bool; got {type(result).__name__!r}. "
                "The Gate enforces this contract but does not, and cannot, "
                "know what SHOULD authorize a real query — that boundary "
                "is undisclosed by Lloyds."
            )
        return "answered_directly" if result else "escalated_to_human"
