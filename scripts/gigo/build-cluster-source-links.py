"""Purpose: Build cluster_sources link rows.
Input: Stored cluster payload with cluster_id and raw_ids.
Output: Link rows connecting topic clusters to raw intelligence IDs.
Side effects: Optional file write only.
Idempotent: Yes; link generation is deterministic.
Recipe: recipes/workflow-b-synthesize-store-clusters.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.aeo_cluster_shared import build_source_links, emit, load_input


def build_cluster_source_links(cluster: dict[str, Any]) -> list[dict[str, Any]]:
    """Purpose: Build cluster_sources link rows.
    Input: Stored cluster payload with cluster_id and raw_ids.
    Output: Link rows connecting topic clusters to raw intelligence IDs.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/workflow-b-synthesize-store-clusters.md
    """
    return build_source_links(cluster)


if __name__ == "__main__":
    payload = load_input({"cluster_id": 42, "raw_ids": [1, 2]})
    emit(build_cluster_source_links(payload["data"]), payload["output"])
