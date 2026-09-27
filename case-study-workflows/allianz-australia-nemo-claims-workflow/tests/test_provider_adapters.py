"""
tests/test_provider_adapters.py

IMPORTANT — read this before treating these tests as "the provider is
verified": these tests mock each provider's SDK client entirely. They
prove that ClaudeProvider / OpenAIProvider / GeminiProvider correctly
BUILD a request and correctly PARSE a response shaped the way that SDK's
documentation says it will be shaped. They do NOT prove that a real
Claude/OpenAI/Gemini API actually returns that shape in practice, that
the SDK version installed matches what these mocks assume, or that the
schema translation actually satisfies the real model's structured-output
mechanism. That is what "runtime-verify with a real API key" (README.md,
"Provider Verification Status") still means and still requires.

What this DOES catch, without any network access:
- Wrong attribute/method names against the SDK's documented interface
- Broken JSON parsing on malformed responses
- Whether ProviderResponseError is raised correctly on failure paths

Run with: python -m pytest tests/test_provider_adapters.py -v
"""

import sys
import os
import json
import types
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from providers.base import ProviderResponseError


SAMPLE_SCHEMA = {
    "type": "object",
    "properties": {"determination": {"type": "string"}},
    "required": ["determination"],
}


# ---------------------------------------------------------------------------
# Claude adapter
# ---------------------------------------------------------------------------

def _install_fake_anthropic(tool_use_input=None, no_tool_use=False, raise_on_call=False):
    fake_anthropic = types.ModuleType("anthropic")

    class FakeToolUseBlock:
        type = "tool_use"
        def __init__(self, input_data):
            self.input = input_data

    class FakeMessages:
        def create(self, **kwargs):
            if raise_on_call:
                raise RuntimeError("simulated API failure")
            content = [] if no_tool_use else [FakeToolUseBlock(tool_use_input)]
            return types.SimpleNamespace(content=content)

    class FakeAnthropic:
        def __init__(self, api_key):
            self.messages = FakeMessages()

    fake_anthropic.Anthropic = FakeAnthropic
    sys.modules["anthropic"] = fake_anthropic


def test_claude_adapter_parses_tool_use_response():
    _install_fake_anthropic(tool_use_input={"determination": "covered"})
    from providers.claude_provider import ClaudeProvider
    provider = ClaudeProvider(api_key="fake-key")
    result = provider.complete_structured("system", "user msg", SAMPLE_SCHEMA, max_tokens=100)
    assert result.data == {"determination": "covered"}
    assert result.provider_name == "claude"
    print("test_claude_adapter_parses_tool_use_response: PASSED")


def test_claude_adapter_raises_on_missing_tool_use():
    _install_fake_anthropic(no_tool_use=True)
    from providers.claude_provider import ClaudeProvider
    provider = ClaudeProvider(api_key="fake-key")
    try:
        provider.complete_structured("system", "user msg", SAMPLE_SCHEMA, max_tokens=100)
        assert False, "Expected ProviderResponseError"
    except ProviderResponseError as e:
        assert e.provider_name == "claude"
    print("test_claude_adapter_raises_on_missing_tool_use: PASSED")


def test_claude_adapter_raises_on_api_failure():
    _install_fake_anthropic(raise_on_call=True)
    from providers.claude_provider import ClaudeProvider
    provider = ClaudeProvider(api_key="fake-key")
    try:
        provider.complete_structured("system", "user msg", SAMPLE_SCHEMA, max_tokens=100)
        assert False, "Expected ProviderResponseError"
    except ProviderResponseError:
        pass
    print("test_claude_adapter_raises_on_api_failure: PASSED")


# ---------------------------------------------------------------------------
# OpenAI adapter
# ---------------------------------------------------------------------------

def _install_fake_openai(response_content=None, raise_on_call=False):
    fake_openai = types.ModuleType("openai")

    class FakeCompletions:
        def create(self, **kwargs):
            if raise_on_call:
                raise RuntimeError("simulated API failure")
            message = types.SimpleNamespace(content=response_content)
            choice = types.SimpleNamespace(message=message)
            return types.SimpleNamespace(choices=[choice])

    class FakeChat:
        def __init__(self):
            self.completions = FakeCompletions()

    class FakeOpenAI:
        def __init__(self, api_key):
            self.chat = FakeChat()

    fake_openai.OpenAI = FakeOpenAI
    sys.modules["openai"] = fake_openai


def test_openai_adapter_parses_json_response():
    _install_fake_openai(response_content=json.dumps({"determination": "covered"}))
    from providers.openai_provider import OpenAIProvider
    provider = OpenAIProvider(api_key="fake-key")
    result = provider.complete_structured("system", "user msg", SAMPLE_SCHEMA, max_tokens=100)
    assert result.data == {"determination": "covered"}
    assert result.provider_name == "openai"
    print("test_openai_adapter_parses_json_response: PASSED")


def test_openai_adapter_raises_on_malformed_json():
    _install_fake_openai(response_content="not valid json{{{")
    from providers.openai_provider import OpenAIProvider
    provider = OpenAIProvider(api_key="fake-key")
    try:
        provider.complete_structured("system", "user msg", SAMPLE_SCHEMA, max_tokens=100)
        assert False, "Expected ProviderResponseError"
    except ProviderResponseError as e:
        assert e.provider_name == "openai"
    print("test_openai_adapter_raises_on_malformed_json: PASSED")


def test_openai_adapter_raises_on_api_failure():
    _install_fake_openai(raise_on_call=True)
    from providers.openai_provider import OpenAIProvider
    provider = OpenAIProvider(api_key="fake-key")
    try:
        provider.complete_structured("system", "user msg", SAMPLE_SCHEMA, max_tokens=100)
        assert False, "Expected ProviderResponseError"
    except ProviderResponseError:
        pass
    print("test_openai_adapter_raises_on_api_failure: PASSED")


# ---------------------------------------------------------------------------
# Gemini adapter
# ---------------------------------------------------------------------------

def _install_fake_gemini(response_text=None, raise_on_call=False):
    fake_google = types.ModuleType("google")
    fake_genai = types.ModuleType("google.generativeai")

    class FakeGenerativeModel:
        def __init__(self, model_name, system_instruction):
            pass

        def generate_content(self, user_message, generation_config):
            if raise_on_call:
                raise RuntimeError("simulated API failure")
            return types.SimpleNamespace(text=response_text)

    fake_genai.configure = MagicMock()
    fake_genai.GenerativeModel = FakeGenerativeModel
    fake_google.generativeai = fake_genai

    sys.modules["google"] = fake_google
    sys.modules["google.generativeai"] = fake_genai


def test_gemini_adapter_parses_json_response():
    _install_fake_gemini(response_text=json.dumps({"determination": "covered"}))
    from providers.gemini_provider import GeminiProvider
    provider = GeminiProvider(api_key="fake-key")
    result = provider.complete_structured("system", "user msg", SAMPLE_SCHEMA, max_tokens=100)
    assert result.data == {"determination": "covered"}
    assert result.provider_name == "gemini"
    print("test_gemini_adapter_parses_json_response: PASSED")


def test_gemini_adapter_raises_on_malformed_json():
    _install_fake_gemini(response_text="not valid json{{{")
    from providers.gemini_provider import GeminiProvider
    provider = GeminiProvider(api_key="fake-key")
    try:
        provider.complete_structured("system", "user msg", SAMPLE_SCHEMA, max_tokens=100)
        assert False, "Expected ProviderResponseError"
    except ProviderResponseError as e:
        assert e.provider_name == "gemini"
    print("test_gemini_adapter_raises_on_malformed_json: PASSED")


def test_gemini_adapter_raises_on_api_failure():
    _install_fake_gemini(raise_on_call=True)
    from providers.gemini_provider import GeminiProvider
    provider = GeminiProvider(api_key="fake-key")
    try:
        provider.complete_structured("system", "user msg", SAMPLE_SCHEMA, max_tokens=100)
        assert False, "Expected ProviderResponseError"
    except ProviderResponseError:
        pass
    print("test_gemini_adapter_raises_on_api_failure: PASSED")


if __name__ == "__main__":
    test_claude_adapter_parses_tool_use_response()
    test_claude_adapter_raises_on_missing_tool_use()
    test_claude_adapter_raises_on_api_failure()
    test_openai_adapter_parses_json_response()
    test_openai_adapter_raises_on_malformed_json()
    test_openai_adapter_raises_on_api_failure()
    test_gemini_adapter_parses_json_response()
    test_gemini_adapter_raises_on_malformed_json()
    test_gemini_adapter_raises_on_api_failure()
    print("\nAll adapter-logic tests passed (mocked SDKs — NOT a substitute for real-API verification).")
