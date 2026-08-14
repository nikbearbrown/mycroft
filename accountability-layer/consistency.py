"""
Consistency probing — ADR-06 partial mitigation.

Runs the same query a second time through the full validation loop and
compares the two conclusions.

Why this helps:
  A model that genuinely reasoned from evidence should produce conclusions
  that converge across runs. A model that confabulated a plausible-sounding
  conclusion will drift — especially on specific quantitative claims.

What it doesn't prove:
  Two identical confabulations are still confabulations. High consistency
  is weak positive evidence, not proof of genuine reasoning. Low consistency
  is strong negative evidence — it flags unreliable output without requiring
  external ground truth.

Score derivation:
  Number overlap  (weight 0.6) — do the same quantitative values appear?
                                  Numbers are objectively verifiable and
                                  the hardest to confabulate consistently.
  Word overlap    (weight 0.4) — Jaccard similarity on content words,
                                  stopwords removed.

  Combined score → agreement classification:
    ≥ 0.70  HIGH    — materially consistent
    ≥ 0.40  MEDIUM  — partial agreement, some divergence
    < 0.40  LOW     — material inconsistency, flag for review
    UNKNOWN — probe run failed structurally (halted or error)

The probe run is NOT persisted to the DB.  It is metadata on the primary run.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import Callable, Literal

from schemas import AgentID, DataSource

ConsistencyAgreement = Literal["HIGH", "MEDIUM", "LOW", "UNKNOWN"]

_STOPWORDS: frozenset[str] = frozenset({
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "this", "that", "these",
    "those", "it", "its", "not", "no", "nor", "also", "which", "who",
})

_NUMBER_RE = re.compile(
    r'(?:'
    r'\$[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|trillion|M|B|T))?'
    r'|[\d,]+(?:\.\d+)?\s*%'
    r'|[\d,]+(?:\.\d+)?x'
    r'|[\d,]+(?:\.\d+)?\s*bps'
    r')',
    re.IGNORECASE,
)


# ── Data class ─────────────────────────────────────────────────────────────────

@dataclass
class ConsistencyResult:
    score:                  float                  # 0.0 – 1.0
    agreement:              ConsistencyAgreement
    probe_conclusion:       str | None             # second run's conclusion
    primary_numbers:        list[str]
    probe_numbers:          list[str]
    divergent_numbers:      list[str]              # present in one but not both
    word_overlap:           float
    number_overlap:         float
    probe_halted:           bool       = False
    probe_error:            str | None = None
    number_divergence_flag: bool       = False     # hard flag: any number appears in one run only

    def to_dict(self) -> dict:
        return {
            "score":                  self.score,
            "agreement":              self.agreement,
            "probe_conclusion":       self.probe_conclusion,
            "primary_numbers":        self.primary_numbers,
            "probe_numbers":          self.probe_numbers,
            "divergent_numbers":      self.divergent_numbers,
            "word_overlap":           self.word_overlap,
            "number_overlap":         self.number_overlap,
            "probe_halted":           self.probe_halted,
            "probe_error":            self.probe_error,
            "number_divergence_flag": self.number_divergence_flag,
        }


# ── Scoring helpers ────────────────────────────────────────────────────────────

def _content_words(text: str) -> set[str]:
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    return {w for w in words if w not in _STOPWORDS}


def _extract_numbers(text: str) -> list[str]:
    return [m.group(0).strip().lower() for m in _NUMBER_RE.finditer(text)]


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def _compute_score(primary: str, probe: str) -> tuple[float, float, float]:
    """Returns (combined, word_overlap, number_overlap)."""
    word_overlap = _jaccard(_content_words(primary), _content_words(probe))

    p_nums = set(_extract_numbers(primary))
    q_nums = set(_extract_numbers(probe))
    # If neither conclusion contains numbers, don't penalise
    number_overlap = _jaccard(p_nums, q_nums) if (p_nums or q_nums) else 1.0

    combined = round((word_overlap * 0.4) + (number_overlap * 0.6), 3)
    return combined, round(word_overlap, 3), round(number_overlap, 3)


def _classify(score: float) -> ConsistencyAgreement:
    if score >= 0.70:
        return "HIGH"
    if score >= 0.40:
        return "MEDIUM"
    return "LOW"


def _unknown(reason: str, halted: bool = True) -> ConsistencyResult:
    return ConsistencyResult(
        score=0.0, agreement="UNKNOWN",
        probe_conclusion=None,
        primary_numbers=[], probe_numbers=[], divergent_numbers=[],
        word_overlap=0.0, number_overlap=0.0,
        probe_halted=halted, probe_error=reason,
    )


# ── Public API ─────────────────────────────────────────────────────────────────

def run_consistency_probe(
    subject:            str,
    context:            str,
    agent_id:           AgentID,
    confidence_score:   float,
    data_sources:       tuple[DataSource, ...],
    call_agent_fn:      Callable,
    primary_conclusion: str,
) -> ConsistencyResult:
    """
    Run a second validation pass on the same inputs and compare conclusions.

    The probe's run_id is a fresh UUID — the probe is never written to the DB.
    Uses the same adapter (model, temperature) as the primary run so the
    comparison is fair.
    """
    from middleware import HaltError, run_validation_loop

    try:
        result = run_validation_loop(
            subject,
            context,
            uuid.uuid4(),
            agent_id,
            confidence_score=confidence_score,
            data_sources=data_sources,
            call_agent_fn=call_agent_fn,
        )
    except HaltError as exc:
        return _unknown(f"Probe halted: {exc}")
    except Exception as exc:
        return _unknown(f"{type(exc).__name__}: {exc}")

    if not result.final_response:
        return _unknown("Probe produced no final response")

    probe_conclusion = result.final_response.conclusion
    combined, word_overlap, number_overlap = _compute_score(
        primary_conclusion, probe_conclusion
    )

    p_nums = _extract_numbers(primary_conclusion)
    q_nums = _extract_numbers(probe_conclusion)
    p_set  = set(p_nums)
    q_set  = set(q_nums)
    divergent = sorted((p_set | q_set) - (p_set & q_set))

    return ConsistencyResult(
        score=combined,
        agreement=_classify(combined),
        probe_conclusion=probe_conclusion,
        primary_numbers=p_nums,
        probe_numbers=q_nums,
        divergent_numbers=divergent,
        word_overlap=word_overlap,
        number_overlap=number_overlap,
        number_divergence_flag=len(divergent) > 0,
    )
