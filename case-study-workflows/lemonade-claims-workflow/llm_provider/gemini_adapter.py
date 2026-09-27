"""
WHAT THIS FILE DOES: Translates the shared LLMProvider interface into a call
against Google's Gemini API and normalizes the response back to plain text.
All Gemini-specific request/response detail lives here and nowhere else in
the pipeline.
"""
from llm_provider.base import LLMProvider


class GeminiAdapter(LLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.5-pro"):
        self._api_key = api_key
        self._model = model

    def call(self, instruction: str, input_text: str) -> str:
        import requests

        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._model}:generateContent?key={self._api_key}",
            json={
                "system_instruction": {"parts": [{"text": instruction}]},
                "contents": [{"parts": [{"text": input_text}]}],
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
