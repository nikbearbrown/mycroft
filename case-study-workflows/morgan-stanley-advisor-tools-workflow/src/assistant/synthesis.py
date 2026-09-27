"""
WHAT THIS FILE DOES: Produces a draft answer from already-retrieved documents.
Pure function — does not touch the corpus and does not call retrieval.py
itself, per this series' standing convention (established at DBS) that
synthesis-stage modules receive their input rather than fetch it.

CONFIRMED / CONSTRUCTED: Synthesis as a capability is CONFIRMED (case study
Section 3.1 — the Assistant "retrieves and synthesizes answers"). The
internal synthesis mechanism here ([DEV]: naive concatenation/templating of
matched snippets) is CONSTRUCTED and makes no claim to approximate GPT-4-level
synthesis quality. Whether or how the real Assistant flags source documents,
confidence, or recency to the advisor is undisclosed; this module returns the
source document IDs used, but invents no confidence or citation-display
mechanism beyond that plain list.
"""

from dataclasses import dataclass, field


@dataclass
class SynthesisResult:
    draft_answer: str = ""
    sources_used: list[str] = field(default_factory=list)


def synthesize(matches: list[dict]) -> SynthesisResult:
    """[DEV] Naive synthesis: concatenates matched snippets into a single
    draft answer, in corpus order, with no ranking or weighting logic beyond
    what retrieval.py already decided was a match."""
    if not matches:
        return SynthesisResult(draft_answer="", sources_used=[])

    draft_answer = " ".join(doc["snippet"] for doc in matches)
    sources_used = [doc["doc_id"] for doc in matches]

    return SynthesisResult(draft_answer=draft_answer, sources_used=sources_used)
