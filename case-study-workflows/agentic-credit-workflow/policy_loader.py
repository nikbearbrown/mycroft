"""
policy_loader.py
================
Agentic Credit Memo Pipeline — Credit Policy Loader

Loads credit_policy.json and exposes typed accessors used by:
  - orchestrator.py  (ratio thresholds injected into agent prompts)
  - approval_routing.py  (approval tier thresholds)
  - data_sources.py  (KYC review cycle lengths)

Why this exists:
  Credit policy thresholds must be readable by agents at runtime without
  hardcoding values into prompts. The Quantitative Agent compares calculated
  ratios against thresholds from this loader — not from a static string.
  When your risk team changes a threshold, they update credit_policy.json.
  No code changes required.

[DEV] TAXONOMY_PATH env var lets you point to a different policy file per
environment (e.g. a stricter policy in production, a relaxed one in staging).
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any


# [DEV] Change this path if you keep the policy file outside the repo root,
# or set POLICY_PATH in your environment to override it entirely.
DEFAULT_POLICY_PATH = Path(__file__).parent / "credit_policy.json"


@lru_cache(maxsize=1)
def get_loader() -> "PolicyLoader":
    path = Path(os.environ.get("POLICY_PATH", str(DEFAULT_POLICY_PATH)))
    return PolicyLoader(path)


class PolicyLoader:

    def __init__(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(
                f"Credit policy file not found at '{path}'. "
                "Set the POLICY_PATH environment variable to the correct location."
            )
        with open(path) as f:
            self._policy: dict[str, Any] = json.load(f)

    def get_ratio_thresholds(self, industry: str) -> dict[str, float]:
        """
        Returns ratio thresholds for a given industry code.
        Falls back to 'OTHER' if the industry is not in the policy file.

        [DEV] Add new industry codes to credit_policy.json under
        'ratio_thresholds'. The key must match the IndustryCode literal
        in schemas.py exactly.
        """
        thresholds = self._policy.get("ratio_thresholds", {})
        return thresholds.get(industry, thresholds.get("OTHER", {}))

    def get_approval_tiers(self) -> dict[str, Any]:
        """
        Returns the full approval tier configuration.
        Used by approval_routing.py to determine which approval workflow
        a completed memo is routed to.

        [DEV] Edit 'approval_tiers' in credit_policy.json to match your
        institution's credit authority limits. These amounts and risk tier
        assignments are reference defaults only.
        """
        return self._policy.get("approval_tiers", {})

    def get_kyc_review_cycle_months(self, risk_tier: str) -> int:
        """
        Returns how many months a KYC review remains current for a given
        risk tier. The KYC Agent uses this to flag stale reviews.

        [DEV] Adjust review cycle lengths in credit_policy.json under
        'kyc_policy.review_cycle_months'. Confirm with your compliance team.
        """
        cycles = self._policy.get("kyc_policy", {}).get("review_cycle_months", {})
        return cycles.get(risk_tier, 18)

    def is_osint_severity_blocking(self, severity: str) -> bool:
        """
        Returns True if the given OSINT severity level is credit-blocking
        (triggers immediate escalation before the Quantitative Agent runs).

        [DEV] Edit 'osint_policy.blocking_severities' in credit_policy.json.
        """
        blocking = self._policy.get("osint_policy", {}).get("blocking_severities", ["HIGH"])
        return severity in blocking

    def get_covenant_headroom(self, covenant_type: str) -> float:
        """
        Returns the headroom percentage for covenant structuring.
        The Reasoning/Report Agent uses this to propose covenant levels
        above the policy minimum.

        [DEV] Edit 'covenant_guidelines' in credit_policy.json to match
        your institution's structuring standards.
        """
        guidelines = self._policy.get("covenant_guidelines", {})
        key = f"{covenant_type}_covenant_headroom_pct"
        return guidelines.get(key, 0.10)

    def get_macro_overlay(self, industry: str) -> str:
        """
        Returns the current macroeconomic overlay text for the given industry.
        Falls back to the global overlay if no industry-specific entry is set.
        Returns an empty string if neither is set (overlay disabled).

        [DEV] Update 'macro_overlay' in credit_policy.json when your credit
        committee issues a sector view or macro caution. This is a manually
        set signal — not a live data feed. Set a value to null to disable
        the overlay for that industry without removing the key.
        """
        overlay = self._policy.get("macro_overlay", {})
        industry_text = overlay.get(industry)
        global_text = overlay.get("global", "")
        if industry_text:
            return f"{global_text}\nIndustry-specific: {industry_text}" if global_text else industry_text
        return global_text or ""

    def get_policy_summary_for_agent(self, industry: str) -> str:
        """
        Produces a plain-text policy summary injected into agent prompts.
        Agents reference policy thresholds from this string — not from
        hardcoded values in their system prompts.
        """
        thresholds = self.get_ratio_thresholds(industry)
        return (
            f"CREDIT POLICY THRESHOLDS for industry: {industry}\n"
            f"  Leverage Ratio (Total Debt / EBITDA): max {thresholds.get('leverage_ratio_max', 'N/A')}x\n"
            f"  Interest Coverage (EBITDA / Interest Expense): min {thresholds.get('interest_coverage_min', 'N/A')}x\n"
            f"  DSCR (Net Operating Income / Total Debt Service): min {thresholds.get('dscr_min', 'N/A')}x\n"
            f"  Current Ratio (Current Assets / Current Liabilities): min {thresholds.get('current_ratio_min', 'N/A')}x\n"
            f"  Covenant headroom above minimums:\n"
            f"    DSCR: +{self.get_covenant_headroom('dscr') * 100:.0f}%  "
            f"Leverage: +{self.get_covenant_headroom('leverage') * 100:.0f}%  "
            f"Interest Coverage: +{self.get_covenant_headroom('interest_coverage') * 100:.0f}%"
        )
