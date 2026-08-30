"""
WHAT THIS FILE DOES: Runs the Assistant pipeline end to end in strict
sequence: Query Intake -> Retrieval -> [halt on no-match] -> Synthesis ->
Handoff. The only module in this pipeline with knowledge of the full
sequence.

CONFIRMED / CONSTRUCTED: Sequencing mirrors the case study's disclosed shape
(question in -> retrieval and synthesis -> advisor review) without adding any
step the case study does not support. Query Intake's validation logic is
CONSTRUCTED (Section 3.2 of the blueprint: no case-study basis for any
intake mechanism) and exists only to give the pipeline a defined entry
condition.

Halt map (three states, per Design Review Finding 5):
  1. Intake incomplete (empty/missing query)   -> halts before Retrieval
  2. Retrieval finds no match                  -> halts before Synthesis
  3. Clean run                                 -> reaches Handoff

This module defines no send, finalize, or submit function, and imports none.
"""

from .mock_corpus import get_corpus
from .retrieval import retrieve
from .synthesis import synthesize
from .handoff_assistant import handoff_to_advisor


def run_assistant_pipeline(query: str) -> dict:
    # Halt 1: intake
    if not query or not query.strip():
        return {"status": "intake_incomplete"}

    corpus = get_corpus()
    retrieval_result = retrieve(query, corpus)

    # Halt 2: no match
    if not retrieval_result.match_found:
        return handoff_to_advisor(synthesis_result=None, match_found=False)

    synthesis_result = synthesize(retrieval_result.matches)

    # Clean run
    return handoff_to_advisor(synthesis_result=synthesis_result, match_found=True)
