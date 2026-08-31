"""
claims_parser.py — splits raw patent claims text (as pulled from
patents-public-data.patents.publications.claims_localized) into
individual claims, and classifies each as independent or dependent.

Built against real claims text (US-11791319-B2), not a guessed format.
"""
import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Claim:
    number: int
    text: str
    is_independent: bool
    references: Optional[int]  # first claim number this depends on, if dependent
    all_references: List[int]  # every claim number found in a dependency reference


# Claims are numbered at the start of a line/segment, e.g. "1. A semiconductor..."
# followed eventually by the next number. This pattern looks for a number,
# a period, then captures everything up to the next such number (or end of text).
CLAIM_SPLIT_PATTERN = re.compile(
    r"(?:^|\n)\s*(\d+)\.\s+(.*?)(?=(?:\n\s*\d+\.\s+)|\Z)",
    re.DOTALL,
)

# A dependent claim typically references another claim by number, e.g.
# "The substrate of claim 1, wherein..." — this catches "claim N" or "claims N".
# findall (not search) so every reference is captured, not just the first.
DEPENDENCY_PATTERN = re.compile(r"claim[s]?\s+(\d+)", re.IGNORECASE)

# A genuine multi-dependency reference names more than one claim number
# directly adjacent to the word "claim(s)" — e.g. "claim 1 or 2",
# "claims 1-3", "claims 1 and 2". This is intentionally narrow: it does
# NOT flag every "or" in the claim body (that was the earlier bug — see
# README "Known limitation"). It only looks inside a short window right
# after the word "claim(s)".
MULTI_DEPENDENCY_PATTERN = re.compile(
    r"claim[s]?\s+\d+\s*(?:,|or|and|-|to)\s*\d+",
    re.IGNORECASE,
)


def split_claims(raw_claims_text: str) -> List[Claim]:
    """
    Split raw claims text into a list of Claim objects.

    NOTE: this regex-based split is a first pass, not a guaranteed-correct
    parser. Real claims text has known irregularities (OCR artifacts in
    older filings, unusual formatting) that this does not yet handle.
    Every result should be spot-checked against the raw text before
    trusting it for classification downstream.
    """
    if not raw_claims_text or not raw_claims_text.strip():
        return []

    matches = CLAIM_SPLIT_PATTERN.findall(raw_claims_text)
    claims = []

    for number_str, body in matches:
        number = int(number_str)
        body = body.strip()

        all_refs = [int(n) for n in DEPENDENCY_PATTERN.findall(body)]
        is_independent = len(all_refs) == 0
        first_reference = all_refs[0] if all_refs else None

        claims.append(Claim(
            number=number,
            text=body,
            is_independent=is_independent,
            references=first_reference,
            all_references=all_refs,
        ))

    return claims


def flag_multi_dependency(claim: Claim) -> bool:
    """
    Returns True only if the claim text contains a genuine multi-claim
    reference pattern (e.g. "claim 1 or 2", "claims 1-3") — not just any
    "or" appearing somewhere in the claim body. This replaces the earlier,
    over-eager heuristic that produced a confirmed false positive.
    """
    if claim.is_independent:
        return False
    return bool(MULTI_DEPENDENCY_PATTERN.search(claim.text))


def summarize(claims: List[Claim]) -> dict:
    """Quick summary stats — useful for a first sanity check on real data."""
    independent = [c for c in claims if c.is_independent]
    dependent = [c for c in claims if not c.is_independent]
    return {
        "total_claims": len(claims),
        "independent_count": len(independent),
        "dependent_count": len(dependent),
        "independent_numbers": [c.number for c in independent],
    }


if __name__ == "__main__":
    # Quick manual test using placeholder text based on the real shape we
    # saw from BigQuery. Replace with the actual full claims_text pulled
    # from a real patent before trusting this against production data.
    sample = """1. A semiconductor system, comprising:
at least first and second integrated circuit packages, each of the packages
comprising a substrate assembly having generally planar top and bottom sides
and an edge surface, wherein the edge surface extends between the top and
bottom sides.
2. The semiconductor system of claim 1, wherein the substrate assembly
further comprises a conductive layer.
3. The semiconductor system of claim 2, wherein the conductive layer is
copper.
"""
    result = split_claims(sample)
    for c in result:
        print(f"Claim {c.number} — {'INDEPENDENT' if c.is_independent else f'DEPENDENT on {c.references}'}")
        print(f"  {c.text[:80]}...")
    print()
    print(summarize(result))
