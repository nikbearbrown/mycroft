"""
WHAT THIS FILE DOES: Translates the shared LLMProvider interface into a call
against Anthropic's Claude API and normalizes the response back to plain
text. All Claude-specific request/response detail lives here and nowhere
else in the pipeline.
"""
from llm_provider.base import LLMProvider


class ClaudeAdapter(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-5"):
        self._api_key = api_key
        self._model = model

    def call(self, instruction: str, input_text: str) -> str:
        import requests  # imported here so this dependency is only needed
                          # when a real provider is actually selected

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self._model,
                "max_tokens": 500,
                "system": instruction,
                "messages": [{"role": "user", "content": input_text}],
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return "".join(
            block.get("text", "")
            for block in data.get("content", [])
            if block.get("type") == "text"
        )
