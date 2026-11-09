"""Phase 5: filing-date column, outcome cache key, watchdog knobs, price cache."""

import sqlite3

from ecis.db.init_db import get_connection, init_all, insert_default_weights
from ecis.scoring.price_cache import get_cached
from tests.local_import import load_ecis, stub_module


def _init(tmp_path, monkeypatch):
    from ecis.config.settings import settings

    monkeypatch.setattr(settings, "db_dir", tmp_path)
    init_all()
    insert_default_weights()


class TestFilingDateAndCacheKey:
    def test_outcomes_unique_includes_transcript_date(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        conn = sqlite3.connect(str(tmp_path / "outcomes.db"))
        cols = {row[1] for row in conn.execute("PRAGMA table_info(outcomes)")}
        sql = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='outcomes'"
        ).fetchone()[0]
        conn.close()
        assert "transcript_date" in cols
        assert "signal_id, horizon_days, transcript_date" in sql

    def test_file_metadata_period_of_report(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        conn = get_connection("agents")
        cols = {row[1] for row in conn.execute("PRAGMA table_info(file_metadata)")}
        conn.close()
        assert "period_of_report" in cols

    def test_horizons_cover_scorecard(self):
        stub_module("yfinance", download=lambda *a, **k: None, Ticker=type("T", (), {}))
        mod = load_ecis("scoring/outcome_resolver.py", "ecis_outcome_resolver")
        assert set(mod.HORIZONS) == {30, 90, 180}


class TestWatchdogAndPriceCache:
    def test_threshold_roundtrip(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        from ecis.db.init_db import get_threshold, set_threshold

        assert get_threshold("finbert_confidence_min", 0.6) == 0.6
        set_threshold("ece_recalibrate", 0.10)
        assert get_threshold("ece_recalibrate", 0.0) == 0.10

    def test_price_cache_miss(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        assert get_cached("TICKER", "2024-01-15") is None
