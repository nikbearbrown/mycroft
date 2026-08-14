"""
Claim verification — Week 7.

For each citation claim with a URL, fetches the source and checks whether
quantitative values from the same thought_log appear in it.

Supported source types:
  SEC EDGAR companyfacts JSON  (data.sec.gov/api/xbrl/*)
  Generic text / HTML          (regex number search)

verified=True   — source reachable, at least one claim number confirmed
verified=False  — source reachable, no claim number found in it
verified=None   — unattainable (connection error, non-200, parse error)

verification_rate = verified_citations / total_citations  (0.0 when no citations)

ADR: stdlib only. No third-party HTTP or HTML libraries.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Optional

from claims import ExtractedClaim

_NUMBER_RE = re.compile(
    r'(?:'
    r'\$[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|trillion|M|B|T))?'
    r'|[\d,]+(?:\.\d+)?\s*%'
    r'|[\d,]+(?:\.\d+)?x'
    r'|[\d,]+(?:\.\d+)?\s*bps'
    r')',
    re.IGNORECASE,
)

_SUFFIX_MAP: dict[str, float] = {
    "trillion": 1e12, "t": 1e12,
    "billion":  1e9,  "b": 1e9,
    "million":  1e6,  "m": 1e6,
}

_TIMEOUT_S = 10
_MAX_BYTES  = 300_000   # cap HTTP read at 300 KB


# ── Number normalisation ───────────────────────────────────────────────────────

def _normalize(s: str) -> float | None:
    """Parse a quantitative claim string to a plain float, or None on failure."""
    s = s.strip().replace(",", "").replace("$", "")
    lower = s.lower()
    for suffix, mult in _SUFFIX_MAP.items():
        if lower.endswith(suffix):
            try:
                return float(lower[: -len(suffix)].strip()) * mult
            except ValueError:
                return None
    s = re.sub(r"[%xbps]+$", "", s, flags=re.IGNORECASE).strip()
    try:
        return float(s)
    except ValueError:
        return None


def _close_enough(a: float, b: float, tol: float = 0.01) -> bool:
    """True if values agree within 1% relative tolerance."""
    if a == 0.0 and b == 0.0:
        return True
    denom = max(abs(a), abs(b))
    return denom > 0 and abs(a - b) / denom <= tol


# ── Fetching helpers ───────────────────────────────────────────────────────────

def _fetch(url: str) -> str | None:
    """Fetch URL, return text body or None on any error."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "accountability-layer/1.0 audit-research@project.local"},
        )
        with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
            return resp.read(_MAX_BYTES).decode("utf-8", errors="replace")
    except Exception:
        return None


def _is_edgar(url: str) -> bool:
    return "sec.gov" in url or "edgar" in url.lower()


def _numbers_from_edgar(text: str) -> set[float]:
    """Extract all numeric fact values from an SEC EDGAR companyfacts JSON."""
    out: set[float] = set()
    try:
        obj = json.loads(text)
    except Exception:
        return out
    for ns in obj.get("facts", {}).values():
        for concept in ns.values():
            for unit_vals in concept.get("units", {}).values():
                for entry in unit_vals:
                    v = entry.get("val")
                    if isinstance(v, (int, float)):
                        out.add(float(v))
    return out


def _numbers_from_text(text: str) -> set[float]:
    """Extract normalised numbers from arbitrary text."""
    out: set[float] = set()
    for m in _NUMBER_RE.finditer(text):
        n = _normalize(m.group(0))
        if n is not None:
            out.add(n)
    return out


# ── Core check ─────────────────────────────────────────────────────────────────

def _check_url(url: str, claim_numbers: set[float]) -> bool | None:
    if not claim_numbers:
        return None

    text = _fetch(url)
    if not text or not text.strip():
        return None

    source_numbers = (
        _numbers_from_edgar(text)
        if _is_edgar(url) and text.strip().startswith("{")
        else _numbers_from_text(text)
    )

    if not source_numbers:
        return None

    for cn in claim_numbers:
        for sn in source_numbers:
            if _close_enough(cn, sn):
                return True

    return False


# ── Public API ─────────────────────────────────────────────────────────────────

def verify_claims(claims: list[ExtractedClaim]) -> tuple[list[ExtractedClaim], float]:
    """
    For each citation claim with a URL, fetch the source and check whether
    quantitative values from the thought_log appear in it.

    Returns (updated_claims, verification_rate).
    verification_rate = verified_citations / total_citations  (0.0 if no citations)
    """
    quant_numbers: set[float] = set()
    for c in claims:
        if c.claim_type == "quantitative":
            n = _normalize(c.text)
            if n is not None:
                quant_numbers.add(n)

    citations = [
        c for c in claims
        if c.claim_type == "citation"
        and c.source_url
        and c.source_url not in ("N/A", "")
    ]

    if not citations:
        return claims, 0.0

    # Fetch each distinct URL once
    url_results: dict[str, bool | None] = {}
    for c in citations:
        url = c.source_url
        if url not in url_results:
            url_results[url] = _check_url(url, quant_numbers)

    verified_count = sum(1 for v in url_results.values() if v is True)

    updated: list[ExtractedClaim] = []
    for c in claims:
        if c.claim_type == "citation" and c.source_url in url_results:
            updated.append(ExtractedClaim(
                claim_type=c.claim_type,
                text=c.text,
                context=c.context,
                source_label=c.source_label,
                source_url=c.source_url,
                verified=url_results[c.source_url],
            ))
        else:
            updated.append(c)

    rate = round(verified_count / len(citations), 3)
    return updated, rate
