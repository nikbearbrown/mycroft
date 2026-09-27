"""
WHAT THIS FILE DOES: Translates the shared LLMProvider interface into a call
against OpenAI's API and normalizes the response back to plain text. All
GPT-specific request/response detail lives here and nowhere else in the
pipeline.
"""
from llm_provider.base import LLMProvider


class GPTAdapter(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-5"):
        self._api_key = api_key
        self._model = model

    def call(self, instruction: str, input_text: str) -> str:
        import requests

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self._model,
                "messages": [
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": input_text},
                ],
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
