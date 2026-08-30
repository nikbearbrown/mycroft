"""
WHAT THIS FILE DOES: Terminal stage of the Assistant pipeline. Takes whatever
Synthesis (or an earlier halt) produced and returns a status object
representing a draft handed to the advisor. This file, and everything it
imports, defines no send, finalize, submit, or client-facing dispatch
function of any kind.

CONFIRMED / CONSTRUCTED: CONSTRUCTED stub, grounded directly in case study
Section 4 Scenario A Step 4 — "Rachel decides how, or whether, to use the
Assistant's answer... Nothing in Morgan Stanley's disclosures suggests the
Assistant's output reaches the client directly or without Rachel's own
judgment applied first." This file's entire job is to stop here. Per the
locked terminal-state design decision (blueprint Section 5): the absence of
a send/finalize function is structural, not a guard that happens to block
one — no such function exists anywhere in this pipeline for a test to call
even by mistake.
"""

from .synthesis import SynthesisResult


def handoff_to_advisor(synthesis_result: SynthesisResult, match_found: bool) -> dict:
    if not match_found:
        return {"status": "no_match_found"}

    return {
        "status": "handed_off_to_advisor",
        "draft": synthesis_result.draft_answer,
        "sources": synthesis_result.sources_used,
    }
