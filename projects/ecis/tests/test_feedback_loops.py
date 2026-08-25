"""Tests for ticker registry, learning graph, vindication, and HITL approvals."""

from ecis.db.init_db import get_connection, init_all, insert_default_weights
from ecis.schemas.signal import FastPassResult, GuidanceDirection
from ecis.schemas.state import EscalationCategory


def _init(tmp_path, monkeypatch):
    from ecis.config.settings import settings

    monkeypatch.setattr(settings, "db_dir", tmp_path)
    init_all()
    insert_default_weights()


class TestTickerRegistry:
    def test_upsert_and_list(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        from ecis.db.ticker_registry import get_ticker, list_ticker_symbols, upsert_ticker

        upsert_ticker("TICKER", company_name="Test Company", total_transcripts=4)
        row = get_ticker("ticker")
        assert row is not None
        assert row["company_name"] == "Test Company"
        assert row["total_transcripts"] == 4
        assert "TICKER" in list_ticker_symbols()

    def test_upsert_updates_status(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        from ecis.db.ticker_registry import get_ticker, mark_extraction, upsert_ticker

        upsert_ticker("OTHER")
        mark_extraction("OTHER", "complete")
        assert get_ticker("OTHER")["extraction_status"] == "complete"

    def test_migrate_from_directories(self, tmp_path, monkeypatch):
        from ecis.config.settings import settings

        monkeypatch.setattr(settings, "db_dir", tmp_path)
        data = tmp_path / "data"
        edgar = data / "raw" / "edgar" / "TICKER"
        edgar.mkdir(parents=True)
        (edgar / "2024-05-01.htm").write_text("x")
        monkeypatch.setattr(settings, "raw_edgar_dir", data / "raw" / "edgar")
        monkeypatch.setattr(settings, "raw_fmp_dir", data / "raw" / "fmp")
        init_all()
        from ecis.db.ticker_registry import get_ticker, migrate_from_directories

        n = migrate_from_directories()
        assert n >= 1
        row = get_ticker("TICKER")
        assert row is not None
        assert row["total_transcripts"] >= 1


class TestApprovals:
    def test_insert_and_reject(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        from ecis.db.approvals import insert_pending, list_pending, resolve_approval

        aid = insert_pending(
            "watchdog_llm",
            "reduce_weight",
            {"action_type": "reduce_weight", "reader_name": "llm", "proposed_weight": 0.4},
            {"reason": "test"},
        )
        pending = list_pending()
        assert len(pending) == 1
        assert pending[0]["approval_id"] == aid

        resolve_approval(aid, approved=False, note="nope")
        assert list_pending() == []

    def test_approve_reduce_weight(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        from ecis.db.approvals import insert_pending, resolve_approval

        aid = insert_pending(
            "watchdog_llm",
            "reduce_weight",
            {
                "action_type": "reduce_weight",
                "reader_name": "llm",
                "proposed_weight": 0.25,
            },
        )
        resolve_approval(aid, approved=True)
        conn = get_connection("agents")
        row = conn.execute(
            "SELECT weight FROM reader_weights WHERE reader_name = ?", ("llm",)
        ).fetchone()
        conn.close()
        assert row["weight"] == 0.25


class TestVindication:
    def test_skips_below_min_conflicts(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        from ecis.extraction.vindication import aggregate_vindications

        result = aggregate_vindications()
        assert result["applied"] is False
        assert result["total_conflicts"] == 0

    def test_updates_weights_when_keyword_wins(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        conn = get_connection("agents")
        for i in range(8):
            conn.execute(
                """INSERT INTO vindication_records
                   (ticker, chunk_index, conflict_type, vindicated_reader, defeated_reader, reasoning)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                ("TICKER", i, "raised_vs_lowered", "keyword", "finbert", "test"),
            )
        conn.commit()
        conn.close()

        from ecis.extraction.vindication import aggregate_vindications

        result = aggregate_vindications(min_conflicts=5)
        assert result["rates"]["keyword"]["wins"] == 8
        assert result["applied"] is True
        assert result["proposed_weights"]["keyword"] > result["proposed_weights"]["finbert"]


class TestLearningGraph:
    def test_near_miss_fn_loosens_thresholds(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        conn = get_connection("agents")
        for i in range(12):
            conn.execute(
                """INSERT INTO chunk_classifications
                   (ticker, transcript_date, chunk_index, category,
                    keyword_matched, keyword_confidence, finbert_confidence)
                   VALUES (?, ?, ?, 'D', 0, 0, ?)""",
                ("TICKER", "2024-01-01", i, 0.52),
            )
        conn.commit()
        conn.close()

        from ecis.graphs.learning_graph import run_learning

        result = run_learning()
        assert result["missed_from_category_d"] == 12
        assert result["false_negative_rate"] > 0.05
        assert result["adjustment_applied"] is True
        conn = get_connection("agents")
        row = conn.execute(
            "SELECT value FROM escalation_thresholds WHERE param_name = 'finbert_confidence_min'"
        ).fetchone()
        conn.close()
        assert row["value"] < 0.6


class TestClassifyPersist:
    def test_persist_classifications(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        from ecis.graphs.orchestration_agent import classify_chunks

        fp = FastPassResult(
            chunk_index=0,
            chunk_text="We are raising guidance.",
            keyword_matched=True,
            keyword_direction=GuidanceDirection.RAISED,
            keyword_confidence=1.0,
            finbert_direction=GuidanceDirection.RAISED,
            finbert_confidence=0.8,
        )
        cats = classify_chunks([fp], ticker="TICKER", transcript_date="2024-01-01")
        assert cats[EscalationCategory.A] == [0]
        conn = get_connection("agents")
        row = conn.execute("SELECT * FROM chunk_classifications").fetchone()
        conn.close()
        assert row["ticker"] == "TICKER"
        assert row["category"] == "A"


class TestSettingsModels:
    def test_resolve_llama_mistral_both(self):
        from ecis.config.settings import settings

        llama = settings.resolve_llm_models("llama")
        mistral = settings.resolve_llm_models("mistral")
        both = settings.resolve_llm_models("both")
        assert len(llama) == 1 and "llama" in llama[0].lower()
        assert len(mistral) == 1 and "mistral" in mistral[0].lower()
        assert both == llama + mistral
        assert settings.model_alias(mistral[0]) == "mistral"
        assert settings.model_alias(llama[0]) == "llama"
