import pytest

from gateway.adapters.base import FAILURE_KINDS, LLMResponse, ProviderError
from gateway.adapters.fake import FakeAdapter
from gateway.schema import OUTCOMES


def test_fake_returns_a_response():
    fake = FakeAdapter()
    resp = fake.complete(model="small", prompt="hello there", max_tokens=100)

    assert resp.provider == "fake"
    assert resp.model == "small"
    assert resp.text == "fake response"
    assert resp.latency_ms == 10


def test_token_counts_are_deterministic():
    fake = FakeAdapter()
    a = fake.complete(model="small", prompt="one two three", max_tokens=100)
    b = fake.complete(model="small", prompt="one two three", max_tokens=100)

    assert a.tokens_in == b.tokens_in == 3
    assert a.tokens_out == b.tokens_out == 2  # "fake response"


def test_queued_responses_come_out_in_order():
    fake = FakeAdapter()
    fake.queue_response("first").queue_response("second")

    assert fake.complete(model="m", prompt="p", max_tokens=10).text == "first"
    assert fake.complete(model="m", prompt="p", max_tokens=10).text == "second"
    # script exhausted -> falls back to the default
    assert fake.complete(model="m", prompt="p", max_tokens=10).text == "fake response"


def test_queued_error_raises_provider_error():
    fake = FakeAdapter()
    fake.queue_error(kind="timeout", message="took too long")

    with pytest.raises(ProviderError) as exc:
        fake.complete(model="small", prompt="p", max_tokens=10)

    assert exc.value.kind == "timeout"
    assert exc.value.model == "small"


def test_cheap_fails_then_strong_succeeds():
    """The sequence the whole gateway exists to handle."""
    fake = FakeAdapter()
    fake.queue_error(kind="provider_error").queue_response("good answer")

    with pytest.raises(ProviderError):
        fake.complete(model="cheap", prompt="p", max_tokens=10)

    resp = fake.complete(model="strong", prompt="p", max_tokens=10)
    assert resp.text == "good answer"
    assert [c["model"] for c in fake.calls] == ["cheap", "strong"]


def test_llm_response_rejects_negative_values():
    with pytest.raises(ValueError):
        LLMResponse(text="x", provider="p", model="m",
                    tokens_in=-1, tokens_out=0, latency_ms=0)
    with pytest.raises(ValueError):
        LLMResponse(text="x", provider="p", model="m",
                    tokens_in=0, tokens_out=0, latency_ms=-5)


def test_unknown_failure_kind_is_rejected():
    with pytest.raises(ValueError, match="not one of"):
        ProviderError("boom", provider="p", model="m", kind="exploded")


def test_failure_kinds_are_valid_logbook_outcomes():
    """Pins the two vocabularies together so they cannot drift apart."""
    assert FAILURE_KINDS < OUTCOMES