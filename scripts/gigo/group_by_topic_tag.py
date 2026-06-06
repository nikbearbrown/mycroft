"""Purpose: Group unprocessed raw intelligence rows by topic_tag.
Input: Unprocessed raw_intelligence rows from data/verified/aeo-workflow-a/.
Output: Topic-group records with combined_text and source IDs.
Side effects: Optional file write only.
Idempotent: Yes; grouping is deterministic.
Recipe: recipes/workflow-b-synthesize-store-clusters.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.aeo_cluster_shared import emit, group_by_topic, load_input


def group_by_topic_tag(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Purpose: Group unprocessed raw intelligence rows by topic_tag.
    Input: Unprocessed raw_intelligence rows.
    Output: Topic-group records with combined_text and source IDs.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/workflow-b-synthesize-store-clusters.md
    """
    return group_by_topic(rows)


if __name__ == "__main__":
    sample = [{"id": 1, "topic_tag": "ai", "title": "AI news", "raw_content": "Body", "url": "u"}]
    payload = load_input(sample)
    emit(group_by_topic_tag(payload["data"]), payload["output"])
