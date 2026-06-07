"""Purpose: Clean, normalize, validate, or prepare storage payloads for this converted workflow node.
Input: JSON-compatible data from data/raw/, data/verified/, logs/, or stdin.
Output: JSON-compatible node result for downstream recipe steps.
Side effects: Optional file write only; live external effects are represented as approval-required handoff specs.
Idempotent: Yes; same input yields the same local output except generated timestamps.
Recipe: recipes/techstackcomparativeagentworkflow.md
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKFLOW_NAME = 'TechStackComparativeAgentWorkflow'
WORKFLOW_SLUG = 'techstackcomparativeagentworkflow'
NODE_NAME = 'Split Out'
NODE_TYPE = 'n8n-nodes-base.splitOut'
CLASSIFICATION = 'gigo'


def load_input(sample: Any | None = None) -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="JSON string or path to a JSON file.")
    parser.add_argument("--output", help="Optional path to write JSON output.")
    args = parser.parse_args()
    if args.input:
        candidate = Path(args.input)
        data = json.loads(candidate.read_text() if candidate.exists() else args.input)
    else:
        data = sample if sample is not None else {}
    return {"data": data, "output": args.output}


def emit(data: Any, output_path: str | None = None) -> None:
    text = json.dumps(data, indent=2, sort_keys=True, default=str)
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n")
    print(text)


def split_out(payload: Any) -> dict[str, Any]:
    """Purpose: Clean, normalize, validate, or prepare storage payloads for this converted workflow node.
    Input: JSON-compatible payload.
    Output: JSON-compatible result for this node.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; deterministic local conversion.
    Recipe: recipes/techstackcomparativeagentworkflow.md
    """
    result: dict[str, Any] = {
        "workflow": WORKFLOW_NAME,
        "node": NODE_NAME,
        "node_type": NODE_TYPE,
        "classification": CLASSIFICATION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": payload,
    }
    if CLASSIFICATION == "ingest":
        result.update({"status": "source_handoff", "live_call_performed": False, "credential_policy": "Use environment variables only; never hardcode credentials."})
    elif CLASSIFICATION == "gigo":
        items = payload if isinstance(payload, list) else payload.get("items", payload.get("records", [])) if isinstance(payload, dict) else []
        result.update({"status": "normalized", "record_count": len(items) if isinstance(items, list) else 1, "records": items if isinstance(items, list) else [payload]})
    else:
        result.update({"status": "tool_handoff", "live_call_performed": False, "review_required": True})
    return result


if __name__ == "__main__":
    payload = load_input({"sample": True, "node": NODE_NAME})
    emit(split_out(payload["data"]), payload["output"])
