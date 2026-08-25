"""Tests for Phase 7–8 pipeline enhancements."""

from datetime import date

from ecis.config.settings import settings
from ecis.preprocessing.boilerplate import boilerplate_token_ratio, strip_boilerplate
from ecis.preprocessing.chunk_validator import validate_chunk
from ecis.schemas.signal import GuidanceDirection, SectionLabel, SignalRecord, SourceMethod


class TestModelResolution:
    def test_qwen_and_all(self):
        assert settings.resolve_llm_models("qwen") == [settings.llm_qwen_model]
        names = settings.resolve_llm_models("all")
        assert len(names) == 3
        assert settings.llm_qwen_model in names

    def test_aliases(self):
        assert settings.model_alias("qwen2.5:14b-instruct-q4_K_M") == "qwen"
        assert settings.model_alias("mistral:7b-instruct") == "mistral"
        assert settings.model_alias("llama3.1:8b-instruct-q8_0") == "llama"

    def test_model_weight(self):
        w = settings.llm_weight_for("qwen2.5:14b", {"llm_qwen": 0.6, "llm": 0.5})
        assert w == 0.6


class TestChunkValidation:
    def test_empty_rejected(self):
        ok, reason = validate_chunk("   ")
        assert ok is False
        assert reason == "empty"

    def test_short_rejected(self):
        ok, reason = validate_chunk("too short")
        assert ok is False
        assert reason == "below_min_tokens"

    def test_normal_accepted(self):
        text = "We are raising full year revenue guidance based on data center demand " * 3
        ok, reason = validate_chunk(text)
        assert ok is True
        assert reason is None

    def test_boilerplate_ratio(self):
        text = "This release contains forward-looking statements. Safe harbor statement. Form 8-K risk factors."
        assert boilerplate_token_ratio(text) > 0.0
        stripped = strip_boilerplate("Safe harbor statement. We grew revenue 20 percent.")
        assert "revenue" in stripped.lower()


class TestSignalGating:
    def test_low_confidence_flag(self):
        signal = SignalRecord(
            ticker="TICKER",
            direction=GuidanceDirection.MAINTAINED,
            confidence_raw=0.2,
            source_method=SourceMethod.TRIANGULATED,
            supporting_quote="We continue to see demand.",
            section_label=SectionLabel.PREPARED_REMARKS,
            transcript_date=date(2025, 1, 15),
            chunk_index=1,
            character_offsets=(0, 40),
            low_confidence=True,
            content_hash="abc123",
            retry_count=2,
        )
        assert signal.low_confidence is True
        assert signal.retry_count == 2
        assert signal.content_hash == "abc123"
