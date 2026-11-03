"""
INGEST (ingest.py): SEC fair-access rules, provenance, and checkpoint/resume.

What is pinned here:
  - no request is made without SEC_USER_AGENT carrying a name and a contact email, and the
    header is actually sent (with Accept-Encoding);
  - the client never exceeds the configured rate, and any rate >= SEC's 10/s is refused;
  - ZIP URLs come from SEC's data-set page (both hosting-folder styles), not from a pattern;
  - manifest.json carries the SHA-256 and the fields DATA_CONTRACT.md names, and neither the
    manifest nor request_log.jsonl stores the User-Agent value (it holds a personal email);
  - a complete quarter is skipped with zero requests; a corrupted one is re-downloaded; an
    interrupted, truncated, or non-ZIP download leaves no file behind;
  - 403/429 back off and then halt, never retry in a tight loop;
  - G1 (`verify`) fails on a hash mismatch, too-fast request spacing, or an unhandled refusal;
  - unsafe ZIP member paths are refused at extraction.

No network: the HTTP opener, the clock and sleep are injected. Fixtures are in tests/fixtures/
(see its README for provenance).
"""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import ingest  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
PAGE_HTML = (FIXTURES / "sec_insider_dataset_page_trimmed.html").read_bytes()
ZIP_BYTES = (FIXTURES / "form345_header_only.zip").read_bytes()
ZIP_SHA = hashlib.sha256(ZIP_BYTES).hexdigest()

UA = "Test Fellow test.fellow@example.org"
URL_2026Q3 = ("https://www.sec.gov/files/datastandardsinnovation/data/"
              "insider-transactions-data-sets/2026q3_form345.zip")
URL_2026Q2 = ("https://www.sec.gov/files/structureddata/data/"
              "insider-transactions-data-sets/2026q2_form345.zip")


class FakeResponse:
    def __init__(self, status=200, body=b"", headers=None, fail_after=None):
        self.status = status
        self.headers = dict(headers or {})
        self._buf = io.BytesIO(body)
        self._fail_after = fail_after
        self._read = 0
        self.closed = False

    def read(self, n=-1):
        if self._fail_after is not None and self._read >= self._fail_after:
            raise ConnectionResetError("connection dropped mid-download")
        data = self._buf.read(n if self._fail_after is None else min(n, self._fail_after))
        self._read += len(data)
        return data

    def close(self):
        self.closed = True


class FakeSec:
    """Scripted opener: url -> list of responses, consumed in order. Records every call."""

    def __init__(self, routes):
        self.routes = {url: list(resps) for url, resps in routes.items()}
        self.calls: list[tuple[str, dict]] = []

    def __call__(self, url, headers, timeout):
        self.calls.append((url, dict(headers)))
        queue = self.routes.get(url)
        if not queue:
            return FakeResponse(404)
        return queue.pop(0) if len(queue) > 1 else queue[0]


class FakeClock:
    """Monotonic clock + sleep + wall clock that only move when sleep() is called."""

    def __init__(self):
        self.t = 0.0
        self.sleeps: list[float] = []
        self.epoch = datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc)

    def monotonic(self):
        return self.t

    def sleep(self, dt):
        self.sleeps.append(dt)
        self.t += dt

    def now(self):
        return self.epoch + timedelta(seconds=self.t)


def page():
    return FakeResponse(200, PAGE_HTML, {"Content-Type": "text/html"})


def zip_resp(body=ZIP_BYTES, **kw):
    return FakeResponse(200, body, {"Content-Length": str(len(body))}, **kw)


class IngestTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.data = self.tmp / "form345"
        self.clock = FakeClock()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def client(self, sec, rate=1.0):
        return ingest.SecClient(UA, rate, self.data / ingest.REQUEST_LOG_NAME, opener=sec,
                                clock=self.clock.monotonic, sleep=self.clock.sleep,
                                now=self.clock.now)

    def log_lines(self):
        path = self.data / ingest.REQUEST_LOG_NAME
        return [json.loads(l) for l in path.read_text().splitlines()] if path.exists() else []


class TestUserAgent(unittest.TestCase):
    def test_missing_is_refused(self):
        for env in ({}, {"SEC_USER_AGENT": ""}, {"SEC_USER_AGENT": "   "}):
            with self.assertRaises(ingest.ConfigError):
                ingest.require_user_agent(env)

    def test_without_email_is_refused(self):
        with self.assertRaises(ingest.ConfigError):
            ingest.require_user_agent({"SEC_USER_AGENT": "Test Fellow"})

    def test_email_only_is_refused(self):
        with self.assertRaises(ingest.ConfigError):
            ingest.require_user_agent({"SEC_USER_AGENT": "test.fellow@example.org"})

    def test_name_and_email_accepted(self):
        self.assertEqual(ingest.require_user_agent({"SEC_USER_AGENT": f"  {UA} "}), UA)

    def test_main_makes_no_request_without_user_agent(self):
        calls = []
        orig = ingest._default_open
        ingest._default_open = lambda *a, **k: calls.append(a)  # would record any request
        try:
            with tempfile.TemporaryDirectory() as d:
                code = ingest.main(["--quarters", "2026q3", "--data-dir", d], env={})
        finally:
            ingest._default_open = orig
        self.assertEqual(code, 2)
        self.assertEqual(calls, [])


class TestRate(IngestTestCase):
    def test_rates_at_or_above_sec_limit_refused(self):
        for bad in (10, 10.0, 25, 0, -1):
            with self.assertRaises(ingest.ConfigError):
                ingest.check_rate(bad)

    def test_main_refuses_rate_10(self):
        code = ingest.main(["--quarters", "2026q3", "--rate", "10", "--data-dir", str(self.data)],
                           env={"SEC_USER_AGENT": UA})
        self.assertEqual(code, 2)

    def test_requests_are_spaced_by_the_interval(self):
        sec = FakeSec({"https://example.test/a": [FakeResponse(200, b"x")]})
        client = self.client(sec, rate=1.0)
        for _ in range(4):
            client.get("https://example.test/a").close()
        starts = [ingest._parse_ts(r["ts"]) for r in self.log_lines()]
        gaps = [(b - a).total_seconds() for a, b in zip(starts, starts[1:])]
        self.assertEqual(len(gaps), 3)
        self.assertTrue(all(g >= 1.0 - 1e-9 for g in gaps), gaps)
        self.assertEqual(len(self.clock.sleeps), 3)             # the first request does not wait

    def test_half_rate_doubles_the_interval(self):
        sec = FakeSec({"https://example.test/a": [FakeResponse(200, b"x")]})
        client = self.client(sec, rate=0.5)
        client.get("https://example.test/a").close()
        client.get("https://example.test/a").close()
        self.assertEqual(self.clock.sleeps, [2.0])

    def test_headers_sent(self):
        sec = FakeSec({"https://example.test/a": [FakeResponse(200, b"x")]})
        self.client(sec).get("https://example.test/a").close()
        _, headers = sec.calls[0]
        self.assertEqual(headers["User-Agent"], UA)
        self.assertIn("gzip", headers["Accept-Encoding"])


class TestQuarters(unittest.TestCase):
    def test_single_list_and_range(self):
        self.assertEqual(ingest.parse_quarters("2026q3"), ["2026q3"])
        self.assertEqual(ingest.parse_quarters("2026Q3,2025q4"), ["2025q4", "2026q3"])
        self.assertEqual(ingest.parse_quarters("2025q3:2026q2"),
                         ["2025q3", "2025q4", "2026q1", "2026q2"])
        self.assertEqual(len(ingest.parse_quarters("2023q1:2026q3")), 15)

    def test_bad_input_refused(self):
        for bad in ("2026q5", "26q3", "2026-3", "2026q3:2025q1", ""):
            with self.assertRaises(ingest.ConfigError):
                ingest.parse_quarters(bad)


class TestDatasetPage(unittest.TestCase):
    def test_both_hosting_folders_and_absolute_href(self):
        links = ingest.parse_dataset_page(PAGE_HTML.decode())
        self.assertEqual(links["2026q3"], URL_2026Q3)
        self.assertEqual(links["2026q2"], URL_2026Q2)
        self.assertTrue(links["2006q1"].startswith("https://www.sec.gov/files/structureddata/"))
        self.assertNotIn("readme", " ".join(links.values()))

    def test_unlisted_quarter_halts_before_any_zip_request(self):
        sec = FakeSec({ingest.DATASET_PAGE_URL: [page()]})
        with tempfile.TemporaryDirectory() as d, self.assertRaises(ingest.IngestError) as cm:
            c = ingest.SecClient(UA, 1.0, Path(d) / "log.jsonl", opener=sec,
                                 clock=FakeClock().monotonic, sleep=lambda s: None)
            ingest.run(["2026q4"], Path(d), c)
        self.assertIn("2026q4", str(cm.exception))
        self.assertEqual([u for u, _ in sec.calls], [ingest.DATASET_PAGE_URL])


class TestDownloadAndManifest(IngestTestCase):
    def fake(self, **routes):
        base = {ingest.DATASET_PAGE_URL: [page()], URL_2026Q3: [zip_resp()]}
        base.update(routes)
        return FakeSec(base)

    def test_download_writes_zip_manifest_log_and_extracts(self):
        result = ingest.run(["2026q3"], self.data, self.client(self.fake()))
        self.assertEqual(result["downloaded"], ["2026q3"])
        zp = self.data / "2026q3_form345.zip"
        self.assertEqual(zp.read_bytes(), ZIP_BYTES)
        entry = json.loads((self.data / "manifest.json").read_text())["quarters"]["2026q3"]
        self.assertEqual(entry["sha256"], ZIP_SHA)
        self.assertEqual(entry["bytes"], len(ZIP_BYTES))
        self.assertEqual(entry["source_url"], URL_2026Q3)
        self.assertEqual(entry["http_status"], 200)
        self.assertIs(entry["user_agent_set"], True)
        self.assertTrue(entry["retrieved_at"].endswith("Z"))
        self.assertEqual([r["url"] for r in self.log_lines()], [ingest.DATASET_PAGE_URL, URL_2026Q3])
        self.assertTrue(all({"ts", "url", "status", "elapsed_ms"} <= r.keys() for r in self.log_lines()))
        self.assertTrue((self.data / "2026q3" / "SUBMISSION.tsv").exists())
        self.assertFalse(list(self.data.glob("*.part")))

    def test_user_agent_value_not_stored(self):
        ingest.run(["2026q3"], self.data, self.client(self.fake()))
        for name in ("manifest.json", "request_log.jsonl"):
            text = (self.data / name).read_text()
            self.assertNotIn("example.org", text, name)
            self.assertNotIn("Test Fellow", text, name)

    def test_resume_skips_complete_quarter_with_zero_requests(self):
        ingest.run(["2026q3"], self.data, self.client(self.fake()))
        sec2 = self.fake()
        result = ingest.run(["2026q3"], self.data, self.client(sec2))
        self.assertEqual(result, {"downloaded": [], "skipped": ["2026q3"], "requests": 0})
        self.assertEqual(sec2.calls, [])

    def test_resume_fetches_only_the_missing_quarter(self):
        ingest.run(["2026q3"], self.data, self.client(self.fake()))
        sec2 = self.fake(**{URL_2026Q2: [zip_resp()]})
        result = ingest.run(["2026q2", "2026q3"], self.data, self.client(sec2))
        self.assertEqual(result["downloaded"], ["2026q2"])
        self.assertEqual(result["skipped"], ["2026q3"])
        self.assertEqual([u for u, _ in sec2.calls], [ingest.DATASET_PAGE_URL, URL_2026Q2])

    def test_corrupted_zip_is_redownloaded(self):
        ingest.run(["2026q3"], self.data, self.client(self.fake()))
        (self.data / "2026q3_form345.zip").write_bytes(b"tampered")
        result = ingest.run(["2026q3"], self.data, self.client(self.fake()))
        self.assertEqual(result["downloaded"], ["2026q3"])
        self.assertEqual(ingest.sha256_file(self.data / "2026q3_form345.zip"), ZIP_SHA)

    def assert_nothing_kept(self):
        self.assertFalse((self.data / "2026q3_form345.zip").exists())
        self.assertFalse(list(self.data.glob("*.part")))
        manifest = self.data / "manifest.json"
        if manifest.exists():
            self.assertNotIn("2026q3", json.loads(manifest.read_text())["quarters"])

    def test_interrupted_download_is_discarded(self):
        sec = self.fake(**{URL_2026Q3: [zip_resp(fail_after=100)]})
        with self.assertRaises(ConnectionResetError):
            ingest.run(["2026q3"], self.data, self.client(sec))
        self.assert_nothing_kept()

    def test_truncated_download_is_discarded(self):
        short = FakeResponse(200, ZIP_BYTES[:200], {"Content-Length": str(len(ZIP_BYTES))})
        with self.assertRaises(ingest.IngestError):
            ingest.run(["2026q3"], self.data, self.client(self.fake(**{URL_2026Q3: [short]})))
        self.assert_nothing_kept()

    def test_non_zip_body_is_discarded(self):
        html = b"<html>Request Rate Threshold Exceeded</html>"
        with self.assertRaises(ingest.IngestError):
            ingest.run(["2026q3"], self.data, self.client(self.fake(**{URL_2026Q3: [zip_resp(html)]})))
        self.assert_nothing_kept()

    def test_gzip_encoded_page_is_decoded(self):
        import gzip
        gz = FakeResponse(200, gzip.compress(PAGE_HTML), {"Content-Encoding": "gzip"})
        result = ingest.run(["2026q3"], self.data,
                            self.client(self.fake(**{ingest.DATASET_PAGE_URL: [gz]})))
        self.assertEqual(result["downloaded"], ["2026q3"])


class TestRefusals(IngestTestCase):
    def test_429_backs_off_then_halts(self):
        sec = FakeSec({ingest.DATASET_PAGE_URL: [FakeResponse(429)]})
        with self.assertRaises(ingest.HaltError):
            ingest.run(["2026q3"], self.data, self.client(sec))
        self.assertEqual(len(sec.calls), ingest.MAX_RETRIES + 1)
        backoffs = [s for s in self.clock.sleeps if s >= ingest.BACKOFF_SECONDS]
        self.assertEqual(backoffs, [ingest.BACKOFF_SECONDS, 2 * ingest.BACKOFF_SECONDS])
        self.assertEqual([r["status"] for r in self.log_lines()], [429, 429, 429])

    def test_403_then_200_recovers(self):
        sec = FakeSec({ingest.DATASET_PAGE_URL: [FakeResponse(403), page()],
                       URL_2026Q3: [zip_resp()]})
        result = ingest.run(["2026q3"], self.data, self.client(sec))
        self.assertEqual(result["downloaded"], ["2026q3"])

    def test_404_halts_without_retry(self):
        sec = FakeSec({ingest.DATASET_PAGE_URL: [page()]})   # zip URL unrouted -> 404
        with self.assertRaises(ingest.HaltError):
            ingest.run(["2026q3"], self.data, self.client(sec))
        self.assertEqual([u for u, _ in sec.calls].count(URL_2026Q3), 1)


class TestVerify(IngestTestCase):
    def download(self):
        sec = FakeSec({ingest.DATASET_PAGE_URL: [page()], URL_2026Q3: [zip_resp()]})
        ingest.run(["2026q3"], self.data, self.client(sec))

    def test_clean_run_passes(self):
        self.download()
        self.assertEqual(ingest.verify(["2026q3"], self.data), [])

    def test_hash_mismatch_fails(self):
        self.download()
        (self.data / "2026q3_form345.zip").write_bytes(b"tampered")
        self.assertTrue(any("SHA-256" in p for p in ingest.verify(["2026q3"], self.data)))

    def test_missing_quarter_fails(self):
        self.download()
        self.assertTrue(any("2026q2" in p for p in ingest.verify(["2026q2"], self.data)))

    def test_too_fast_spacing_fails(self):
        self.download()
        log = self.data / ingest.REQUEST_LOG_NAME
        lines = [json.loads(l) for l in log.read_text().splitlines()]
        lines[1]["ts"] = lines[0]["ts"]                     # two requests in the same instant
        log.write_text("".join(json.dumps(l) + "\n" for l in lines))
        self.assertTrue(any("spacing" in p for p in ingest.verify(["2026q3"], self.data)))

    def test_unhandled_refusal_fails(self):
        self.download()
        with open(self.data / ingest.REQUEST_LOG_NAME, "a") as fh:
            fh.write(json.dumps({"ts": "2026-11-03T13:00:00.000Z", "url": "https://www.sec.gov/x",
                                 "status": 429, "elapsed_ms": 5}) + "\n")
        self.assertTrue(any("429" in p for p in ingest.verify(["2026q3"], self.data)))


class TestExtraction(IngestTestCase):
    def test_path_traversal_member_refused(self):
        self.data.mkdir(parents=True)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("../escape.tsv", "x")
        (self.data / "2026q3_form345.zip").write_bytes(buf.getvalue())
        with self.assertRaises(ingest.IngestError):
            ingest.extract_quarter(self.data, "2026q3", "irrelevant")
        self.assertFalse((self.tmp / "escape.tsv").exists())

    def test_extraction_is_idempotent_per_hash(self):
        self.data.mkdir(parents=True)
        (self.data / "2026q3_form345.zip").write_bytes(ZIP_BYTES)
        out = ingest.extract_quarter(self.data, "2026q3", ZIP_SHA)
        marker = json.loads((out / ingest.EXTRACT_MARKER).read_text())
        self.assertEqual(marker["sha256"], ZIP_SHA)
        self.assertIn("NONDERIV_TRANS.tsv", marker["members"])
        (out / "SUBMISSION.tsv").write_text("changed")      # same hash -> not re-extracted
        ingest.extract_quarter(self.data, "2026q3", ZIP_SHA)
        self.assertEqual((out / "SUBMISSION.tsv").read_text(), "changed")


if __name__ == "__main__":
    unittest.main()
