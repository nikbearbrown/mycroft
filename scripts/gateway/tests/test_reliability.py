"""What happens when the provider misbehaves. Sprint 9.

Two layers decide how a failure is handled, and both are tested here.

The adapter decides what KIND of failure it was and whether a retry could
possibly help. That judgment is not obvious: a 429 asking you to slow down is
worth retrying, and a 429 saying the request is too large never is -- waiting
cannot shrink a prompt. Getting that wrong costs either money (retrying the
hopeless) or answers (giving up on the recoverable).

The gateway decides what to DO about it. The rules it must hold even when
everything is on fire: one retry and never two, no retry at all on a terminal
error, a row in the logbook for every attempt including the failed ones, and a
caller who gets a result object rather than an exception.

The second of those matters most. All three tiers sit behind one provider and
one credential, so an outage is not partial -- it takes the whole ladder. The
only thing that survives it is the record.
"""

import pytest

from gateway.adapters.base import ProviderError
from gateway.adapters.fake import FakeAdapter
from gateway.adapters.groq import GroqAdapter
from gateway.client import GatewayClient
from gateway.gateway import Gateway
from gateway.logbook import Logbook
from gateway.policy import Policy
from gateway.report import read_records
from gateway.tiers import TierConfig

LABELS = ["positive", "negative", "neutral"]


# -- how the adapter classifies a failure --------------------------------

class StubClient:
    """Mimics the SDK surface the adapter touches. No network."""

    def __init__(self, error):
        self._error = error
        self.chat = type("Chat", (), {"completions": self})()

    def create(self, **kwargs):
        raise self._error


def raised_by(error) -> ProviderError:
    adapter = GroqAdapter(client=StubClient(error))
    with pytest.raises(ProviderError) as caught:
        adapter.complete(model="m", prompt="p", max_tokens=16)
    return caught.value


def error_with(status=None, message="something went wrong", name="APIError"):
    return type(name, (Exception,), {"status_code": status})(message)


def test_a_bad_credential_is_terminal():
    """Every tier shares one key, so a retry fails identically. Never retry it."""
    failure = raised_by(error_with(401, "invalid_api_key"))
    assert failure.kind == "provider_error"
    assert failure.retryable is False


def test_a_missing_model_is_terminal():
    """qwen3.6-27b vanished mid-project; retrying would not have brought it back."""
    assert raised_by(error_with(404, "model does not exist")).retryable is False


def test_rate_limiting_is_retryable_and_says_so_in_the_message():
    failure = raised_by(error_with(429, "Rate limit reached for model"))
    assert failure.retryable is True
    assert "rate_limit" in str(failure)


def test_a_429_about_request_size_is_terminal_despite_being_a_429():
    """The distinction that cost a whole tier on 2026-09-17.

    Waiting fixes a pacing 429 and can never fix an oversize one -- only a
    smaller budget can. Both arrive as 429.
    """
    failure = raised_by(error_with(429, "Request too large: reduce max_tokens"))
    assert failure.retryable is False


def test_a_timeout_is_recorded_as_a_timeout_not_a_generic_error():
    failure = raised_by(error_with(None, "connection timed out", name="APITimeoutError"))
    assert failure.kind == "timeout"
    assert failure.retryable is True


# -- what the gateway does about it --------------------------------------

def build(log_path, prices, *, escalate="mid"):
    tiers = TierConfig({"version": "t", "tiers": {
        "cheap": {"provider": "groq", "model": "small", "status": "evidenced",
                  "evidence": "test", "context_limit": 131072, "capabilities": ["text"]},
        "mid": {"provider": "groq", "model": "large", "status": "evidenced",
                "evidence": "test", "context_limit": 131072, "capabilities": ["text"]},
        "strong": {"provider": "anthropic", "model": "strong", "status": "evidenced",
                   "evidence": "test", "context_limit": 131072, "capabilities": ["text"]},
    }})
    policy = Policy({
        "version": "p",
        "tier_order": ["cheap", "mid", "strong"],
        "max_tokens_by_tier": {"cheap": 512, "mid": 512, "strong": 1024},
        "task_types": {"sentiment_classification": {
            "description": "Label the text.", "output": "label", "labels": LABELS,
            "validator": "label_in_set", "quality_check": "deterministic",
            "start_tier": "cheap", "escalate_to": escalate,
            "promote_above_chars": 100000, "evidence": ["x"]}}}, tiers)

    groq = FakeAdapter(provider="groq")
    client = GatewayClient(logbook=Logbook(log_path, prices),
                           adapters={"groq": groq,
                                     "anthropic": FakeAdapter(provider="anthropic")},
                           tiers=tiers.as_client_map(), policy_version="p",
                           clock=lambda: 0.0)
    return Gateway(client=client, policy=policy, tiers=tiers, caller="test"), groq


def ask(gateway):
    return gateway.handle(task_type="sentiment_classification",
                          text="Fake Industries beat estimates.")


def test_a_total_outage_returns_a_result_not_an_exception(log_path, prices_v1):
    """One provider, one credential: an outage takes every tier at once."""
    gateway, groq = build(log_path, prices_v1)
    groq.queue_error(message="service unavailable").queue_error(message="service unavailable")

    result = ask(gateway)  # must not raise

    assert result.error is not None
    assert result.text == ""
    assert result.passed is False


def test_every_failed_attempt_is_still_in_the_logbook(log_path, prices_v1):
    """The record is what survives an outage. A missing row looks like a cheap day."""
    gateway, groq = build(log_path, prices_v1)
    groq.queue_error(message="boom").queue_error(message="boom")

    result = ask(gateway)
    rows = read_records(log_path)

    assert len(rows) == 2 == result.attempts
    assert [r["outcome"] for r in rows] == ["provider_error", "provider_error"]
    assert {r["tier"] for r in rows} == {"cheap", "mid"}
    assert all(r["request_id"] == result.request_id for r in rows)


def test_a_partial_outage_still_answers(log_path, prices_v1):
    """Cheap is down, mid is up: the caller gets an answer and pays for two attempts."""
    gateway, groq = build(log_path, prices_v1)
    groq.queue_error(message="cheap is down").queue_response("positive")

    result = ask(gateway)

    assert result.passed and result.text == "positive"
    assert (result.escalated, result.final_tier) == (True, "mid")
    assert read_records(log_path)[1]["routing_reason"] == "escalation"


def test_a_terminal_failure_does_not_buy_a_second_attempt(log_path, prices_v1):
    """A bad key fails the same way on every tier. Retrying it is spending for nothing."""
    gateway, groq = build(log_path, prices_v1)
    groq.queue_error(message="invalid_api_key", retryable=False)

    result = ask(gateway)

    assert result.attempts == 1
    assert len(groq.calls) == 1
    assert result.error is not None


def test_a_timeout_is_retried_and_recorded_as_a_timeout(log_path, prices_v1):
    gateway, groq = build(log_path, prices_v1)
    groq.queue_error(kind="timeout", message="took too long").queue_response("positive")

    result = ask(gateway)
    rows = read_records(log_path)

    assert result.passed
    assert rows[0]["outcome"] == "timeout"
    assert rows[1]["outcome"] == "ok"


def test_a_failure_costs_nothing_but_is_still_priced_and_recorded(log_path, prices_v1):
    """Zero tokens, zero cost -- but a row, so the attempt is not invisible."""
    gateway, groq = build(log_path, prices_v1)
    groq.queue_error(message="boom").queue_error(message="boom")

    ask(gateway)
    rows = read_records(log_path)

    assert all(r["cost_usd"] == 0 for r in rows)
    assert all((r["tokens_in"], r["tokens_out"]) == (0, 0) for r in rows)
    assert all(r["price_table_version"] for r in rows)


def test_a_slow_answer_is_still_an_answer(log_path, prices_v1):
    """Latency is recorded, not judged. Nothing in the gateway gives up on slow."""
    gateway, groq = build(log_path, prices_v1)
    groq.queue_response("positive", latency_ms=9000)

    result = ask(gateway)

    assert result.passed
    assert result.attempts == 1


def test_an_outage_on_a_task_that_cannot_escalate_stops_at_one(log_path, prices_v1):
    gateway, groq = build(log_path, prices_v1, escalate=None)
    groq.queue_error(message="boom")

    result = ask(gateway)

    assert (result.attempts, len(groq.calls)) == (1, 1)
    assert result.error is not None