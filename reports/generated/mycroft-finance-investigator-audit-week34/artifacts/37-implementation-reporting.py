"""Machine-log and human-report rendering."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_machine_log(
    path: Path,
    run_id: str,
    recipe_version: str,
    config: dict[str, Any],
    validation: dict[str, Any],
    investigation: dict[str, Any],
) -> None:
    payload = {
        "workflow": "mycroft-finance-investigator",
        "run_id": run_id,
        "recipe_version": recipe_version,
        "mode": "synthetic_sample",
        "config": config,
        "validation": validation,
        "investigation": investigation,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_human_report(
    path: Path,
    run_id: str,
    config: dict[str, Any],
    investigation: dict[str, Any],
) -> None:
    verified = [
        finding
        for finding in investigation["findings"]
        if finding["kind"] == "VERIFIED_CALCULATION"
    ]
    prompts = [
        finding
        for finding in investigation["findings"]
        if finding["kind"] == "INVESTIGATION_PROMPT"
    ]
    lines = [
        "# Monthly Performance Investigation",
        "",
        "## Review Status",
        "",
        f"- Run ID: `{run_id}`",
        "- Decision: `PENDING HUMAN REVIEW`",
        f"- Entity: {config['entity']}",
        f"- Period: {config['period']}",
        f"- Materiality: {config['materiality_amount']} (`{config['materiality_status']}`)",
        "",
        "## Question",
        "",
        config["question"],
        "",
        "## Verified Mathematical Findings",
        "",
        "| Finding | Evidence references |",
        "|---|---:|",
    ]
    for finding in verified:
        lines.append(
            f"| {finding['statement']} | {len(finding['evidence'])} |"
        )
    lines.extend(
        [
            "",
            "## Investigation Prompts",
            "",
        ]
    )
    if prompts:
        for finding in prompts:
            lines.append(f"- {finding['statement']}")
    else:
        lines.append("- No operational driver records were available.")
    lines.extend(
        [
            "",
            "## Current Explanation — Owner Required",
            "",
            "_Intentionally blank. The investigator does not infer business causation from numerical movement._",
            "",
            "## Evidence Index",
            "",
        ]
    )
    for reference in investigation["evidence"]:
        lines.append(f"- `{reference}`")
    lines.extend(
        [
            "",
            "## Agent Trace",
            "",
            "| Step | Tool | Reason |",
            "|---:|---|---|",
        ]
    )
    for step in investigation["trace"]:
        lines.append(f"| {step['step']} | `{step['tool']}` | {step['reason']} |")
    lines.extend(
        [
            "",
            "## Human Decision",
            "",
            "- Reviewer:",
            "- Review date:",
            "- Materiality decision:",
            "- Causal explanation and supporting evidence:",
            "- Distribution decision: `APPROVE` / `REQUEST CHANGES` / `BLOCK`",
            "",
            "### Did Not Test",
            "",
            "- Human adequacy of materiality and business explanations.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
