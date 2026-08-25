"""Tests for database init, orchestration agent, and triangulator."""

import os
import sqlite3
import tempfile

import pytest

from ecis.schemas.signal import (
    FastPassResult,
    GuidanceDirection,
    SectionLabel,
)
from ecis.schemas.state import EscalationCategory


class TestDatabaseInit:
    def test_init_creates_databases(self, tmp_path, monkeypatch):
        from ecis.config.settings import settings

        monkeypatch.setattr(settings, "db_dir", tmp_path)
        from ecis.db.init_db import init_all

        init_all()

        for name in ("signals", "outcomes", "agents", "checkpoints"):
            db_path = tmp_path / f"{name}.db"
            assert db_path.exists(), f"{name}.db was not created"
            conn = sqlite3.connect(str(db_path))
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            conn.close()
            assert len(tables) > 0, f"{name}.db has no tables"

    def test_signals_schema(self, tmp_path, monkeypatch):
        from ecis.config.settings import settings

        monkeypatch.setattr(settings, "db_dir", tmp_path)
        from ecis.db.init_db import init_database

        init_database("signals")
        conn = sqlite3.connect(str(tmp_path / "signals.db"))
        cursor = conn.execute("PRAGMA table_info(signals)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()

        expected = {
            "signal_id", "ticker", "direction", "confidence_raw",
            "source_method", "supporting_quote", "section_label",
            "transcript_date", "chunk_index", "char_start", "char_end",
            "created_at", "llm_model", "content_hash", "retry_count",
            "low_confidence",
        }
        assert expected.issubset(columns)


class TestOrchestrationAgent:
    def test_category_a_both_agree(self):
        from ecis.graphs.orchestration_agent import classify_chunk

        fp = FastPassResult(
            chunk_index=0,
            chunk_text="We are raising guidance.",
            keyword_matched=True,
            keyword_direction=GuidanceDirection.RAISED,
            keyword_confidence=1.0,
            finbert_direction=GuidanceDirection.RAISED,
            finbert_confidence=0.8,
            finbert_positive=0.8,
            finbert_negative=0.1,
            finbert_neutral=0.1,
        )
        assert classify_chunk(fp) == EscalationCategory.A

    def test_category_c_disagree(self):
        from ecis.graphs.orchestration_agent import classify_chunk

        fp = FastPassResult(
            chunk_index=0,
            chunk_text="We are raising guidance but challenges remain.",
            keyword_matched=True,
            keyword_direction=GuidanceDirection.RAISED,
            keyword_confidence=1.0,
            finbert_direction=GuidanceDirection.LOWERED,
            finbert_confidence=0.7,
            finbert_positive=0.1,
            finbert_negative=0.7,
            finbert_neutral=0.2,
        )
        assert classify_chunk(fp) == EscalationCategory.C

    def test_category_d_nothing(self):
        from ecis.graphs.orchestration_agent import classify_chunk

        fp = FastPassResult(
            chunk_index=0,
            chunk_text="Revenue grew 15% year over year.",
            keyword_matched=False,
            keyword_confidence=0.0,
            finbert_confidence=0.4,
            finbert_positive=0.3,
            finbert_negative=0.3,
            finbert_neutral=0.4,
        )
        assert classify_chunk(fp) == EscalationCategory.D

    def test_category_b_one_reader(self):
        from ecis.graphs.orchestration_agent import classify_chunk

        fp = FastPassResult(
            chunk_index=0,
            chunk_text="We see upside to guidance.",
            keyword_matched=True,
            keyword_direction=GuidanceDirection.RAISED,
            keyword_confidence=1.0,
            finbert_confidence=0.4,
            finbert_positive=0.4,
            finbert_negative=0.3,
            finbert_neutral=0.3,
        )
        assert classify_chunk(fp) == EscalationCategory.B


class TestTriangulator:
    def test_triangulate_agreement(self):
        from ecis.extraction.triangulator import triangulate_chunk

        chunk = {
            "chunk_index": 0,
            "text": "We are raising guidance for the year.",
            "ticker": "TICKER",
            "transcript_date": "2025-01-15",
            "section_label": "prepared_remarks",
            "speaker": "CEO",
            "char_start": 0,
            "char_end": 40,
        }
        kw = {"matched": True, "direction": "raised", "confidence": 1.0, "phrases": ["raising guidance"]}
        fb = {"direction": GuidanceDirection.RAISED, "confidence": 0.8}
        llm = {
            "direction": "raised",
            "confidence": 0.9,
            "supporting_quote": "We are raising guidance for the year.",
            "reasoning": "Forward-looking, explicit raise.",
        }

        signal = triangulate_chunk(chunk, kw, fb, llm)
        assert signal is not None
        assert signal.direction == GuidanceDirection.RAISED
        assert signal.confidence_raw > 0.5
        assert signal.ticker == "TICKER"
