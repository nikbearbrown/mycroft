"""
The model-call timeout (MODEL_TIMEOUT_S in adapters/langchain_adapter.py).

What this locks in
    - A model server that accepts the request and never answers — how Ollama hung
      during compares — ends the call with LangchainTimeoutError instead of blocking
      forever, on both the plain model call (the assessment extraction) and the agent
      adapter. LangchainTimeoutError is a LangchainConnectionError, so the routes'
      existing handler records the run as halted with the error.
    - It is a stall limit, not a cap on a call's length: a server that streams slowly
      but steadily, for longer than the limit in total, still succeeds.
    - A refused connection is still reported as unreachable, not as a timeout, and a
      timeout wrapped in another exception is still recognised as one.

No network and no model: a stub Ollama server on 127.0.0.1, with the real ChatOllama and
httpx client in front of it.
"""

from __future__ import annotations

import json
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

from adapters import langchain_adapter as la
from core.directive import get_active_directive

_ANSWER = "<thought_log>Step 1.</thought_log>\n<conclusion>The answer.</conclusion>"  # blocks on their own lines


def _chunk(content: str, done: bool) -> bytes:
    body = {"model": "llama3.2", "created_at": "2026-09-27T00:00:00Z",
            "message": {"role": "assistant", "content": content}, "done": done}
    if done:
        body["done_reason"] = "stop"
    return (json.dumps(body) + "\n").encode()


class _StubOllama:
    """mode "hang": read the request, never answer. mode "slow": stream the answer in
    pieces with `gap` seconds between them."""

    def __init__(self, mode: str, gap: float = 0.0, pieces: int = 1):
        stub = self
        self.release = threading.Event()

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *args):
                pass

            def do_POST(self):
                self.rfile.read(int(self.headers.get("Content-Length", 0)))
                if mode == "hang":
                    stub.release.wait(30)
                    return
                self.send_response(200)
                self.send_header("Content-Type", "application/x-ndjson")
                self.end_headers()
                step = -(-len(_ANSWER) // pieces)
                for i in range(0, len(_ANSWER), step):
                    time.sleep(gap)
                    self.wfile.write(_chunk(_ANSWER[i:i + step], False))
                    self.wfile.flush()
                self.wfile.write(_chunk("", True))

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()

    def close(self):
        self.release.set()
        self.server.shutdown()
        self.server.server_close()


class ModelTimeoutTest(unittest.TestCase):
    def _stub(self, *args, **kwargs) -> _StubOllama:
        stub = _StubOllama(*args, **kwargs)
        self.addCleanup(stub.close)
        return stub

    def _patched(self, host: str, timeout: float):
        p = patch.multiple(la, OLLAMA_HOST=host, MODEL_TIMEOUT_S=timeout)
        p.start()
        self.addCleanup(p.stop)

    def test_a_silent_model_ends_the_extraction_call_with_a_timeout(self):
        self._patched(self._stub("hang").url, 0.3)
        started = time.monotonic()
        with self.assertRaises(la.LangchainTimeoutError) as caught:
            la.make_langchain_model_call()("system", "user")
        self.assertLess(time.monotonic() - started, 10)
        self.assertIsInstance(caught.exception, la.LangchainConnectionError)
        self.assertIn("sent nothing for 0.3 s", str(caught.exception))

    def test_a_silent_model_ends_the_agent_call_with_a_timeout(self):
        self._patched(self._stub("hang").url, 0.3)
        adapter = la.make_langchain_adapter(use_tools=False)
        started = time.monotonic()
        with self.assertRaises(la.LangchainTimeoutError):
            adapter("subject", "", get_active_directive())
        self.assertLess(time.monotonic() - started, 10)

    def test_a_slow_steady_stream_longer_than_the_limit_still_succeeds(self):
        self._patched(self._stub("slow", gap=0.12, pieces=6).url, 0.4)
        adapter = la.make_langchain_adapter(use_tools=False)
        started = time.monotonic()
        response = adapter("subject", "", get_active_directive())
        self.assertGreater(time.monotonic() - started, 0.4)  # longer than the limit in total
        self.assertEqual(response.conclusion, "The answer.")

    def test_a_refused_connection_is_unreachable_not_a_timeout(self):
        # httpx's own error, built directly: a real refused socket costs seconds on Windows.
        import httpx
        err = la._connection_error("llama3.2", httpx.ConnectError("[WinError 10061] refused"))
        self.assertNotIsInstance(err, la.LangchainTimeoutError)
        self.assertIn("Cannot reach model", str(err))

    def test_a_timeout_wrapped_in_another_error_is_still_a_timeout(self):
        import httpx
        try:
            try:
                raise httpx.ReadTimeout("timed out")
            except httpx.ReadTimeout as inner:
                raise RuntimeError("wrapped") from inner
        except RuntimeError as outer:
            self.assertIsInstance(la._connection_error("llama3.2", outer), la.LangchainTimeoutError)

    def test_the_limit_reaches_the_ollama_client(self):
        self._patched("http://127.0.0.1:1", 42)
        chat = la._build_chat("llama3.2", 0.0, 42)
        self.assertEqual(chat.client_kwargs, {"timeout": 42})


if __name__ == "__main__":
    unittest.main()
