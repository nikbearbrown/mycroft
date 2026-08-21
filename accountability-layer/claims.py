"""
Claim extraction — ADR-06 partial mitigation.

Parses a thought_log string into structured ExtractedClaim objects so the
thought_log can be treated as a set of verifiable assertions rather than
a narrative to be trusted.

Claim types:
  citation     — [SOURCE: label, url] blocks required by the directive
  quantitative — sentences containing numbers, percentages, dollar amounts
  hedge        — sentences containing explicit uncertainty language
  causal       — sentences containing causal connectors

These are stored per run and form the foundation for the next mitigation
layer: citation URL verification (fetch source, check the claim appears).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Optional

ClaimType = Literal["citation", "quantitative", "hedge", "causal"]

# ── Patterns ───────────────────────────────────────────────────────────────────

_CITATION_RE = re.compile(
    r'\[SOURCE:\s*(?P<label>[^\],]+),\s*(?P<url>[^\]]+)\]',
    re.IGNORECASE,
)

_QUANTITATIVE_RE = re.compile(
    r'(?:'
    r'\$[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|trillion|M|B|T))?'
    r'|[\d,]+(?:\.\d+)?\s*%'
    r'|[\d,]+(?:\.\d+)?x'           # multiples e.g. 2.3x
    r'|[\d,]+(?:\.\d+)?\s*bps'      # basis points
    r')',
    re.IGNORECASE,
)

_HEDGE_WORDS: frozenset[str] = frozenset({
    "estimated", "estimate", "approximately", "approximate", "roughly",
    "unclear", "uncertain", "uncertainty", "assumed", "assumption",
    "may", "might", "could", "possibly", "potentially", "likely",
    "unlikely", "limited data", "incomplete", "unavailable", "unknown",
    "speculative", "preliminary", "unverified", "pending", "subject to",
})

_CAUSAL_PHRASES: tuple[str, ...] = (
    "because", "therefore", "as a result", "due to", "consequently",
    "this led to", "which caused", "resulting in", "driven by",
    "attributed to", "stemming from", "on account of",
)


# ── Data class ─────────────────────────────────────────────────────────────────

@dataclass
class ExtractedClaim:
    claim_type:   ClaimType
    text:         str            # the specific claim or value
    context:      str            # surrounding sentence for readability
    source_label: str | None  = None
    source_url:   str | None  = None
    verified:     bool | None = None   # True=confirmed, False=not found, None=unattainable/unchecked

    def to_dict(self) -> dict:
        d: dict = {
            "claim_type": self.claim_type,
            "text":       self.text,
            "context":    self.context,
            "verified":   self.verified,
        }
        if self.source_label is not None:
            d["source_label"] = self.source_label
        if self.source_url is not None:
            d["source_url"] = self.source_url
        return d


# ── Helpers ────────────────────────────────────────────────────────────────────

def _sentences(text: str) -> list[str]:
    """Split on sentence-ending punctuation followed by whitespace."""
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]


# ── Public API ─────────────────────────────────────────────────────────────────

def extract_claims(thought_log: str | None) -> list[ExtractedClaim]:
    """
    Parse a thought_log string into structured ExtractedClaim objects.
    Always safe to call — returns [] if thought_log is None or empty.
    """
    if not thought_log:
        return []

    claims: list[ExtractedClaim] = []
    seen: set[tuple] = set()

    # ── Citations ──────────────────────────────────────────────────────────
    for m in _CITATION_RE.finditer(thought_log):
        label = m.group("label").strip()
        url   = m.group("url").strip()
        key   = ("citation", label.lower())
        if key in seen:
            continue
        seen.add(key)
        start   = max(0, m.start() - 100)
        context = thought_log[start : m.end() + 40].strip()
        claims.append(ExtractedClaim(
            claim_type="citation",
            text=f"{label} — {url}",
            context=context,
            source_label=label,
            source_url=url,
        ))

    # ── Sentence-level analysis ────────────────────────────────────────────
    for sentence in _sentences(thought_log):
        lower = sentence.lower()

        # Quantitative
        for m in _QUANTITATIVE_RE.finditer(sentence):
            key = ("quantitative", m.group(0).lower())
            if key in seen:
                continue
            seen.add(key)
            claims.append(ExtractedClaim(
                claim_type="quantitative",
                text=m.group(0).strip(),
                context=sentence,
            ))

        # Hedges
        found_hedges = [w for w in _HEDGE_WORDS if w in lower]
        if found_hedges:
            key = ("hedge", sentence[:80].lower())
            if key not in seen:
                seen.add(key)
                claims.append(ExtractedClaim(
                    claim_type="hedge",
                    text=", ".join(sorted(found_hedges)),
                    context=sentence,
                ))

        # Causal
        found_causal = [p for p in _CAUSAL_PHRASES if p in lower]
        if found_causal:
            key = ("causal", sentence[:80].lower())
            if key not in seen:
                seen.add(key)
                claims.append(ExtractedClaim(
                    claim_type="causal",
                    text=found_causal[0],
                    context=sentence,
                ))

    return claims
