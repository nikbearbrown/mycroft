"""
Ollama adapter — wraps a locally running Ollama instance to satisfy the
accountability layer contract.

No external dependencies. Uses stdlib urllib only.

Requires: Ollama running at OLLAMA_HOST (default: http://localhost:11434)
Requires: the requested model already pulled  (ollama pull llama3.2)

Determinism guarantee:
  Ollama respects `seed` + `temperature=0` within a fixed model version and
  quantisation level. Results are NOT guaranteed to be byte-identical across:
    - model version upgrades
    - quantisation changes (e.g. Q4_K_M → Q8_0)
    - Ollama version upgrades that change sampling internals
  The seed and model name are stored on every run record so the exact conditions
  can be reconstructed for audit purposes even if the environment has changed.

ADR-10: SQLite prototype. ADR-11: directive v1.1.0 mechanical enforcement.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from parser import AgentResponse, _parse_response
from directive import DirectiveVersion


OLLAMA_HOST        = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
_GENERATE_ENDPOINT = f"{OLLAMA_HOST}/api/generate"
_TIMEOUT_S         = 120   # local model inference can be slow on CPU
CONTEXT_CHAR_LIMIT = 6_000  # conservative — protects sub-8k-context models like qwen2.5:3b


class OllamaConnectionError(Exception):
    """Ollama is not reachable at OLLAMA_HOST."""


class OllamaModelError(Exception):
    """Model not found or not pulled on the local Ollama instance."""


# ── Adapter factory ───────────────────────────────────────────────────────────

def make_ollama_adapter(
    model: str = "llama3.2",
    temperature: float = 0.0,
    seed: int = 42,
):
    """
    Returns a call_agent_fn compatible with run_validation_loop.

    temperature=0.0 + fixed seed → deterministic output within a model version.
    Set temperature > 0 to allow variation (loses determinism guarantee).

    Raises:
        OllamaConnectionError — Ollama not running or wrong host
        OllamaModelError      — model not pulled locally
    """

    def adapter(subject: str, context: str, directive: DirectiveVersion) -> AgentResponse:
        # Build the prompt — same structure as Gemini adapter
        prompt = f"Subject: {subject}"
        if context and context.strip():
            truncated = context[:CONTEXT_CHAR_LIMIT]
            prompt += f"\n\nContext:\n{truncated}"

        payload = {
            "model":  model,
            "prompt": prompt,
            "system": directive.text,   # directive injected as system prompt (ADR-01b)
            "stream": False,
            "options": {
                "temperature": temperature,
                "seed":        seed,
            },
        }

        body = json.dumps(payload).encode("utf-8")
        req  = urllib.request.Request(
            _GENERATE_ENDPOINT,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise OllamaConnectionError(
                f"Cannot reach Ollama at {OLLAMA_HOST}. "
                f"Is Ollama running? Check: ollama serve\n"
                f"Original error: {exc}"
            ) from exc

        # Ollama returns {"error": "..."} on model-not-found
        if "error" in data:
            err = data["error"]
            if "not found" in err.lower() or "pull" in err.lower():
                raise OllamaModelError(
                    f"Model '{model}' not found locally. "
                    f"Pull it first: ollama pull {model}\n"
                    f"Ollama error: {err}"
                )
            raise RuntimeError(f"Ollama error: {err}")

        raw_text = data.get("response", "")
        return _parse_response(raw_text)

    return adapter
