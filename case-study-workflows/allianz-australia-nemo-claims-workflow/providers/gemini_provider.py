"""
providers/gemini_provider.py

Gemini adapter. Uses Gemini's response_schema / response_mime_type
GenerationConfig fields to enforce structured output.

VERIFICATION STATUS: design-complete, syntax-verified only. This adapter
has not been exercised against a live Gemini API call in this build
environment (no network access). Runtime-verify this first if you're
setting NEMO_PROVIDER=gemini — see README.md, "Provider Verification
Status".
"""

import json

from providers.base import LLMProvider, StructuredResponse, ProviderResponseError


class GeminiProvider(LLMProvider):

    def __init__(self, api_key: str, model: str = "gemini-2.5-pro"):
        # [DEV] Deferred import — see claude_provider.py for why.
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self._genai = genai
        self._model_name = model

    def complete_structured(self, system_prompt, user_message, output_schema, max_tokens) -> StructuredResponse:
        model = self._genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=system_prompt,
        )

        # [DEV] Gemini's response_schema does not accept every JSON Schema
        # keyword OpenAI/Claude tolerate (e.g. it's stricter about
        # "additionalProperties" and some "enum" placements). If an
        # agent's schema starts failing only on this adapter, that's the
        # first thing to check — translate the shared schema here rather
        # than changing the agent's schema to be Gemini-specific.
        generation_config = {
            "max_output_tokens": max_tokens,
            "response_mime_type": "application/json",
            "response_schema": output_schema,
        }

        try:
            response = model.generate_content(
                user_message,
                generation_config=generation_config,
            )
        except Exception as e:
            raise ProviderResponseError("gemini", f"API call failed: {e}")

        raw_text = response.text
        try:
            data = json.loads(raw_text)
        except (json.JSONDecodeError, TypeError) as e:
            raise ProviderResponseError("gemini", f"Response was not valid JSON: {e}")

        return StructuredResponse(data=data, raw_text=raw_text, provider_name="gemini")
