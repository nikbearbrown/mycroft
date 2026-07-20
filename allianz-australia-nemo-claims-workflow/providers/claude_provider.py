"""
providers/claude_provider.py

Anthropic adapter. Translates the shared output_schema (JSON Schema) into
a forced tool-use call, since Claude's structured-output mechanism is
tool use, not a JSON-mode flag.

VERIFICATION STATUS: design-complete, syntax-verified only. This adapter
has not been exercised against a live Anthropic API call in this build
environment (no network access). Runtime-verify this first if you're
setting NEMO_PROVIDER=claude — see README.md, "Provider Verification
Status".
"""

import json

from providers.base import LLMProvider, StructuredResponse, ProviderResponseError


class ClaudeProvider(LLMProvider):

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        # [DEV] Import is deferred to __init__, not module level, so this
        # file can be imported (e.g. by tests using FakeProvider instead)
        # without requiring the anthropic package to be installed.
        import anthropic
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def complete_structured(self, system_prompt, user_message, output_schema, max_tokens) -> StructuredResponse:
        tool_name = "emit_structured_output"
        tool_def = {
            "name": tool_name,
            "description": "Emit the structured result for this task.",
            "input_schema": output_schema,
        }

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                tools=[tool_def],
                tool_choice={"type": "tool", "name": tool_name},
            )
        except Exception as e:
            raise ProviderResponseError("claude", f"API call failed: {e}")

        tool_use_block = next(
            (block for block in response.content if getattr(block, "type", None) == "tool_use"),
            None,
        )
        if tool_use_block is None:
            raise ProviderResponseError("claude", "No tool_use block in response — model did not emit structured output.")

        return StructuredResponse(
            data=tool_use_block.input,
            raw_text=json.dumps(tool_use_block.input),
            provider_name="claude",
        )
