"""Phase 3: SQLite init, state schema, keyword/NER, triangulation, cosine."""

import sqlite3

import numpy as np

from ecis.extraction.triangulator import triangulate_chunk
from ecis.graphs.orchestration_agent import classify_chunk
from ecis.schemas.signal import FastPassResult, GuidanceDirection
from ecis.schemas.state import EscalationCategory, PipelineState
from tests.local_import import load_ecis


def _keyword():
    return load_ecis("readers/keyword_reader.py", "ecis_keyword_reader")


def _ner():
    return load_ecis("readers/ner_reader.py", "ecis_ner_reader")


class TestDatabases:
    def test_four_files_and_weights(self, tmp_path, monkeypatch):
        from ecis.config.settings import settings
        from ecis.db.init_db import init_all, insert_default_weights

        monkeypatch.setattr(settings, "db_dir", tmp_path)
        init_all()
        insert_default_weights()
        for name in ("signals", "outcomes", "agents", "checkpoints"):
            assert (tmp_path / f"{name}.db").exists()
        conn = sqlite3.connect(str(tmp_path / "agents.db"))
        names = {r[0] for r in conn.execute("SELECT reader_name FROM reader_weights")}
        conn.close()
        assert {"keyword", "finbert", "llm"} <= names


class TestStateAndRouting:
    def test_pipeline_state_keys(self):
        keys = PipelineState.__annotations__
        assert "chunks" in keys
        assert "category_a_indices" in keys
        assert "llm_model" in keys

    def test_escalation_categories(self):
        agree = FastPassResult(
            chunk_index=0, chunk_text="x",
            keyword_matched=True, keyword_direction=GuidanceDirection.RAISED,
            finbert_direction=GuidanceDirection.RAISED, finbert_confidence=0.9,
        )
        disagree = FastPassResult(
            chunk_index=1, chunk_text="x",
            keyword_matched=True, keyword_direction=GuidanceDirection.RAISED,
            finbert_direction=GuidanceDirection.LOWERED, finbert_confidence=0.9,
        )
        empty = FastPassResult(chunk_index=2, chunk_text="x")
        assert classify_chunk(agree) == EscalationCategory.A
        assert classify_chunk(disagree) == EscalationCategory.C
        assert classify_chunk(empty) == EscalationCategory.D


class TestReadersAndCombine:
    def test_keyword_baseline(self):
        keyword_read = _keyword().read_chunk
        hit = keyword_read("We are raising guidance for the full year based on strong demand.")
        miss = keyword_read("The weather was mild this quarter.")
        assert hit["matched"] is True
        assert hit["direction"] == "raised"
        assert miss["matched"] is False

    def test_ner_money_and_metrics(self):
        ner = _ner()
        text = "Revenue of $35.1 billion and free cash flow improved."
        assert ner._MONEY_PATTERN.search(text)
        assert any(p.search(text) for p in ner._METRIC_PATTERNS)

    def test_triangulator_prefers_agreement(self, tmp_path, monkeypatch):
        from ecis.config.settings import settings
        from ecis.db.init_db import init_all, insert_default_weights

        monkeypatch.setattr(settings, "db_dir", tmp_path)
        init_all()
        insert_default_weights()
        chunk = {
            "ticker": "TICKER",
            "text": "We are raising full year guidance.",
            "section_label": "prepared_remarks",
            "transcript_date": "2025-01-15",
            "chunk_index": 0,
            "char_start": 0,
            "char_end": 40,
            "speaker": "CFO",
        }
        signal = triangulate_chunk(
            chunk,
            {"matched": True, "direction": "raised", "confidence": 1.0},
            {"direction": "raised", "confidence": 0.8},
            {"direction": "raised", "confidence": 0.9, "supporting_quote": chunk["text"]},
        )
        assert signal is not None
        assert signal.direction.value == "raised"

    def test_cosine_identical_is_one(self):
        def cosine_similarity(a, b):
            va, vb = np.array(a), np.array(b)
            denom = np.linalg.norm(va) * np.linalg.norm(vb)
            return 0.0 if denom == 0 else float(np.dot(va, vb) / denom)

        assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0
        assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0
