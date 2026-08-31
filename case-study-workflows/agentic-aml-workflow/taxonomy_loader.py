"""
taxonomy_loader.py
==================
Agentic AML Compliance Workflow — Taxonomy and Policy Library Loader
US Equities · OFAC/BSA/FinCEN

Loads aml_taxonomy.json at startup. Provides two context formatters:

  format_flag_context()    — formats the relevant flag entry for the triage agent
  format_policy_context()  — formats the policy library for the reasoning agent

Integration with the orchestrator:
  Both formatters are called BEFORE the relevant agent runs.
  The formatted text is prepended to the accumulated context chain.

  In AMLOrchestrator.run():

    Before triage_agent:
        taxonomy_ctx = loader.format_flag_context(trade.aml_flag.flag_type)
        context += f"\\n\\n[aml_taxonomy]:\\n{taxonomy_ctx}"

    Before reasoning_agent:
        policy_ctx = loader.format_policy_context()
        context += f"\\n\\n[policy_library]:\\n{policy_ctx}"

The [SOURCE: AML-TAXONOMY] and [SOURCE: POLICY-LIB] citation markers in
these formatted strings match the citation format defined in agent_validation.py.

Dependencies:
    pip install pydantic>=2.0
    aml_taxonomy.json must exist at TAXONOMY_PATH (default: same directory)
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default path — override via TAXONOMY_PATH environment variable
# [DEV] SET TAXONOMY FILE PATH ────────────────────────────────────────────────
# Default: looks for aml_taxonomy.json in the same directory as this file.
# Override by setting the TAXONOMY_PATH environment variable, or pass a path
# directly to TaxonomyLoader("path/to/your/aml_taxonomy.json").
# ─────────────────────────────────────────────────────────────────────────────
TAXONOMY_PATH = Path(
    os.environ.get("TAXONOMY_PATH", Path(__file__).parent / "aml_taxonomy.json")
)


class TaxonomyLoader:
    """
    Loads and formats the AML taxonomy and policy library for agent context injection.
    Load once at startup and reuse across all workflow invocations.

    Usage:
        loader = TaxonomyLoader()                  # loads from TAXONOMY_PATH
        loader = TaxonomyLoader("path/to/file.json")  # custom path

    The loader caches the parsed taxonomy on first load.
    Call reload() if the taxonomy file is updated at runtime.
    """

    def __init__(self, path: str | Path | None = None):
        self._path = Path(path) if path else TAXONOMY_PATH
        self._taxonomy: dict[str, Any] | None = None
        self._flags_by_type: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            raise FileNotFoundError(
                f"AML taxonomy file not found at '{self._path}'. "
                "Set the TAXONOMY_PATH environment variable to the correct path, "
                "or place aml_taxonomy.json in the same directory as taxonomy_loader.py."
            )
        with open(self._path, encoding="utf-8") as f:
            self._taxonomy = json.load(f)
        self._flags_by_type = {
            flag["flag_type"]: flag
            for flag in self._taxonomy.get("flags", [])
        }
        logger.info(
            f"AML taxonomy loaded from '{self._path}'. "
            f"{len(self._flags_by_type)} flag types: {list(self._flags_by_type.keys())}."
        )

    def reload(self) -> None:
        """Reloads the taxonomy from disk. Call if the file is updated at runtime."""
        self._load()
        logger.info("AML taxonomy reloaded.")

    # ─────────────────────────────────────────────────────────
    # TRIAGE AGENT CONTEXT
    # ─────────────────────────────────────────────────────────

    def format_flag_context(self, flag_type: str) -> str:
        """
        Returns formatted plain text for the specific AML flag type.
        Injected into the triage agent's context before it runs.

        The triage agent uses this to:
          - Understand what the flag means
          - Know the regulatory basis
          - Know what to direct the investigation agent to check
          - Assign the correct risk level

        The [SOURCE: AML-TAXONOMY] marker is embedded so the triage agent
        can cite it using the required citation format.
        """
        flag = self._flags_by_type.get(flag_type)
        if not flag:
            logger.warning(
                f"Flag type '{flag_type}' not found in taxonomy. "
                f"Known types: {list(self._flags_by_type.keys())}. "
                "Providing generic context."
            )
            return self._generic_flag_context(flag_type)

        thresholds = self._taxonomy.get("confidence_thresholds", {})

        lines = [
            "=== AML FLAG TAXONOMY [SOURCE: AML-TAXONOMY] ===",
            "",
            f"Flag type:     {flag['flag_type']}",
            f"Display name:  {flag['display_name']}",
            "",
            f"Description:",
            f"  {flag['description']}",
            "",
            "Regulatory basis:",
        ]
        for basis in flag.get("regulatory_basis", []):
            lines.append(f"  - {basis}")

        lines += [
            "",
            "Investigation checklist (direct the investigation agent to check each):",
        ]
        for item in flag.get("investigation_checklist", []):
            lines.append(f"  - {item}")

        lines += [
            "",
            "False positive indicators:",
        ]
        for indicator in flag.get("false_positive_indicators", []):
            lines.append(f"  - {indicator}")

        lines += [
            "",
            "Genuine concern indicators:",
        ]
        for indicator in flag.get("genuine_concern_indicators", []):
            lines.append(f"  - {indicator}")

        lines += [
            "",
            f"SAR consideration: {flag.get('sar_consideration', 'Consult BSA Officer.')}",
            "",
            f"Triage guidance: {flag.get('triage_guidance', '')}",
            "",
            "Confidence thresholds [SOURCE: AML-TAXONOMY]:",
            f"  Auto-clear below:      {thresholds.get('auto_clear_below', 0.30)}",
            f"  Investigation zone:    {thresholds.get('investigation_zone_low', 0.30)} – {thresholds.get('investigation_zone_high', 0.85)}",
            f"  Auto-escalate above:   {thresholds.get('auto_escalate_above', 0.85)}",
            f"  Note: {thresholds.get('note', '')}",
        ]

        return "\n".join(lines)

    def _generic_flag_context(self, flag_type: str) -> str:
        """Fallback context for unrecognized flag types."""
        thresholds = (self._taxonomy or {}).get("confidence_thresholds", {})
        return (
            f"=== AML FLAG TAXONOMY [SOURCE: AML-TAXONOMY] ===\n\n"
            f"Flag type: {flag_type}\n"
            f"Note: This flag type is not in the current taxonomy file. "
            f"Apply standard AML investigation procedure.\n\n"
            f"Confidence thresholds:\n"
            f"  Auto-clear below:    {thresholds.get('auto_clear_below', 0.30)}\n"
            f"  Auto-escalate above: {thresholds.get('auto_escalate_above', 0.85)}\n"
        )

    # ─────────────────────────────────────────────────────────
    # REASONING AGENT CONTEXT
    # ─────────────────────────────────────────────────────────

    def format_policy_context(self) -> str:
        """
        Returns formatted plain text from the policy library.
        Injected into the reasoning agent's context before it runs.

        The reasoning agent uses this to:
          - Cite specific regulatory provisions in its numbered reasoning chain
          - Determine whether SAR filing criteria are met
          - Reference KYC review cycle requirements
          - Reference OFAC compliance obligations

        The [SOURCE: POLICY-LIB] marker is embedded for citation.
        """
        if not self._taxonomy:
            return "=== COMPLIANCE POLICY LIBRARY [SOURCE: POLICY-LIB] ===\nNot loaded."

        policy = self._taxonomy.get("policy_library", {})
        lines = ["=== COMPLIANCE POLICY LIBRARY [SOURCE: POLICY-LIB] ===", ""]

        # SAR filing
        sar = policy.get("sar_filing", {})
        if sar:
            lines += [
                f"SAR FILING REQUIREMENTS:",
                f"  Regulatory basis: {sar.get('regulatory_basis', '')}",
                f"  Filing threshold: USD {sar.get('filing_threshold_usd', 5000):,}",
                f"  Filing deadline:  {sar.get('filing_deadline_days', 30)} days "
                f"(extended: {sar.get('extended_deadline_days', 60)} days)",
                f"  Confidentiality:  {sar.get('confidentiality_requirement', '')}",
                f"  Note: {sar.get('note', '')}",
                "",
            ]

        # KYC review cycles
        kyc = policy.get("kyc_review_cycles", {})
        if kyc:
            lines += [f"KYC REVIEW CYCLE THRESHOLDS:"]
            lines.append(f"  Regulatory basis: {kyc.get('regulatory_basis', '')}")
            for tier, cycle in kyc.get("cycles", {}).items():
                lines.append(
                    f"  {tier}: {cycle['months']}-month cycle — {cycle.get('note', '')}"
                )
            lines += [f"  Note: {kyc.get('note', '')}", ""]

        # OFAC compliance
        ofac = policy.get("ofac_compliance", {})
        if ofac:
            lines += [
                f"OFAC SANCTIONS COMPLIANCE:",
                f"  Regulatory basis: {ofac.get('regulatory_basis', '')}",
                f"  List staleness threshold: {ofac.get('list_staleness_threshold_hours', 24)} hours",
                f"  Query method: {ofac.get('query_method', '')}",
                f"  Blocked transactions: {ofac.get('blocked_transaction_requirements', '')}",
                "",
            ]

        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────
    # UTILITY
    # ─────────────────────────────────────────────────────────

    def list_flag_types(self) -> list[str]:
        """Returns all flag types defined in the taxonomy."""
        return list(self._flags_by_type.keys())

    def get_confidence_thresholds(self) -> dict[str, float]:
        """Returns the confidence score routing thresholds."""
        t = (self._taxonomy or {}).get("confidence_thresholds", {})
        return {
            "auto_clear_below": float(t.get("auto_clear_below", 0.30)),
            "auto_escalate_above": float(t.get("auto_escalate_above", 0.85)),
        }


# ─────────────────────────────────────────────────────────────
# MODULE-LEVEL SINGLETON — load once at startup
# ─────────────────────────────────────────────────────────────

_loader: TaxonomyLoader | None = None


def get_loader(path: str | Path | None = None) -> TaxonomyLoader:
    """
    Returns the module-level TaxonomyLoader, loading it on first call.
    Pass `path` to override the default TAXONOMY_PATH on first call only.

    Usage in orchestrator:
        from taxonomy_loader import get_loader
        loader = get_loader()
        context += f"\\n\\n[aml_taxonomy]:\\n{loader.format_flag_context(flag_type)}"
    """
    global _loader
    if _loader is None:
        _loader = TaxonomyLoader(path)
    return _loader
