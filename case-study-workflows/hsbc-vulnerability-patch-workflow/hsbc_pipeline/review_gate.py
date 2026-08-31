"""
This is this reference implementation's central design decision, and it
deliberately follows the same pattern this series used for Lemonade's
Authorization Gate.

CONFIRMED: HSBC has stated a general, bank-wide governance principle — that
AI deployments are reviewed, monitored, and audited to preserve human
accountability (case study Section 3.2).

NOT DISCLOSED: HSBC has not described a code-specific approval gate, a
sign-off threshold, a severity cutoff, or any specific review criteria for
coding-assistant-drafted changes.

Per the case study's own finding (Sections 3.2 and 6.1), this Gate ships
with ZERO default review criteria — no severity threshold, no confidence
score, no auto-approval path — under any [DEV] marker, anywhere in this
module. It requires a real, externally supplied decision function to do
anything at all. Inventing a labeled placeholder here (e.g., "auto-approve
low-severity fixes") would have implied a shape of answer — that HSBC's
review process is severity-based, or threshold-based, or confidence-based —
that nothing in the public record supports.
"""

from .models import ReviewDecision


class HumanReviewGate:
    def __init__(self, decision_fn):
        if decision_fn is None:
            raise ValueError(
                "HumanReviewGate requires an externally supplied decision_fn; "
                "this repository ships no default review policy, per the case "
                "study's finding that HSBC discloses no code-specific approval "
                "gate (Section 3.2)."
            )
        self._decision_fn = decision_fn

    def review(self, draft_patch, report):
        approved = self._decision_fn(draft_patch, report)
        if approved:
            return ReviewDecision(approved=True)
        return ReviewDecision(approved=False, reason="not_approved")
