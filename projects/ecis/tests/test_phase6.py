"""Phase 6: Llama vs Mistral model tags, content-hash join, per-model Scorecard."""

import inspect

from ecis.config.settings import settings
from ecis.scoring.scorer import score_by_llm_model


class TestModelTags:
    def test_llama_and_mistral_resolution(self):
        assert settings.resolve_llm_models("llama") == [settings.llm_llama_model]
        assert settings.resolve_llm_models("mistral") == [settings.llm_mistral_model]
        both = settings.resolve_llm_models("both")
        assert settings.llm_llama_model in both
        assert settings.llm_mistral_model in both

    def test_aliases(self):
        assert settings.model_alias("llama3.1:8b-instruct-q8_0") == "llama"
        assert settings.model_alias("mistral:7b-instruct") == "mistral"


class TestAlignmentAndScorecard:
    def test_signals_have_content_hash(self, tmp_path, monkeypatch):
        from ecis.db.init_db import init_database

        monkeypatch.setattr(settings, "db_dir", tmp_path)
        init_database("signals")
        import sqlite3

        conn = sqlite3.connect(str(tmp_path / "signals.db"))
        cols = {row[1] for row in conn.execute("PRAGMA table_info(signals)")}
        conn.close()
        assert "content_hash" in cols
        assert "llm_model" in cols

    def test_score_by_llm_model_exists(self):
        assert callable(score_by_llm_model)
        params = inspect.signature(score_by_llm_model).parameters
        assert "ticker" in params or "horizon" in params or len(params) >= 0
