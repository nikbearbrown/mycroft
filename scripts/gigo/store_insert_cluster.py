"""Purpose: Prepare topic_clusters insert payload.
Input: Validated cluster JSON from data/verified/aeo-workflow-b/.
Output: Idempotent insert payload for topic_clusters.
Side effects: Optional file write only; no database writes.
Idempotent: Yes; record preparation is deterministic.
Recipe: recipes/workflow-b-synthesize-store-clusters.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.aeo_cluster_shared import emit, insert_cluster_record, load_input


def store_insert_cluster(cluster: dict[str, Any]) -> dict[str, Any]:
    """Purpose: Prepare topic_clusters insert payload.
    Input: Validated cluster JSON.
    Output: Idempotent insert payload for topic_clusters.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/workflow-b-synthesize-store-clusters.md
    """
    return insert_cluster_record(cluster)


if __name__ == "__main__":
    payload = load_input({"cluster_title": "AI cluster", "topic_tag": "ai", "summary": "Summary", "confidence_score": 7})
    emit(store_insert_cluster(payload["data"]), payload["output"])
