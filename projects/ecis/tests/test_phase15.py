"""Phase 15: sector mood, management language, surprise, and reaction windows."""

from ecis.analytics.features import (
    definitive_ratio,
    numerical_specificity,
    quarter_key,
)
from ecis.analytics.management import ceo_cfo_divergence, confidence_score, guidance_language, management_confidence
from ecis.analytics.sector_sentiment import aggregate_sector_sentiment, cross_sector_zscores, sector_mood_index
from ecis.analytics.stats import mean, pearson, spearman, zscore
from ecis.db.init_db import get_connection, init_all, insert_default_weights
from ecis.db.ticker_registry import upsert_ticker


def _init(tmp_path, monkeypatch):
    from ecis.config.settings import settings

    monkeypatch.setattr(settings, "db_dir", tmp_path)
    monkeypatch.setattr(settings, "fmp_api_key", "")
    init_all()
    insert_default_weights()


def _insert_signal(
    ticker,
    day,
    direction="raised",
    conf=0.8,
    quote="We will grow revenue 12% in FY2025.",
    role="ceo",
    hedge=0.1,
    fls=0.6,
    tone=0.4,
):
    conn = get_connection("signals")
    conn.execute(
        """INSERT INTO signals
           (ticker, direction, confidence_raw, source_method, supporting_quote,
            section_label, transcript_date, chunk_index, char_start, char_end,
            speaker_role, hedging_index, fls_density, tone_shift)
           VALUES (?, ?, ?, 'triangulated', ?,
                   'prepared_remarks', ?, 0, 0, 40, ?, ?, ?, ?)""",
        (ticker, direction, conf, quote, day, role, hedge, fls, tone),
    )
    conn.commit()
    sid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return sid


def _insert_outcome(signal_id, day, excess=0.04, same=0.01, mid=0.02, week=0.03, mag=0.05):
    conn = get_connection("outcomes")
    conn.execute(
        """INSERT INTO outcomes
           (signal_id, horizon_days, excess_return, correct, transcript_date,
            ret_same_day, ret_1_3d, ret_1_2w, reaction_magnitude)
           VALUES (?, 30, ?, 1, ?, ?, ?, ?, ?)""",
        (signal_id, excess, day, same, mid, week, mag),
    )
    conn.commit()
    conn.close()


class TestStats:
    def test_pearson_spearman_and_zscore(self):
        xs = [1, 2, 3, 4, 5]
        ys = [2, 4, 6, 8, 10]
        assert abs(pearson(xs, ys) - 1.0) < 1e-9
        assert abs(spearman(xs, ys) - 1.0) < 1e-9
        assert zscore(5, xs) is not None
        assert mean([1, None, 3]) == 2.0


class TestLanguageFeatures:
    def test_specificity_and_definitive_ratio(self):
        specific = "We will grow revenue 12% in FY2025 and target 18% operating margin."
        vague = "We may approximately see various outcomes around mid-single digits."
        assert numerical_specificity(specific) > numerical_specificity(vague)
        assert definitive_ratio(specific) > definitive_ratio(vague)
        assert quarter_key("2024-05-12") == "2024-Q2"

    def test_confidence_score_bounds(self):
        high = confidence_score({
            "quote": "We will grow revenue 12% in FY2025.",
            "hedging_index": 0.05,
            "fls_density": 0.8,
        })
        low = confidence_score({
            "quote": "We may approximately see various outcomes around mid-single digits.",
            "hedging_index": 0.9,
            "fls_density": 0.1,
        })
        assert 0 <= low < high <= 100


class TestSectorAnalytics:
    def test_aggregator_mood_and_zscores(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        upsert_ticker("AAA", sector="semiconductors")
        upsert_ticker("BBB", sector="software")
        _insert_signal("AAA", "2024-01-15", hedge=0.1, fls=0.7, tone=0.5)
        _insert_signal("AAA", "2024-04-15", hedge=0.4, fls=0.3, tone=-0.2, direction="lowered")
        _insert_signal("BBB", "2024-01-15", hedge=0.2, fls=0.5, tone=0.1)
        _insert_signal("BBB", "2024-04-15", hedge=0.25, fls=0.45, tone=0.05)

        sector = aggregate_sector_sentiment()
        names = {r["sector"] for r in sector}
        assert "semiconductors" in names
        assert "software" in names
        row = next(r for r in sector if r["sector"] == "semiconductors" and r["quarter"] == "2024-Q1")
        assert row["tone_mean"] is not None
        assert row["hedging_mean"] is not None
        assert row["n_tickers"] == 1

        mood = sector_mood_index()
        assert any(r["regime"] in {"bullish", "bearish", "neutral"} for r in mood)
        z = cross_sector_zscores()
        q1 = [r for r in z if r["quarter"] == "2024-Q1"]
        assert len(q1) == 2


class TestManagement:
    def test_guidance_and_divergence(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        upsert_ticker("AAA", sector="AI")
        _insert_signal(
            "AAA", "2024-01-15", role="ceo",
            quote="We will grow revenue 12% in FY2025.", hedge=0.1, fls=0.7,
        )
        _insert_signal(
            "AAA", "2024-01-15", role="cfo",
            quote="We may approximately see various outcomes around mid-single digits.",
            hedge=0.8, fls=0.2, direction="maintained", conf=0.4,
        )
        _insert_signal(
            "AAA", "2024-04-16", role="ceo",
            quote="We may approximately see various outcomes around mid-single digits.",
            hedge=0.7, fls=0.2,
        )

        conf = management_confidence()
        assert conf[0]["confidence"] is not None
        guide = guidance_language()
        later = [r for r in guide if r["quarter"] == "2024-Q2"]
        assert later
        assert later[0]["flag"] in {"more_vague", "more_specific", "stable"}
        div = ceo_cfo_divergence()
        assert div
        assert div[0]["confidence_gap"] > 0


class TestImpactAndSurprise:
    def test_correlations_windows_and_surprise(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        upsert_ticker("AAA", sector="AI")
        sids = []
        for i, (day, direction, excess) in enumerate([
            ("2024-01-15", "raised", 0.05),
            ("2024-01-16", "raised", 0.04),
            ("2024-01-17", "lowered", -0.03),
            ("2024-01-18", "lowered", -0.02),
        ]):
            sid = _insert_signal("AAA", day, direction=direction, conf=0.7 + i * 0.02)
            _insert_outcome(sid, day, excess=excess, same=excess / 2)
            sids.append(sid)

        from ecis.analytics.impact import reaction_windows, signal_price_correlation
        from ecis.analytics.surprise import surprise_analytics

        corr = signal_price_correlation()
        features = {r["feature"] for r in corr}
        assert {"direction", "confidence", "hedging", "tone_shift"} <= features
        windows = reaction_windows()
        assert any(r["car_1d"] is not None for r in windows)
        surprise = surprise_analytics()
        assert surprise
        assert "nlp_vs_consensus" in surprise[0]


class TestRefresh:
    def test_persists_tables(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        upsert_ticker("AAA", sector="AI")
        sid = _insert_signal("AAA", "2024-01-15")
        _insert_outcome(sid, "2024-01-15")
        from ecis.analytics.refresh import refresh_analytics
        from ecis.analytics.store import fetch_table

        result = refresh_analytics()
        assert result["tables"]["sector_mood"] >= 1
        assert fetch_table("sector_mood")
        assert fetch_table("management_confidence")
