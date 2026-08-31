"""
WHAT THIS FILE DOES: Checks whether client consent has been given before the
Debrief pipeline proceeds to transcription. This is the one genuine gate in
either pipeline in this repository — do not confuse it with the "no gate at
all" design decision governing the OUTPUT side of this pipeline
(post_meeting_draft.py / handoff_debrief.py). Consent is an INPUT
precondition Morgan Stanley states directly; it is not the undisclosed
authorization boundary this series' empty-gate pattern (Lemonade, HSBC) was
built to model, and it is not the unconditional-review property the rest of
this pipeline models either. It is its own, third thing: a client-granted
precondition, not a decision anyone at Morgan Stanley or in this code makes
or withholds.

CONFIRMED / CONSTRUCTED: The precondition itself is CONFIRMED — case study
Section 4 Scenario B Step 1: "With Mr. Alvarez's consent, Debrief records and
transcribes the meeting." The data representation of the consent flag here
([DEV]: a plain boolean) is CONSTRUCTED; Morgan Stanley discloses no consent
data model.

Naming note: this module uses `cleared` / not `cleared`, not
`authorized` / `not_authorized`. This is a deliberate departure from series
convention, logged in DESIGN_DECISIONS.md as distinct in reasoning from
HSBC's `not_approved` and DBS's `cleared_for_finalization` departures.
"""

from dataclasses import dataclass


@dataclass
class ConsentResult:
    cleared: bool = False


def check_consent(consent_flag: bool) -> ConsentResult:
    return ConsentResult(cleared=bool(consent_flag))
