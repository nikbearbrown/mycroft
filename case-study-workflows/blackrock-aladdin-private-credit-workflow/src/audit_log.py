"""
Audit Log.

§4's [DEV] marker takes no position: "no source confirms whether an
equivalent audit-log mechanism exists in BlackRock's actual production
system. If you build one, document that choice as yours." This repo builds
one — cheap, low-risk, and a clean, obvious place to demonstrate a safe
extension point (add a field, swap the storage backend). Documented here,
explicitly, as this repo's own choice, not BlackRock's confirmed practice.
"""
import json
from datetime import datetime, timezone


class AuditLog:
    def __init__(self, path: str = "audit_log.jsonl"):
        self.path = path

    def append(self, query_id: str, module: str, output: str) -> None:
        entry = {
            "query_id": query_id,
            "module": module,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "output_summary": str(output)[:500],  # truncated — not a full LLM-draft dump
        }
        with open(self.path, "a") as f:
            f.write(json.dumps(entry) + "\n")
