"""Purpose: Prepare cluster_sources insert payloads.
Input: Link rows from build_cluster_source_links.py.
Output: Idempotent insert payloads for cluster_sources.
Side effects: Optional file write only; no database writes.
Idempotent: Yes; row preparation is deterministic.
Recipe: recipes/workflow-b-synthesize-store-clusters.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.aeo_cluster_shared import emit, load_input


def store_insert_source_links(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Purpose: Prepare cluster_sources insert payloads.
    Input: Link rows.
    Output: Idempotent insert payloads for cluster_sources.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/workflow-b-synthesize-store-clusters.md
    """
    return [{"table": "cluster_sources", "operation": "insert_ignore", **row} for row in rows]


if __name__ == "__main__":
    payload = load_input([{"cluster_id": 42, "raw_intelligence_id": 1}])
    emit(store_insert_source_links(payload["data"]), payload["output"])
