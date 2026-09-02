import pytest

from gateway.adapters.base import ProviderError
from gateway.adapters.groq import GroqAdapter


class StubUsage:
    def __init__(self, prompt_tokens, completion_tokens):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class StubResponse:
    def __init__(self, text="hello", usage=None):
        message = type("M", (), {"content": text})()
        self.choices = [type("C", (), {"message": message})()]
        self.usage = usage


class StubClient:
    """Mimics the SDK surface the adapter touches. No network."""

    def __init__(self, *, response=None, error=None):
        self._response = response
        self._error = error
        self.chat = type("Chat", (), {"completions": self})()

    def create(self, **kwargs):
        if self._error:
            raise self._error
        return self._response


class RateLimitError(Exception):
    status_code = 429


class APITimeoutError(Exception):
    pass


def test_a_successful_call_maps_to_llm_response():
    stub = StubClient(response=StubResponse("the answer", StubUsage(120, 45)))
    adapter = GroqAdapter(client=stub)

    resp = adapter.complete(model="llama-3.1-8b-instant", prompt="q", max_tokens=100)

    assert resp.provider == "groq"
    assert resp.model == "llama-3.1-8b-instant"
    assert resp.text == "the answer"
    assert resp.tokens_in == 120
    assert resp.tokens_out == 45


def test_missing_usage_raises_rather_than_inventing_zero():
    """A call with no token counts cannot be priced honestly."""
    stub = StubClient(response=StubResponse("hi", usage=None))
    adapter = GroqAdapter(client=stub)

    with pytest.raises(ProviderError, match="usage"):
        adapter.complete(model="m", prompt="q", max_tokens=10)


def test_rate_limit_is_flagged_in_the_message():
    stub = StubClient(error=RateLimitError("too many requests"))
    adapter = GroqAdapter(client=stub)

    with pytest.raises(ProviderError) as exc:
        adapter.complete(model="m", prompt="q", max_tokens=10)

    assert exc.value.kind == "provider_error"
    assert "rate_limit:" in str(exc.value)


def test_timeout_maps_to_the_timeout_kind():
    stub = StubClient(error=APITimeoutError("deadline exceeded"))
    adapter = GroqAdapter(client=stub)

    with pytest.raises(ProviderError) as exc:
        adapter.complete(model="m", prompt="q", max_tokens=10)

    assert exc.value.kind == "timeout"


def test_generic_failure_maps_to_provider_error():
    stub = StubClient(error=RuntimeError("something broke"))
    adapter = GroqAdapter(client=stub)

    with pytest.raises(ProviderError) as exc:
        adapter.complete(model="m", prompt="q", max_tokens=10)

    assert exc.value.kind == "provider_error"


def test_unexpected_response_shape_is_reported():
    stub = StubClient(response=StubResponse("x", StubUsage(1, 1)))
    stub._response.choices = []
    adapter = GroqAdapter(client=stub)

    with pytest.raises(ProviderError, match="unexpected response shape"):
        adapter.complete(model="m", prompt="q", max_tokens=10)


def test_no_key_and_no_client_is_refused():
    with pytest.raises(ValueError, match="api_key"):
        GroqAdapter()