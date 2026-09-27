"""
claims_agent.py — the real ClaimsAgent class, wiring together:
  - claims_parser.py (split_claims, flag_multi_dependency) — tested
    against 4 real patents, 64 claims, all correctly classified.
  - claim_classifier.py (classify_claim) — tested against 1 real
    independent claim so far. The result was genuinely good, but this
    is a much smaller sample than the parser's — treat classification
    results with correspondingly more caution until tested more broadly.
"""
from dataclasses import dataclass, field
from typing import List, Optional

from claims_parser import Claim, split_claims, flag_multi_dependency
from claim_classifier import ScopeClassification, classify_claim


@dataclass
class ClaimReading:
    claim: Claim
    possible_multi_dependency: bool
    scope: Optional[ScopeClassification] = None


@dataclass
class PatentClaimsReading:
    publication_number: str
    readings: List[ClaimReading] = field(default_factory=list)

    @property
    def independent_count(self) -> int:
        return sum(1 for r in self.readings if r.claim.is_independent)

    @property
    def dependent_count(self) -> int:
        return sum(1 for r in self.readings if not r.claim.is_independent)

    @property
    def flagged_multi_dependency(self) -> List[ClaimReading]:
        return [r for r in self.readings if r.possible_multi_dependency]


class ClaimsAgent:
    """
    Reads a patent's claims text and produces a structured reading:
    independent/dependent classification (tested, reliable), a
    protection-scope reading for each independent claim (lightly
    tested — read with appropriate caution), and an explicit flag on
    any claim whose dependency reference pattern needs manual review.
    """

    def __init__(self, anthropic_api_key: Optional[str] = None):
        self._api_key = anthropic_api_key

    def read_claims(self, publication_number: str, claims_text: str,
                     classify_independent: bool = True) -> PatentClaimsReading:
        """
        classify_independent: if True (default), calls the Claude API
        once per independent claim. Set to False for the fast,
        zero-cost structural reading only.
        """
        claims = split_claims(claims_text)
        result = PatentClaimsReading(publication_number=publication_number)

        for claim in claims:
            multi_dep = flag_multi_dependency(claim)
            reading = ClaimReading(claim=claim, possible_multi_dependency=multi_dep)

            if classify_independent and claim.is_independent:
                reading.scope = classify_claim(
                    claim_number=claim.number,
                    claim_text=claim.text,
                    api_key=self._api_key,
                )

            result.readings.append(reading)

        return result

    def summarize(self, reading: PatentClaimsReading) -> dict:
        return {
            "publication_number": reading.publication_number,
            "total_claims": len(reading.readings),
            "independent_count": reading.independent_count,
            "dependent_count": reading.dependent_count,
            "flagged_for_manual_review": [
                r.claim.number for r in reading.flagged_multi_dependency
            ],
            "scope_readings": [
                {
                    "claim": r.claim.number,
                    "breadth": r.scope.breadth,
                    "posture": r.scope.posture,
                    "confidence_caveat": r.scope.confidence_caveat,
                }
                for r in reading.readings if r.scope is not None
            ],
        }
