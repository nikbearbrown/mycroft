"""Purpose: Format pending topic clusters as a webhook response payload.
Input: List of topic cluster records from data/verified/aeo-workflow-b/.
Output: JSON response payload for reports/generated/ or local webhook handoff.
Side effects: Optional file write only; no network calls.
Idempotent: Yes except generated_at timestamp.
Recipe: recipes/workflow-b-synthesize-store-clusters.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.aeo_cluster_shared import emit, format_webhook, load_input


def format_cluster_webhook_output(clusters: list[dict[str, Any]]) -> dict[str, Any]:
    """Purpose: Format pending topic clusters as a webhook response payload.
    Input: List of topic cluster records.
    Output: JSON response payload.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes except timestamp.
    Recipe: recipes/workflow-b-synthesize-store-clusters.md
    """
    return format_webhook(clusters)


if __name__ == "__main__":
    payload = load_input([{"cluster_title": "AI cluster", "confidence_score": 7}])
    emit(format_cluster_webhook_output(payload["data"]), payload["output"])
