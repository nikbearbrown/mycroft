import pytest

from gateway.schema import SchemaError, new_request_id, validate_record


def valid_record() -> dict:
    return {
        "request_id": new_request_id(),
        "attempt_no": 1,
        "task_type": "news_classification",
        "provider": "groq",
        "model": "small",
        "tier": "cheap",
        "routing_reason": "policy",
        "policy_version": "0.1.0",
        "tokens_in": 100,
        "tokens_out": 50,
        "cost_usd": 0.02,
        "price_table_version": "test-v1",
        "latency_ms": 120,
        "outcome": "ok",
        "caller": "test-caller",
        "timestamp_utc": "2026-08-26T10:00:00+00:00",
        "parent_request_id": None,
        "validator_result": None,
        "schema_version": "1.0.0",
        "notes": None,
    }


def test_a_valid_record_passes():
    assert validate_record(valid_record())


def test_missing_required_field_is_rejected():
    record = valid_record()
    del record["task_type"]
    with pytest.raises(SchemaError, match="task_type"):
        validate_record(record)


def test_unknown_outcome_is_rejected():
    record = valid_record()
    record["outcome"] = "probably_fine"
    with pytest.raises(SchemaError, match="outcome"):
        validate_record(record)


def test_negative_cost_is_rejected():
    record = valid_record()
    record["cost_usd"] = -0.01
    with pytest.raises(SchemaError, match="cost_usd"):
        validate_record(record)


def test_non_utc_timestamp_is_rejected():
    record = valid_record()
    record["timestamp_utc"] = "2026-08-26T10:00:00+05:30"
    with pytest.raises(SchemaError, match="not UTC"):
        validate_record(record)

    record = valid_record()
    record["timestamp_utc"] = "2026-08-26T10:00:00"
    with pytest.raises(SchemaError, match="no timezone offset"):
        validate_record(record)