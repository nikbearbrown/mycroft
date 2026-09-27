"""Define and validate the gateway logbook record contract."""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = "1.0.0"

OUTCOMES = frozenset({"ok", "validator_fail", "provider_error", "timeout"})
ROUTING_REASONS = frozenset({"policy", "pin", "escalation", "shadow", "override"})

_REQUIRED_STR_FIELDS = (
    "request_id", "task_type", "provider", "model", "tier",
    "routing_reason", "policy_version", "price_table_version",
    "outcome", "caller",
)


class SchemaError(ValueError):
    """Raised when an attempt record violates the logbook contract."""


def new_request_id() -> str:
    # All attempts serving one request share this. Retries do NOT get a
    # fresh id -- that is what would make a retried request look cheaper.
    return uuid.uuid4().hex


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Attempt:
    """One physical call to one model. Never mutated after construction."""

    request_id: str
    attempt_no: int
    task_type: str
    provider: str
    model: str
    tier: str
    routing_reason: str
    policy_version: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    price_table_version: str
    latency_ms: int
    outcome: str
    caller: str
    timestamp_utc: str = field(default_factory=utc_now_iso)
    parent_request_id: str | None = None
    validator_result: dict[str, Any] | None = None
    schema_version: str = SCHEMA_VERSION
    notes: str | None = None

    def to_record(self) -> dict[str, Any]:
        return asdict(self)


def validate_record(record: dict[str, Any]) -> dict[str, Any]:
    """Reject a record that would corrupt downstream measurement."""
    for key in _REQUIRED_STR_FIELDS:
        value = record.get(key)
        if not isinstance(value, str) or not value.strip():
            raise SchemaError(f"{key!r} must be a non-empty string, got {value!r}")

    if record["outcome"] not in OUTCOMES:
        raise SchemaError(f"outcome {record['outcome']!r} is not one of {sorted(OUTCOMES)}")

    if record["routing_reason"] not in ROUTING_REASONS:
        raise SchemaError(f"routing_reason {record['routing_reason']!r} is invalid")

    attempt_no = record.get("attempt_no")
    if not isinstance(attempt_no, int) or isinstance(attempt_no, bool) or attempt_no < 1:
        raise SchemaError(f"attempt_no must be an int >= 1, got {attempt_no!r}")

    for key in ("tokens_in", "tokens_out", "latency_ms"):
        value = record.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise SchemaError(f"{key} must be a non-negative int, got {value!r}")

    cost = record.get("cost_usd")
    if isinstance(cost, bool) or not isinstance(cost, (int, float)) or cost < 0:
        raise SchemaError(f"cost_usd must be a non-negative number, got {cost!r}")

    parent = record.get("parent_request_id")
    if parent is not None and (not isinstance(parent, str) or not parent.strip()):
        raise SchemaError("parent_request_id must be a non-empty string or None")

    validator_result = record.get("validator_result")
    if validator_result is not None and not isinstance(validator_result, dict):
        raise SchemaError("validator_result must be a dict or None")

    timestamp = record.get("timestamp_utc")
    if not isinstance(timestamp, str) or not timestamp.strip():
        raise SchemaError("timestamp_utc must be a non-empty string")
    parsed = datetime.fromisoformat(timestamp)
    if parsed.utcoffset() is None:
        raise SchemaError(f"timestamp_utc {timestamp!r} has no timezone offset")
    if parsed.utcoffset().total_seconds() != 0:
        raise SchemaError(f"timestamp_utc {timestamp!r} is not UTC")

    return record