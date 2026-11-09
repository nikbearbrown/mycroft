"""Phase 2: ingest helpers, clean, normalise, chunk metadata, signal contract."""

from datetime import date

import pytest

from ecis.config.settings import settings
from ecis.preprocessing.chunker import _parse_sections
from ecis.preprocessing.normaliser import normalise_transcript
from ecis.schemas.signal import GuidanceDirection, SectionLabel, SignalRecord, SourceMethod
from tests.local_import import load_ecis


class TestIngestGuards:
    def test_edgar_rate_limiter_interval(self):
        pytest.importorskip("bs4")
        from ecis.ingestion.edgar_fetcher import RateLimiter

        limiter = RateLimiter(10)
        assert abs(limiter._interval - 0.1) < 1e-9

    def test_fmp_daily_limit(self):
        fmp = load_ecis("ingestion/fmp_fetcher.py", "ecis_fmp_fetcher")
        tracker = fmp.DailyLimitTracker(2)
        assert tracker.remaining == 2
        assert tracker.consume() is True
        assert tracker.consume() is True
        assert tracker.consume() is False


class TestCleaning:
    def test_edgar_strips_html_and_script(self):
        pytest.importorskip("bs4")
        from ecis.preprocessing.cleaner import clean_edgar_html

        html = "<html><script>void 0</script><body><p>We raised guidance.</p></body></html>"
        text = clean_edgar_html(html)
        assert "script" not in text.lower()
        assert "raised guidance" in text.lower()

    def test_fmp_json_content(self):
        pytest.importorskip("bs4")
        from ecis.preprocessing.cleaner import clean_fmp_json

        text = clean_fmp_json('{"content": "Analyst Q&A. We reaffirm guidance."}')
        assert "reaffirm" in text.lower()


class TestNormaliseAndChunkMeta:
    def test_section_and_speaker_markers(self):
        raw = (
            "Prepared remarks\n"
            "Jane Doe, CEO:\n"
            "Welcome to the call.\n"
            "Question-and-answer\n"
            "Alex Smith, Analyst:\n"
            "What is the outlook?"
        )
        out = normalise_transcript(raw)
        assert "[SECTION: prepared_remarks]" in out
        assert "[SECTION: qa]" in out
        assert "[SPEAKER:" in out

    def test_parse_sections_does_not_cross_boundary(self):
        text = (
            "[SECTION: prepared_remarks]\n"
            "[SPEAKER: CEO]\n"
            "Opening remarks.\n"
            "[SECTION: qa]\n"
            "[SPEAKER: Analyst]\n"
            "What is next quarter?"
        )
        sections = _parse_sections(text)
        labels = {s["section_label"] for s in sections}
        assert "prepared_remarks" in labels
        assert "qa" in labels


class TestSignalContract:
    def test_invalid_confidence_and_empty_quote(self):
        kwargs = dict(
            ticker="TICKER",
            direction=GuidanceDirection.RAISED,
            confidence_raw=0.8,
            source_method=SourceMethod.KEYWORD,
            supporting_quote="We are raising guidance.",
            section_label=SectionLabel.PREPARED_REMARKS,
            transcript_date=date(2025, 1, 15),
            chunk_index=0,
            character_offsets=(0, 20),
        )
        SignalRecord(**kwargs)
        with pytest.raises(Exception):
            SignalRecord(**{**kwargs, "confidence_raw": 1.2})
        with pytest.raises(Exception):
            SignalRecord(**{**kwargs, "supporting_quote": ""})

    def test_embedding_defaults(self):
        assert "MiniLM" in settings.embedding_model_name
        assert settings.embedding_dim == 384
        assert settings.chunk_size_tokens == 400
        assert settings.chunk_overlap_tokens == 50
