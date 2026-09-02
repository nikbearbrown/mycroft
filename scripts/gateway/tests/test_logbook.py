import json
import threading

import pytest

from gateway.logbook import Logbook, LogbookWriter
from gateway.prices import UnknownModelPrice
from gateway.schema import SchemaError


def read_lines(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def escalated_request(lb):
    """Cheap attempt fails validation, strong attempt succeeds."""
    rid = lb.begin_request(task_type="news_classification", caller="test-caller")
    lb.record_attempt(rid, provider="groq", model="small", tier="cheap",
                      routing_reason="policy", policy_version="0.1.0",
                      tokens_in=1000, tokens_out=1000, latency_ms=300,
                      outcome="validator_fail",
                      validator_result={"passed": False, "reason": "label_not_in_set"})
    lb.record_attempt(rid, provider="anthropic", model="strong", tier="strong",
                      routing_reason="escalation", policy_version="0.1.0",
                      tokens_in=1000, tokens_out=1000, latency_ms=900,
                      outcome="ok", validator_result={"passed": True})
    return rid


def test_one_attempt_writes_one_row(log_path, prices_v1):
    lb = Logbook(log_path, prices_v1)
    rid = lb.begin_request(task_type="t", caller="c")
    lb.record_attempt(rid, provider="groq", model="small", tier="cheap",
                      routing_reason="policy", policy_version="0.1.0",
                      tokens_in=1000, tokens_out=1000, latency_ms=5, outcome="ok")

    rows = read_lines(log_path)
    assert len(rows) == 1
    assert rows[0]["cost_usd"] == pytest.approx(0.30)
    assert rows[0]["price_table_version"] == "test-v1"


def test_escalation_reuses_the_same_request_id(log_path, prices_v1):
    lb = Logbook(log_path, prices_v1)
    rid = escalated_request(lb)

    rows = read_lines(log_path)
    assert {r["request_id"] for r in rows} == {rid}
    assert [r["attempt_no"] for r in rows] == [1, 2]


def test_unknown_task_type_is_recorded_not_defaulted(log_path, prices_v1):
    lb = Logbook(log_path, prices_v1)
    rid = lb.begin_request(task_type="something_nobody_defined", caller="c")
    lb.record_attempt(rid, provider="groq", model="small", tier="cheap",
                      routing_reason="policy", policy_version="0.1.0",
                      tokens_in=10, tokens_out=10, latency_ms=5, outcome="ok")

    assert read_lines(log_path)[0]["task_type"] == "something_nobody_defined"


def test_unknown_model_writes_nothing(log_path, prices_v1):
    lb = Logbook(log_path, prices_v1)
    rid = lb.begin_request(task_type="t", caller="c")
    with pytest.raises(UnknownModelPrice):
        lb.record_attempt(rid, provider="mystery", model="unpriced", tier="cheap",
                          routing_reason="policy", policy_version="0.1.0",
                          tokens_in=1000, tokens_out=1000, latency_ms=5, outcome="ok")
    assert not log_path.exists() or read_lines(log_path) == []


def test_invalid_record_never_reaches_the_file(log_path):
    writer = LogbookWriter(log_path)
    with pytest.raises(SchemaError):
        writer.append({"request_id": "x", "outcome": "nope"})
    assert not log_path.exists()


def test_opening_a_second_writer_does_not_truncate(log_path, prices_v1):
    lb = Logbook(log_path, prices_v1)
    rid = lb.begin_request(task_type="t", caller="c")
    lb.record_attempt(rid, provider="groq", model="small", tier="cheap",
                      routing_reason="policy", policy_version="0.1.0",
                      tokens_in=10, tokens_out=10, latency_ms=5, outcome="ok")

    Logbook(log_path, prices_v1)
    Logbook(log_path, prices_v1)
    assert len(read_lines(log_path)) == 1


def test_concurrent_writers_produce_whole_lines(log_path, prices_v1):
    """Interleaved appends must not lose or tear each other's rows."""
    writers = [Logbook(log_path, prices_v1) for _ in range(8)]

    def write_many(lb):
        for _ in range(25):
            rid = lb.begin_request(task_type="t", caller="c")
            lb.record_attempt(rid, provider="groq", model="small", tier="cheap",
                              routing_reason="policy", policy_version="0.1.0",
                              tokens_in=100, tokens_out=100, latency_ms=1, outcome="ok")

    threads = [threading.Thread(target=write_many, args=(lb,)) for lb in writers]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 200
    for line in lines:
        json.loads(line)