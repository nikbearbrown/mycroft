"""Purpose: Normalize Claude or local cluster synthesis output.
Input: Cluster JSON or model response from logs/.
Output: Validated topic cluster fields.
Side effects: Optional file write only.
Idempotent: Yes; parsing is deterministic.
Recipe: recipes/workflow-b-synthesize-store-clusters.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.aeo_cluster_shared import emit, load_input, parse_cluster_response as parse_response


def parse_cluster_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Normalize Claude or local cluster synthesis output.
    Input: Cluster JSON or model response.
    Output: Validated topic cluster fields.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/workflow-b-synthesize-store-clusters.md
    """
    return parse_response(payload)


if __name__ == "__main__":
    payload = load_input({"cluster_title": "AI cluster", "summary": "Summary", "confidence_score": 7, "source_urls": ["u"]})
    emit(parse_cluster_response(payload["data"]), payload["output"])
