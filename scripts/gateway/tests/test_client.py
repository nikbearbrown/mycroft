import pytest

from gateway.adapters.fake import FakeAdapter
from gateway.client import GatewayClient, NoAdapterForProvider, UnknownTier
from gateway.logbook import Logbook
from gateway.prices import UnknownModelPrice
from gateway.report import read_records

TIERS = {
    "cheap":  {"provider": "groq", "model": "small"},
    "strong": {"provider": "anthropic", "model": "strong"},
}


def make_client(log_path, prices, adapters=None, clock=None):
    fake_groq = FakeAdapter(provider="groq")
    fake_anthropic = FakeAdapter(provider="anthropic")
    return GatewayClient(
        logbook=Logbook(log_path, prices),
        adapters=adapters or {"groq": fake_groq, "anthropic": fake_anthropic},
        tiers=TIERS,
        policy_version="0.1.0",
        clock=clock or (lambda: 0.0),
    ), fake_groq, fake_anthropic


def test_a_successful_call_writes_one_ok_row(log_path, prices_v1):
    client, _, _ = make_client(log_path, prices_v1)
    result = client.call(task_type="news_classification", caller="test",
                         tier="cheap", prompt="one two three")

    rows = read_records(log_path)
    assert len(rows) == 1
    assert rows[0]["outcome"] == "ok"
    assert rows[0]["provider"] == "groq"
    assert rows[0]["model"] == "small"
    assert rows[0]["tier"] == "cheap"
    assert rows[0]["request_id"] == result.request_id


def test_cost_is_recorded_from_the_response(log_path, prices_v1):
    client, _, _ = make_client(log_path, prices_v1)
    client.call(task_type="t", caller="c", tier="cheap", prompt="one two three")

    row = read_records(log_path)[0]
    # 3 words in, "fake response" = 2 words out
    # 3/1000 * 0.10 + 2/1000 * 0.20 = 0.0003 + 0.0004 = 0.0007
    assert row["tokens_in"] == 3
    assert row["tokens_out"] == 2
    assert row["cost_usd"] == pytest.approx(0.0007)


def test_a_provider_failure_is_recorded_and_reraised(log_path, prices_v1):
    client, fake_groq, _ = make_client(log_path, prices_v1)
    fake_groq.queue_error(kind="timeout", message="took too long")

    with pytest.raises(Exception):
        client.call(task_type="t", caller="c", tier="cheap", prompt="p")

    rows = read_records(log_path)
    assert len(rows) == 1, "a failed attempt is still a row"
    assert rows[0]["outcome"] == "timeout"
    assert rows[0]["tokens_in"] == 0
    assert rows[0]["tokens_out"] == 0
    assert rows[0]["cost_usd"] == 0.0


def test_escalation_shares_one_request_id(log_path, prices_v1):
    client, fake_groq, _ = make_client(log_path, prices_v1)
    fake_groq.queue_error(kind="provider_error")

    rid = client.logbook.begin_request(task_type="t", caller="c")
    with pytest.raises(Exception):
        client.call(task_type="t", caller="c", tier="cheap",
                    prompt="p", request_id=rid)
    client.call(task_type="t", caller="c", tier="strong",
                prompt="p", request_id=rid, routing_reason="escalation")

    rows = read_records(log_path)
    assert [r["attempt_no"] for r in rows] == [1, 2]
    assert {r["request_id"] for r in rows} == {rid}
    assert rows[1]["routing_reason"] == "escalation"


def test_an_unpriceable_model_is_refused_before_the_call(log_path, prices_v1):
    """No money is spent on a request that could not be accounted for."""
    fake = FakeAdapter(provider="mystery")
    client = GatewayClient(
        logbook=Logbook(log_path, prices_v1),
        adapters={"mystery": fake},
        tiers={"odd": {"provider": "mystery", "model": "unpriced"}},
        policy_version="0.1.0",
    )

    with pytest.raises(UnknownModelPrice):
        client.call(task_type="t", caller="c", tier="odd", prompt="p")

    assert fake.calls == [], "the adapter must never have been reached"
    assert not log_path.exists()


def test_unknown_tier_is_refused(log_path, prices_v1):
    client, _, _ = make_client(log_path, prices_v1)
    with pytest.raises(UnknownTier):
        client.call(task_type="t", caller="c", tier="nonexistent", prompt="p")


def test_tier_naming_a_missing_adapter_is_refused(log_path, prices_v1):
    client, _, _ = make_client(log_path, prices_v1, adapters={"groq": FakeAdapter()})
    with pytest.raises(NoAdapterForProvider):
        client.call(task_type="t", caller="c", tier="strong", prompt="p")


def test_latency_comes_from_the_clients_clock(log_path, prices_v1):
    ticks = iter([0.0, 0.3])       # start, end -> 300ms
    client, _, _ = make_client(log_path, prices_v1, clock=lambda: next(ticks))
    client.call(task_type="t", caller="c", tier="cheap", prompt="p")

    assert read_records(log_path)[0]["latency_ms"] == 300