"""Tests for the Pydantic signal schema."""

from datetime import date, datetime

import pytest

from ecis.schemas.signal import (
    ChunkMeta,
    FastPassResult,
    GuidanceDirection,
    SectionLabel,
    SignalRecord,
    SourceMethod,
    VerificationStatus,
)


class TestSignalRecord:
    def _valid_kwargs(self, **overrides):
        defaults = {
            "ticker": "TICKER",
            "direction": GuidanceDirection.RAISED,
            "confidence_raw": 0.85,
            "source_method": SourceMethod.LLM,
            "supporting_quote": "We are raising our revenue guidance.",
            "section_label": SectionLabel.PREPARED_REMARKS,
            "transcript_date": date(2025, 1, 15),
            "chunk_index": 3,
            "character_offsets": (100, 200),
        }
        defaults.update(overrides)
        return defaults

    def test_valid_signal(self):
        signal = SignalRecord(**self._valid_kwargs())
        assert signal.ticker == "TICKER"
        assert signal.direction == GuidanceDirection.RAISED
        assert signal.confidence_raw == 0.85

    def test_confidence_bounds(self):
        with pytest.raises(Exception):
            SignalRecord(**self._valid_kwargs(confidence_raw=1.5))
        with pytest.raises(Exception):
            SignalRecord(**self._valid_kwargs(confidence_raw=-0.1))

    def test_empty_quote_rejected(self):
        with pytest.raises(Exception):
            SignalRecord(**self._valid_kwargs(supporting_quote=""))

    def test_invalid_offsets_reversed(self):
        with pytest.raises(Exception):
            SignalRecord(**self._valid_kwargs(character_offsets=(200, 100)))

    def test_negative_offsets_rejected(self):
        with pytest.raises(Exception):
            SignalRecord(**self._valid_kwargs(character_offsets=(-1, 50)))

    def test_all_directions(self):
        for d in GuidanceDirection:
            signal = SignalRecord(**self._valid_kwargs(direction=d))
            assert signal.direction == d

    def test_all_source_methods(self):
        for m in SourceMethod:
            signal = SignalRecord(**self._valid_kwargs(source_method=m))
            assert signal.source_method == m

    def test_optional_fields_default_none(self):
        signal = SignalRecord(**self._valid_kwargs())
        assert signal.confidence_calibrated is None
        assert signal.reasoning_trace is None
        assert signal.ner_entities is None
        assert signal.self_consistency_votes is None
        assert signal.verification_status is None
        assert signal.llm_model is None
        assert signal.content_hash is None
        assert signal.retry_count == 0
        assert signal.low_confidence is False

    def test_calibrated_confidence_bounds(self):
        signal = SignalRecord(**self._valid_kwargs(confidence_calibrated=0.9))
        assert signal.confidence_calibrated == 0.9
        with pytest.raises(Exception):
            SignalRecord(**self._valid_kwargs(confidence_calibrated=1.2))

    def test_serialisation_roundtrip(self):
        signal = SignalRecord(**self._valid_kwargs())
        data = signal.model_dump()
        restored = SignalRecord(**data)
        assert restored.ticker == signal.ticker
        assert restored.direction == signal.direction


class TestChunkMeta:
    def test_valid_chunk_meta(self):
        meta = ChunkMeta(
            source_file="data/raw/TICKER.html",
            ticker="TICKER",
            transcript_date=date(2025, 1, 15),
            section_label=SectionLabel.QA,
            speaker="CEO",
            chunk_index=0,
            char_start=0,
            char_end=400,
        )
        assert meta.ticker == "TICKER"
        assert meta.section_label == SectionLabel.QA

    def test_invalid_end_before_start(self):
        with pytest.raises(Exception):
            ChunkMeta(
                source_file="test.html",
                ticker="TICKER",
                transcript_date=date(2025, 1, 15),
                section_label=SectionLabel.PREPARED_REMARKS,
                chunk_index=0,
                char_start=100,
                char_end=50,
            )


class TestFastPassResult:
    def test_default_values(self):
        fp = FastPassResult(chunk_index=0, chunk_text="test")
        assert fp.keyword_matched is False
        assert fp.finbert_confidence == 0.0
        assert fp.keyword_direction is None
