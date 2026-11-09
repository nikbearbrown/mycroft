"""Downloader tests: the resume and retry behaviour plan.md Week 2 asks for.

These use a local HTTP server rather than the SEC, so they are fast, offline,
and can produce the failures that matter -- a dropped connection mid-stream, and
a server that ignores a Range request. Both are real and neither is reproducible
on demand against sec.gov.
"""

import http.server
import io
import socket
import threading
import zipfile
from pathlib import Path

import pytest
import requests

import src.ingest.download_bulk as dl


def make_zip(members=20, size=4096) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for i in range(members):
            zf.writestr(f"FILE_{i}.tsv", b"x" * size)
    return buf.getvalue()


PAYLOAD = make_zip()


class Handler(http.server.BaseHTTPRequestHandler):
    """Serves PAYLOAD. Behaviour is driven by class attributes per test."""

    ignore_range = False      # answer 200 with the whole body even if asked for a range
    truncate_after = None     # bytes to send before hanging up
    fail_times = 0            # answer 500 this many times first
    not_found = False         # answer 404, as the SEC does for an unpublished quarter
    hits = 0                  # how many requests reached the server

    def log_message(self, *args):
        pass

    def do_GET(self):
        cls = type(self)
        cls.hits += 1
        if cls.not_found:
            self.send_error(404, "not published")
            return
        if cls.fail_times > 0:
            cls.fail_times -= 1
            self.send_error(500, "transient")
            return

        start = 0
        rng = self.headers.get("Range")
        if rng and not cls.ignore_range:
            start = int(rng.split("=")[1].split("-")[0])
            body = PAYLOAD[start:]
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{len(PAYLOAD)-1}/{len(PAYLOAD)}")
        else:
            body = PAYLOAD
            self.send_response(200)

        if cls.truncate_after is not None:
            # Advertise the full length, then send less and close: the exact
            # shape of a connection dropped mid-transfer.
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body[: cls.truncate_after])
            return

        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@pytest.fixture
def server():
    Handler.ignore_range = False
    Handler.truncate_after = None
    Handler.fail_times = 0
    Handler.not_found = False
    Handler.hits = 0
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    srv = http.server.HTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{port}"
    srv.shutdown()


@pytest.fixture
def sandbox(tmp_path, server, monkeypatch):
    monkeypatch.setattr(dl, "DATA_DIR", tmp_path)
    monkeypatch.setattr(dl, "BASE", server)
    monkeypatch.setattr(dl, "user_agent", lambda: "Test test@example.edu")
    monkeypatch.setattr(dl.time, "sleep", lambda s: None)  # no real backoff waits
    return tmp_path


def test_downloads_and_verifies(sandbox):
    path = dl.download("2099q1")
    assert path.read_bytes() == PAYLOAD
    dl.verify_zip(path)


def test_second_call_is_a_no_op(sandbox):
    first = dl.download("2099q1")
    mtime = first.stat().st_mtime_ns
    again = dl.download("2099q1")
    assert again == first and again.stat().st_mtime_ns == mtime


def test_resumes_from_a_partial_file(sandbox):
    partial = sandbox / "2099q1_nport.zip.part"
    half = len(PAYLOAD) // 2
    partial.write_bytes(PAYLOAD[:half])
    path = dl.download("2099q1")
    assert path.read_bytes() == PAYLOAD, "resumed file does not match the original"


def test_range_ignored_by_server_does_not_corrupt(sandbox):
    """The latent bug: appending a 200 response onto existing bytes yields an
    archive of the wrong length that still looks finished."""
    Handler.ignore_range = True
    partial = sandbox / "2099q1_nport.zip.part"
    partial.write_bytes(PAYLOAD[: len(PAYLOAD) // 2])
    path = dl.download("2099q1")
    assert path.read_bytes() == PAYLOAD
    assert len(path.read_bytes()) == len(PAYLOAD), "bytes were appended, not restarted"


def test_retries_a_transient_failure(sandbox):
    Handler.fail_times = 2
    path = dl.download("2099q1", attempts=4)
    assert path.read_bytes() == PAYLOAD


def test_gives_up_after_the_attempt_budget(sandbox):
    Handler.fail_times = 99
    with pytest.raises(SystemExit):
        dl.download("2099q1", attempts=2)


def test_does_not_retry_a_404(sandbox):
    """2026Q3 returns 404 because the SEC has not published it. Asking four more
    times is just noise -- the answer is correct and will not change."""
    Handler.not_found = True
    with pytest.raises(requests.HTTPError):
        dl.download("2099q1", attempts=4)
    assert Handler.hits == 1, f"a 404 was retried; server saw {Handler.hits} requests"
    assert not (sandbox / "2099q1_nport.zip").exists()


def test_does_retry_a_500(sandbox):
    """The contrast with the 404 case: a 5xx is worth asking again."""
    Handler.fail_times = 2
    dl.download("2099q1", attempts=4)
    assert Handler.hits == 3, f"expected 2 failures then a success, saw {Handler.hits}"


def test_truncated_transfer_is_caught(sandbox):
    """A short read must fail loudly, not rename a half file into place."""
    Handler.truncate_after = len(PAYLOAD) // 3
    with pytest.raises(SystemExit):
        dl.download("2099q1", attempts=2)
    assert not (sandbox / "2099q1_nport.zip").exists()


def test_verify_zip_rejects_a_truncated_archive(tmp_path):
    bad = tmp_path / "bad.zip"
    bad.write_bytes(PAYLOAD[: len(PAYLOAD) // 2])
    with pytest.raises(zipfile.BadZipFile):
        dl.verify_zip(bad)
