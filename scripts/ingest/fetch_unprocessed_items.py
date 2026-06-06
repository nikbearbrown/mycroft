"""Purpose: Load unprocessed raw_intelligence rows for Workflow B.
Input: JSON array from data/verified/aeo-workflow-a/ or approved database export.
Output: Unprocessed rows sorted for grouping.
Side effects: Reads only local JSON input; optional file write; no database calls.
Idempotent: Yes; filtering is deterministic.
Recipe: recipes/workflow-b-synthesize-store-clusters.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.aeo_cluster_shared import emit, load_input, unprocessed_rows


def fetch_unprocessed_items(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Purpose: Load unprocessed raw_intelligence rows for Workflow B.
    Input: JSON array from verified local data or database export.
    Output: Unprocessed rows sorted for grouping.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/workflow-b-synthesize-store-clusters.md
    """
    return unprocessed_rows(rows)


if __name__ == "__main__":
    sample = [{"id": 1, "topic_tag": "ai", "title": "AI news", "raw_content": "Body", "url": "u", "processed": False}]
    payload = load_input(sample)
    emit(fetch_unprocessed_items(payload["data"]), payload["output"])
