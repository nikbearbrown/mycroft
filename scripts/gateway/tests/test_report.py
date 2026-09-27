import pytest

from gateway.logbook import Logbook
from gateway.report import (
    iter_provenance,
    naive_mean_cost_per_attempt,
    percentile,
    read_records,
    request_totals,
    summary,
)


def escalated_request(lb):
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


def test_cost_rolls_up_across_an_escalation(log_path, prices_v1):
    lb = Logbook(log_path, prices_v1)
    escalated_request(lb)

    totals = request_totals(read_records(log_path))
    assert len(totals) == 1, "two attempts are ONE logical request"
    # cheap 0.30 + strong 9.00
    assert totals[0]["total_cost_usd"] == pytest.approx(9.30)
    assert totals[0]["escalated"] is True


def test_naive_per_attempt_average_understates_cost(log_path, prices_v1):
    """The guard test: the wrong metric is provably wrong, and flatters cheap."""
    lb = Logbook(log_path, prices_v1)
    escalated_request(lb)
    records = read_records(log_path)

    correct = summary(records)["mean_cost_per_request_usd"]
    naive = naive_mean_cost_per_attempt(records)

    assert correct == pytest.approx(9.30)
    assert naive == pytest.approx(4.65)
    assert naive < correct, "per-attempt averaging must understate the truth"


def test_latency_sums_across_attempts(log_path, prices_v1):
    lb = Logbook(log_path, prices_v1)
    escalated_request(lb)
    assert request_totals(read_records(log_path))[0]["total_latency_ms"] == 1200


def test_rates_count_requests_not_attempts(log_path, prices_v1):
    lb = Logbook(log_path, prices_v1)
    escalated_request(lb)                       # 2 attempts, 1 request, succeeded

    rid = lb.begin_request(task_type="news_classification", caller="test-caller")
    lb.record_attempt(rid, provider="groq", model="small", tier="cheap",
                      routing_reason="policy", policy_version="0.1.0",
                      tokens_in=10, tokens_out=10, latency_ms=50,
                      outcome="provider_error")

    stats = summary(read_records(log_path))
    assert stats["requests"] == 2
    assert stats["attempts"] == 3
    assert stats["escalation_rate"] == pytest.approx(0.5)
    assert stats["failure_rate"] == pytest.approx(0.5)


def test_history_is_not_repriced_when_the_table_changes(log_path, prices_v1, prices_v2):
    lb_old = Logbook(log_path, prices_v1)
    rid_old = lb_old.begin_request(task_type="t", caller="c")
    lb_old.record_attempt(rid_old, provider="groq", model="small", tier="cheap",
                          routing_reason="policy", policy_version="0.1.0",
                          tokens_in=1000, tokens_out=0, latency_ms=100, outcome="ok")

    lb_new = Logbook(log_path, prices_v2)   # same file, new price table
    rid_new = lb_new.begin_request(task_type="t", caller="c")
    lb_new.record_attempt(rid_new, provider="groq", model="small", tier="cheap",
                          routing_reason="policy", policy_version="0.1.0",
                          tokens_in=1000, tokens_out=0, latency_ms=100, outcome="ok")

    old, new = read_records(log_path)
    assert old["cost_usd"] == pytest.approx(0.10)
    assert new["cost_usd"] == pytest.approx(0.20)
    assert old["price_table_version"] != new["price_table_version"]


def test_provenance_names_the_final_model(log_path, prices_v1):
    """'Which model wrote this claim?' -- it is the LAST one, not the first."""
    lb = Logbook(log_path, prices_v1)
    escalated_request(lb)

    rows = list(iter_provenance(read_records(log_path)))
    assert len(rows) == 1
    _, caller, final_model = rows[0]
    assert caller == "test-caller"
    assert final_model == "strong"


def test_percentile_returns_an_observed_value():
    assert percentile([10.0, 20.0, 30.0, 40.0], 50) == 20.0
    assert percentile([10.0, 20.0, 30.0, 40.0], 95) == 40.0
    with pytest.raises(ValueError):
        percentile([], 50)