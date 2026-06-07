"""Shared utilities for Workflow B -- Synthesize & Store Clusters.

Purpose: Group raw intelligence rows and prepare topic cluster records.
Input: raw_intelligence-like JSON rows from data/verified/aeo-workflow-a/ or database exports.
Output: topic cluster, source-link, processed-item, and webhook payload records.
Side effects: Optional file writes through caller scripts; no network or database calls.
Idempotent: Yes; local grouping and record preparation are deterministic.
Recipe: recipes/workflow-b-synthesize-store-clusters.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_input(sample: Any | None = None) -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="JSON string or path to a JSON file.")
    parser.add_argument("--output", help="Optional path to write JSON output.")
    args = parser.parse_args()
    if args.input:
        candidate = Path(args.input)
        text = candidate.read_text() if candidate.exists() else args.input
        data = json.loads(text)
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
        data = json.loads(text) if text else sample
    else:
        data = sample
    return {"data": data, "output": args.output}


def emit(data: Any, output_path: str | None = None) -> None:
    text = json.dumps(data, indent=2, sort_keys=True, default=str)
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n")
    print(text)


def unprocessed_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return rows that are not marked processed, sorted like the n8n query."""
    return sorted([row for row in rows if not row.get("processed")], key=lambda row: (row.get("topic_tag") or "", row.get("pulled_date") or ""), reverse=True)


def group_by_topic(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group raw intelligence rows by topic_tag and build synthesis prompts."""
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(str(row.get("topic_tag") or "ai"), []).append(row)
    outputs: list[dict[str, Any]] = []
    for topic, items in sorted(groups.items()):
        combined = []
        for item in items:
            combined.append(f"- {item.get('title', '')} ({item.get('source_name', '')}): {item.get('raw_content', '')} URL: {item.get('url', '')}")
        outputs.append(
            {
                "topic_tag": topic,
                "item_count": len(items),
                "raw_ids": [item.get("id") for item in items],
                "source_urls": [item.get("url") for item in items if item.get("url")],
                "combined_text": "\n".join(combined),
                "items": items,
            }
        )
    return outputs


def synthesize_cluster(group: dict[str, Any]) -> dict[str, Any]:
    """Create a deterministic local cluster synthesis from grouped rows."""
    topic = group.get("topic_tag", "ai")
    items = group.get("items", [])
    titles = [str(item.get("title") or "").strip() for item in items if item.get("title")]
    title_terms = " ".join(titles[:3])
    title = f"{str(topic).title()} intelligence cluster"
    if title_terms:
        words = re.findall(r"[A-Za-z0-9$.-]+", title_terms)[:8]
        title = " ".join(words)[:80]
    source_names = sorted({str(item.get("source_name") or "unknown") for item in items})
    summary = (
        f"{len(items)} unprocessed items in topic '{topic}' were grouped from {', '.join(source_names)}. "
        "The cluster should be reviewed for corroboration, novelty, and whether it is strong enough for downstream AEO FAQ generation."
    )
    confidence = 8 if len(source_names) >= 3 and len(items) >= 5 else 6 if len(items) >= 2 else 4
    return {
        "cluster_title": title,
        "topic_tag": topic,
        "summary": summary,
        "source_urls": group.get("source_urls", [])[:5],
        "item_count": len(items),
        "confidence_score": confidence,
        "raw_ids": group.get("raw_ids", []),
        "created_date": datetime.now(timezone.utc).isoformat(),
        "phase2_status": "pending",
        "live_model_called": False,
    }


def parse_cluster_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize Claude/local cluster output to required fields."""
    text = payload.get("output") or payload.get("response") or payload
    if isinstance(text, str):
        text = json.loads(text)
    source_urls = text.get("top_source_urls") or text.get("source_urls") or []
    return {
        "cluster_title": str(text.get("cluster_title") or "Untitled cluster")[:120],
        "topic_tag": text.get("topic_tag") or payload.get("topic_tag") or "ai",
        "summary": str(text.get("summary") or ""),
        "source_urls": source_urls,
        "item_count": int(text.get("item_count") or payload.get("item_count") or len(source_urls)),
        "confidence_score": int(text.get("confidence_score") or 0),
        "raw_ids": text.get("raw_ids") or payload.get("raw_ids") or [],
        "phase2_status": "pending",
    }


def insert_cluster_record(cluster: dict[str, Any]) -> dict[str, Any]:
    """Prepare an idempotent topic_clusters insert payload without writing to a database."""
    record = dict(cluster)
    record["table"] = "topic_clusters"
    record["operation"] = "insert_pending"
    record["cluster_id"] = record.get("cluster_id") or abs(hash(json.dumps(record, sort_keys=True, default=str))) % 10_000_000
    return record


def build_source_links(cluster: dict[str, Any]) -> list[dict[str, Any]]:
    """Prepare cluster_sources link rows."""
    cluster_id = cluster.get("cluster_id") or cluster.get("id")
    return [{"cluster_id": cluster_id, "raw_intelligence_id": raw_id} for raw_id in cluster.get("raw_ids", []) if raw_id is not None]


def mark_processed_payload(cluster: dict[str, Any]) -> dict[str, Any]:
    """Prepare raw_intelligence processed-state update payload."""
    ids = [raw_id for raw_id in cluster.get("raw_ids", []) if raw_id is not None]
    return {"table": "raw_intelligence", "operation": "mark_processed", "ids": ids, "ids_str": ",".join(map(str, ids))}


def format_webhook(clusters: list[dict[str, Any]]) -> dict[str, Any]:
    """Format pending clusters for webhook response."""
    return {"count": len(clusters), "clusters": clusters, "generated_at": datetime.now(timezone.utc).isoformat()}
