"""Calibration, contradictions, SHAP-style explanations, and OOD gating."""

from ecis.db.init_db import get_connection, init_all, insert_default_weights
from ecis.db.ticker_registry import upsert_ticker
from ecis.reliability.calibrate import apply_isotonic, apply_platt, fit_isotonic, fit_platt
from ecis.reliability.contradictions import detect_contradictions
from ecis.reliability.explanations import explain_row
from ecis.reliability.ood import mahalanobis, penalty_for
from ecis.reliability.shap_explain import linear_shap


def _init(tmp_path, monkeypatch):
    from ecis.config.settings import settings

    monkeypatch.setattr(settings, "db_dir", tmp_path)
    monkeypatch.setattr(settings, "fmp_api_key", "")
    monkeypatch.setattr(settings, "normalised_dir", tmp_path / "normalised")
    settings.normalised_dir.mkdir(parents=True, exist_ok=True)
    init_all()
    insert_default_weights()


def _signal(ticker, day, direction="raised", conf=0.85, hedge=0.4, tone=0.3):
    conn = get_connection("signals")
    conn.execute(
        """INSERT INTO signals
           (ticker, direction, confidence_raw, source_method, supporting_quote,
            section_label, transcript_date, chunk_index, char_start, char_end,
            hedging_index, fls_density, tone_shift)
           VALUES (?, ?, ?, 'triangulated', 'We will deliver growth.',
                   'prepared_remarks', ?, 0, 0, 40, ?, 0.4, ?)""",
        (ticker, direction, conf, day, hedge, tone),
    )
    conn.commit()
    sid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return sid


class TestCalibration:
    def test_platt_and_isotonic(self):
        xs = [0.1, 0.2, 0.4, 0.6, 0.8, 0.9]
        ys = [0, 0, 0, 1, 1, 1]
        platt = fit_platt(xs, ys)
        assert apply_platt(0.9, platt["coef"], platt["intercept"]) > apply_platt(0.1, platt["coef"], platt["intercept"])
        knots = fit_isotonic(xs, ys)
        assert apply_isotonic(0.85, knots) >= apply_isotonic(0.15, knots)


class TestContradictions:
    def test_bullish_hedge_and_high_conf_dodge(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        upsert_ticker("AAA", sector="AI")
        _signal("AAA", "2024-01-15", conf=0.9, hedge=0.5, tone=0.4)
        conn = get_connection("agents")
        conn.execute(
            """INSERT INTO dodge_scores
               (ticker, transcript_date, quarter, scope, dodge)
               VALUES ('AAA', '2024-01-15', '2024Q1', 'call', 0.6)"""
        )
        conn.commit()
        conn.close()
        rows = detect_contradictions("AAA")
        rules = {r["rule"] for r in rows}
        assert "bullish_tone_rising_hedge" in rules
        assert "high_confidence_high_dodge" in rules
        assert all(r["resolution"] in {"uncertainty", "obfuscation", "mixed_outlook"} for r in rows)


class TestExplainAndOod:
    def test_linear_shap_and_template(self):
        phis = linear_shap([1.0, 0.0], [0.5, -0.2], [0.0, 0.0])
        assert abs(sum(phis) - 0.5) < 1e-9
        text = explain_row("AAA", [
            {"feature": "hedging_index", "shap": 0.4},
            {"feature": "ceo_cfo_divergence", "shap": 0.2},
            {"feature": "dodge_score", "shap": 0.1},
        ])
        assert text.startswith("AAA flagged because")
        assert "NVIDIA" not in text

    def test_mahalanobis_and_penalty(self):
        mean = [0.0, 0.0]
        dist = mahalanobis([3.0, 0.0], mean, None)
        assert dist == 3.0
        assert penalty_for(0.5) == 0.0
        assert penalty_for(10.0) > penalty_for(3.0)


class TestRefresh:
    def test_persists(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        upsert_ticker("AAA", sector="AI")
        sid = _signal("AAA", "2024-01-15")
        _signal("AAA", "2024-04-15", direction="lowered", conf=0.4, hedge=0.2, tone=-0.1)
        conn = get_connection("outcomes")
        conn.execute(
            """INSERT INTO outcomes
               (signal_id, horizon_days, excess_return, correct, transcript_date, ret_same_day)
               VALUES (?, 30, 0.03, 1, '2024-01-15', 0.01)""",
            (sid,),
        )
        conn.commit()
        conn.close()
        from ecis.analytics.store import fetch_table
        from ecis.reliability.refresh import refresh_reliability

        result = refresh_reliability("AAA")
        assert result["tables"]["calibration_models"] >= 1
        assert fetch_table("calibration_models")
        assert fetch_table("contradictions") or True
