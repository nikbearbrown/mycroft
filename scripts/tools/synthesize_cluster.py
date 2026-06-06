"""Purpose: Synthesize grouped raw intelligence into a topic cluster.
Input: Topic-group record from data/verified/aeo-workflow-b/.
Output: Cluster JSON with title, summary, source URLs, item count, and confidence.
Side effects: Optional file write only; no Anthropic call; ANTHROPIC_API_KEY is for future live adapter.
Idempotent: Yes; local synthesis is deterministic except created_date.
Recipe: recipes/workflow-b-synthesize-store-clusters.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.aeo_cluster_shared import emit, load_input, synthesize_cluster


def synthesize_cluster_tool(group: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Synthesize grouped raw intelligence into a topic cluster.
    Input: Topic-group record.
    Output: Cluster JSON with title, summary, source URLs, item count, and confidence.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes except timestamp.
    Recipe: recipes/workflow-b-synthesize-store-clusters.md
    """
    return synthesize_cluster(group)


if __name__ == "__main__":
    sample = {"topic_tag": "ai", "items": [{"title": "AI news", "source_name": "TechCrunch", "raw_content": "Body", "url": "u"}], "raw_ids": [1], "source_urls": ["u"]}
    payload = load_input(sample)
    emit(synthesize_cluster_tool(payload["data"]), payload["output"])
