"""
Guardrail / Hallucination Check.

Input: draft synthesized output before it's returned to the user.
Output: pass, or a flag requiring the draft to be regenerated or escalated.

Sequencing note: this reference implementation runs Synthesis BEFORE
Guardrail, despite §2's component table and §1's Phase 3 description
listing them in the opposite order. §3.5's own contract — "regenerate the
draft" — only makes sense if a draft already exists; you can't regenerate
something never generated once. This is a named, deliberate deviation from
how the source doc's table and prose describe the order — see the README's
"Deviations from the Source Reference" section for the full reasoning.

Deterministic — no LLM call. §2 marks this component "Module" (not
"Module (LLM-backed)"), unlike the Orchestrator and Synthesis module. This
checker extracts numeric figures from the draft and confirms each traces
back to an actual computed value — from BenchmarkResult or the raw portfolio
data — within a tolerance. It does not ask a model to grade its own work.

§3.5's [DEV] marker offered two choices on failure: silently regenerate-and-
log, or surface a visible warning. This implementation does both, in
sequence — one silent regeneration attempt, and if that doesn't clear
verification, a GUARANTEED visible escalation. No second silent attempt, no
quiet failure. This satisfies §3.5's own stated failure mode to avoid: an
unflagged, unverified number reaching a portfolio manager.

Tolerance: figures are compared using a 2% relative difference after
normalizing formatting ($, x, %, M-suffixes). This number was decided
during a dry-run trace, not guessed — without an explicit tolerance,
correctly-rounded figures (draft says "7.5x", computed value is 7.4998...)
fail an exact-match check on essentially every draft, which would make this
guardrail trigger constantly on cosmetic rounding rather than real problems.

Honest, disclosed limitation, not a silent one: this is a regex-based
heuristic, not a full semantic parser. It can be fooled by phrasing it
wasn't built to expect — a number spelled out in words, or a figure
described without a numeral. Four-digit numbers in a plausible calendar-year
range are excluded from verification, since vintage years and dates aren't
computed figures and would otherwise generate constant false positives.
"""
import re
import logging
from .models import GuardrailResult

logger = logging.getLogger(__name__)

NUMBER_PATTERN = re.compile(r'[-+]?\$?\d[\d,]*\.?\d*\s*(%|x|mm|million|M\b)?', re.IGNORECASE)
TOLERANCE = 0.02  # 2% relative difference, decided during dry-run trace #2


class GuardrailChecker:
    def screen(self, draft: str, benchmark_results: list, portfolio_data: list,
               synthesizer, llm, intent, thresholds: dict = None) -> GuardrailResult:
        reference_values = self._build_reference_values(benchmark_results, portfolio_data, thresholds)
        unverified = self._find_unverified_figures(draft, reference_values)

        if not unverified:
            return GuardrailResult(True, draft, [], False)

        # One silent regeneration attempt — cheap, often fixes a one-off
        # phrasing or rounding issue.
        regenerated = synthesizer.draft(
            intent, benchmark_results, portfolio_data, llm, avoid_unverified=unverified
        )
        still_unverified = self._find_unverified_figures(regenerated, reference_values)

        if not still_unverified:
            logger.info(
                f"Guardrail: regeneration cleared verification (originally flagged: {unverified})"
            )
            return GuardrailResult(True, regenerated, [], False)

        # Guaranteed visible escalation — no second silent attempt.
        logger.warning(
            f"Guardrail: escalating — still unverified after regeneration: {still_unverified}"
        )
        flagged = self._append_visible_warning(regenerated, still_unverified)
        return GuardrailResult(False, flagged, still_unverified, True)

    def _build_reference_values(self, benchmark_results: list, portfolio_data: list,
                                  thresholds: dict = None) -> list:
        # Threshold constants are legitimate numbers a synthesized draft might
        # cite for comparison context ("...relative to the 6.0x reference
        # threshold") — they're grounded in the code, not hallucinated, even
        # though they aren't a computed result for this specific asset.
        # Found via end-to-end execution testing, not caught on paper.
        values = [r.value for r in benchmark_results]
        if thresholds:
            values.extend(thresholds.values())
        for record in portfolio_data:
            for key in ("position_size", "market_value", "allocation_pct"):
                if key in record:
                    values.append(record[key])
        return values

    def _find_unverified_figures(self, draft: str, reference_values: list) -> list:
        unverified = []
        for match in NUMBER_PATTERN.finditer(draft):
            raw_token = match.group(0).strip()
            if not raw_token or not any(c.isdigit() for c in raw_token):
                continue
            if self._looks_like_a_year(raw_token):
                continue
            candidates = self._normalize(raw_token)
            if not self._matches_any_reference(candidates, reference_values):
                unverified.append(raw_token)
        return unverified

    def _looks_like_a_year(self, token: str) -> bool:
        digits = re.sub(r'\D', '', token)
        return len(digits) == 4 and 1900 <= int(digits) <= 2100 and "." not in token and "%" not in token

    def _normalize(self, token: str) -> list:
        """A written figure can plausibly mean more than one underlying value
        depending on its unit ('17.4%' means 0.174 as a fraction; '7.5x' means
        7.5 as a bare ratio). Returns every plausible interpretation so the
        matcher checks all of them instead of guessing which one applies."""
        cleaned = token.replace("$", "").replace(",", "").strip()
        suffix = ""
        for s in ("%", "x", "mm", "million", "M"):
            if cleaned.lower().endswith(s.lower()) and len(cleaned) > len(s):
                suffix = s.lower()
                cleaned = cleaned[: -len(s)].strip()
                break
        try:
            base = float(cleaned)
        except ValueError:
            return []

        candidates = [base]
        if suffix == "%":
            candidates.append(base / 100)
        elif suffix in ("mm", "million", "m"):
            candidates.append(base * 1_000_000)
        return candidates

    def _matches_any_reference(self, candidates: list, reference_values: list) -> bool:
        if not candidates:
            return True  # not a real number token — don't flag non-figures
        for c in candidates:
            for ref in reference_values:
                if ref == 0:
                    continue
                # Compare magnitude, not signed value. Natural language often
                # conveys direction in words ("valuation down 17.4%") rather
                # than a literal minus sign on the figure — found via
                # end-to-end execution testing, where a correct figure was
                # wrongly flagged purely because the draft didn't repeat the
                # sign already implied by the word "down".
                if abs(abs(c) - abs(ref)) / abs(ref) < TOLERANCE:
                    return True
        return False

    def _append_visible_warning(self, draft: str, unverified: list) -> str:
        warning = (
            f"\n\n[VERIFICATION WARNING: the following figures could not be confirmed "
            f"against retrieved data and may be inaccurate: {', '.join(unverified)}. "
            f"Please verify independently before relying on them.]"
        )
        return draft + warning
