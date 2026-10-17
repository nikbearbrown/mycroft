"""A minimal Ollama client, and a stub that stands in for it in tests.

Two backends behind one interface:

  OllamaBackend   POSTs to a local Ollama server's /api/chat
  StubBackend     returns canned replies, so the whole adjudication layer --
                  prompt construction, schema validation, the refusal path --
                  is testable without a 5 GB model on disk

--------------------------------------------------------------------------
Why requests and not the `ollama` package
--------------------------------------------------------------------------
plan.md pins `ollama==0.4.5`. This uses `requests`, which is already a
dependency, against the same HTTP API. The surface needed here is one POST to
one endpoint; a package whose whole job is to wrap that endpoint is a
dependency without a job. It also means `OLLAMA_HOST` can point at any
server -- another machine, a container -- without a code change.

--------------------------------------------------------------------------
Determinism
--------------------------------------------------------------------------
`temperature: 0` and a fixed `seed`. A model that answers differently on two
runs cannot be measured against a fixed golden set, and a metric that moves
when nothing changed is not a metric. Ollama still does not guarantee
bit-identical output across model or runtime versions, so the model name and
digest are recorded with every result -- see scripts/run_adjudication.py.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field

import requests

DEFAULT_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")

# Long, because a cold model load on a laptop GPU is slow and a timeout in the
# middle of a 300-row run would poison the throughput measurement.
LOAD_TIMEOUT = 600
CALL_TIMEOUT = 120


class BackendError(RuntimeError):
    """The backend could not be reached, or answered something unusable."""


@dataclass
class Reply:
    """One model response, with the numbers a throughput budget needs."""

    text: str
    seconds: float
    prompt_tokens: int = 0
    completion_tokens: int = 0
    model: str = ""

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class OllamaBackend:
    """Chat completion against a local Ollama server."""

    def __init__(self, model: str = DEFAULT_MODEL, host: str = DEFAULT_HOST,
                 schema: dict | None = None):
        self.model = model
        self.host = host.rstrip("/")
        self.schema = schema

    # -- introspection, so a run can record what actually answered it -------

    def available(self) -> bool:
        try:
            requests.get(f"{self.host}/api/tags", timeout=5).raise_for_status()
            return True
        except Exception:
            return False

    def installed_models(self) -> list:
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=10)
            response.raise_for_status()
            return [m["name"] for m in response.json().get("models", [])]
        except Exception as exc:  # pragma: no cover - network shape
            raise BackendError(f"cannot list models on {self.host}: {exc}") from exc

    def describe(self) -> dict:
        """Model identity, recorded beside every result so a number is traceable."""
        try:
            response = requests.post(
                f"{self.host}/api/show", json={"model": self.model}, timeout=30
            )
            response.raise_for_status()
            body = response.json()
            details = body.get("details", {})
            digest = body.get("digest") or ""
            if not digest:
                # /api/show omits the digest on some builds. It is the one field
                # that pins *which* weights answered, so fall back to the tag
                # listing rather than record a result no one can reproduce.
                tags = requests.get(f"{self.host}/api/tags", timeout=10).json()
                digest = next(
                    (m.get("digest", "") for m in tags.get("models", [])
                     if m.get("name") == self.model),
                    "",
                )
            return {
                "model": self.model,
                "digest": digest[:16],
                "parameter_size": details.get("parameter_size"),
                "quantization": details.get("quantization_level"),
                "family": details.get("family"),
            }
        except Exception as exc:  # pragma: no cover - network shape
            raise BackendError(f"cannot describe {self.model}: {exc}") from exc

    # -- the one call that matters -----------------------------------------

    def chat(self, system: str, user: str) -> Reply:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {"temperature": 0, "seed": 7, "num_predict": 400},
        }
        # Newer Ollama accepts a JSON Schema here and constrains decoding to it.
        # Older builds only understand the string "json". Either is better than
        # parsing prose, so send the schema and fall back rather than fail.
        payload["format"] = self.schema if self.schema else "json"

        started = time.perf_counter()
        try:
            response = requests.post(
                f"{self.host}/api/chat", json=payload, timeout=CALL_TIMEOUT
            )
            if response.status_code == 400 and self.schema:
                payload["format"] = "json"
                response = requests.post(
                    f"{self.host}/api/chat", json=payload, timeout=CALL_TIMEOUT
                )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise BackendError(f"{self.model} on {self.host}: {exc}") from exc
        elapsed = time.perf_counter() - started

        body = response.json()
        return Reply(
            text=body.get("message", {}).get("content", ""),
            seconds=elapsed,
            prompt_tokens=body.get("prompt_eval_count", 0),
            completion_tokens=body.get("eval_count", 0),
            model=self.model,
        )

    def warm(self) -> float:
        """Load the model into VRAM and return how long it took.

        Kept separate from chat() so the first call's model-load cost does not
        land inside the throughput measurement and make the model look four
        times slower than it is.
        """
        started = time.perf_counter()
        try:
            requests.post(
                f"{self.host}/api/chat",
                json={"model": self.model, "messages": [{"role": "user", "content": "ok"}],
                      "stream": False, "options": {"num_predict": 1}},
                timeout=LOAD_TIMEOUT,
            ).raise_for_status()
        except requests.RequestException as exc:
            raise BackendError(f"cannot load {self.model}: {exc}") from exc
        return time.perf_counter() - started


@dataclass
class StubBackend:
    """A scripted backend. Tests use it; nothing else should.

    `replies` maps a substring of the user prompt to the raw text to return.
    Anything unmatched gets `default`, which defaults to a well-formed refusal
    -- so a test that forgets to script a case fails on the assertion it cares
    about rather than on a parse error.
    """

    replies: dict = field(default_factory=dict)
    default: str = '{"company": "UNKNOWN", "share_class": "UNKNOWN", ' \
                   '"confidence": 0.0, "reason": "unscripted"}'
    calls: list = field(default_factory=list)
    model: str = "stub"

    def available(self) -> bool:
        return True

    def describe(self) -> dict:
        return {"model": "stub", "digest": "stub", "parameter_size": None,
                "quantization": None, "family": "stub"}

    def warm(self) -> float:
        return 0.0

    def chat(self, system: str, user: str) -> Reply:
        self.calls.append({"system": system, "user": user})
        for needle, text in self.replies.items():
            if needle in user:
                return Reply(text=text, seconds=0.0, model="stub")
        return Reply(text=self.default, seconds=0.0, model="stub")


def load_backend(model: str | None = None, host: str | None = None,
                 schema: dict | None = None):
    """The backend named by the environment, or an explicit override."""
    return OllamaBackend(
        model=model or DEFAULT_MODEL, host=host or DEFAULT_HOST, schema=schema
    )


def parse_json_object(text: str) -> dict:
    """Pull the first JSON object out of a model reply.

    Models wrap JSON in prose and fences even when told not to, and a run that
    dies on the one row where that happened has thrown away the other 321. The
    brace-scan is a fallback, not a licence: anything it recovers is still
    schema-validated by the caller.
    """
    text = (text or "").strip()
    if not text:
        raise ValueError("empty reply")
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    depth, start = 0, None
    for i, char in enumerate(text):
        if char == "{":
            if depth == 0:
                start = i
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    parsed = json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    start = None
                    continue
                if isinstance(parsed, dict):
                    return parsed
    raise ValueError(f"no JSON object in reply: {text[:120]!r}")
