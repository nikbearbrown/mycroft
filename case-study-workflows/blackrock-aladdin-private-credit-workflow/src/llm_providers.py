"""
LLM Provider Abstraction

Only two pipeline components call an LLM directly: the Orchestrator and the
Synthesis module. Both are written against LLMProvider, never against a
vendor SDK directly, so the underlying model can be swapped without touching
any pipeline logic (this is architecture principle 3 from this repo's /v2
design doc).

All three providers below are real implementations, not stubs — deliberately,
because not every learner forking this repo defaults to the same LLM vendor.
Provider selection happens at runtime (see build_provider), not by editing
this file.

Honest caveat: these reflect each provider's SDK call shape as of early 2026.
SDKs change method signatures between versions more often than the underlying
concepts change. If a call fails with an attribute or method error, check that
provider's current docs — the shape of complete() won't need to change, just
the internals of whichever provider broke.

Imports for each vendor SDK happen inside that provider's __init__, not at
module load time — so you only need the one package for the provider you're
actually using, not all three.
"""
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str, system: str = "", max_tokens: int = 1024) -> str:
        """Single-shot text completion. No streaming, no tool-use — this
        pipeline's LLM calls are parse-or-synthesize, not agentic loops."""
        raise NotImplementedError


class ClaudeProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def complete(self, prompt: str, system: str = "", max_tokens: int = 1024) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def complete(self, prompt: str, system: str = "", max_tokens: int = 1024) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages,
        )
        return response.choices[0].message.content


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        from google import genai
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def complete(self, prompt: str, system: str = "", max_tokens: int = 1024) -> str:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = self.client.models.generate_content(
            model=self.model,
            contents=full_prompt,
        )
        return response.text


def build_provider(name: str, api_key: str) -> LLMProvider:
    """Runtime provider selection — swap providers via config/env var, never
    by editing this file. name is one of 'claude', 'openai', 'gemini'."""
    providers = {
        "claude": ClaudeProvider,
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
    }
    if name not in providers:
        raise ValueError(f"Unknown provider '{name}'. Choose from: {list(providers)}")
    return providers[name](api_key=api_key)
