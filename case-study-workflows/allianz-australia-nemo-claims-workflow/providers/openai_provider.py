"""
providers/openai_provider.py

OpenAI adapter. Uses OpenAI's structured-outputs response_format with the
shared JSON Schema directly — this is the provider where the shared schema
convention maps most directly onto the native mechanism.

VERIFICATION STATUS: design-complete, syntax-verified only. This adapter
has not been exercised against a live OpenAI API call in this build
environment (no network access). Runtime-verify this first if you're
setting NEMO_PROVIDER=openai — see README.md, "Provider Verification
Status".
"""

import json

from providers.base import LLMProvider, StructuredResponse, ProviderResponseError


class OpenAIProvider(LLMProvider):

    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        # [DEV] Deferred import — see claude_provider.py for why.
        import openai
        self._client = openai.OpenAI(api_key=api_key)
        self._model = model

    def complete_structured(self, system_prompt, user_message, output_schema, max_tokens) -> StructuredResponse:
        # [DEV] OpenAI's structured-outputs feature requires
        # "additionalProperties": false on the schema object to guarantee
        # strict adherence. Adding it here rather than requiring every
        # agent's schema to remember to include a provider-specific field.
        strict_schema = dict(output_schema)
        strict_schema.setdefault("additionalProperties", False)

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "structured_output",
                        "schema": strict_schema,
                        "strict": True,
                    },
                },
            )
        except Exception as e:
            raise ProviderResponseError("openai", f"API call failed: {e}")

        raw_text = response.choices[0].message.content
        try:
            data = json.loads(raw_text)
        except (json.JSONDecodeError, TypeError) as e:
            raise ProviderResponseError("openai", f"Response was not valid JSON: {e}")

        return StructuredResponse(data=data, raw_text=raw_text, provider_name="openai")
