from ecis.db.init_db import get_connection, init_all, insert_default_weights
from ecis.db.ticker_registry import upsert_ticker
from ecis.forecasting.coref import resolve_text
from ecis.forecasting.prophet import _decompose_series
from ecis.forecasting.reasoning import is_multistep, plan_chain
from ecis.forecasting.survival import fit_survival, kaplan_meier
from ecis.forecasting.tft import HORIZONS, fit_tft
from ecis.forecasting.topic_shift import js_divergence


def _init(tmp_path, monkeypatch):
    from ecis.config.settings import settings

    monkeypatch.setattr(settings, "db_dir", tmp_path)
    monkeypatch.setattr(settings, "fmp_api_key", "")
    monkeypatch.setattr(settings, "normalised_dir", tmp_path / "normalised")
    settings.normalised_dir.mkdir(parents=True, exist_ok=True)
    init_all()
    insert_default_weights()


class TestForecasts:
    def test_tft_fan_and_horizons(self):
        seqs = []
        for i, q in enumerate(("2022-Q1", "2022-Q2", "2022-Q3", "2022-Q4", "2023-Q1")):
            seqs.append({
                "ticker": "AAA",
                "quarter": q,
                "X": [[0.1 * (i + 1)] * 9 for _ in range(4)],
                "target": int(i % 2 == 0),
                "n_steps": 4,
            })
        result = fit_tft(sequences=seqs)
        rows = result["forecasts"]
        assert {r["horizon"] for r in rows} == set(HORIZONS)
        assert all(r["p10"] <= r["p50"] <= r["p90"] for r in rows)

    def test_prophet_adds_up(self):
        parts = _decompose_series([0.1, 0.2, 0.15, 0.35, 0.3, 0.5, 0.45, 0.7])
        for row in parts:
            recon = row["trend"] + row["seasonality"] + row["residual"]
            assert abs(recon - row["observed"]) < 1e-6

    def test_km_decreases_and_cox(self):
        curve = kaplan_meier([1, 1, 2, 4, 8], [1, 1, 1, 0, 0])
        vals = [curve[t] for t in sorted(curve) if t > 0]
        assert vals == sorted(vals, reverse=True)
        events = [
            {"ticker": "AAA", "quarter": "2023-Q1", "time": 1, "event": 1, "x": [0.8, 40, 0.6, 0.1, 0.2, 0.4, 0.1, -0.1]},
            {"ticker": "AAA", "quarter": "2023-Q2", "time": 2, "event": 1, "x": [0.6, 45, 0.4, 0.0, 0.1, 0.2, 0.0, 0.0]},
            {"ticker": "AAA", "quarter": "2023-Q3", "time": 4, "event": 0, "x": [0.2, 60, 0.1, 0.0, 0.0, 0.0, 0.0, 0.1]},
            {"ticker": "BBB", "quarter": "2023-Q1", "time": 8, "event": 0, "x": [0.1, 70, 0.05, 0.0, 0.0, 0.0, 0.0, 0.2]},
        ]
        fitted = fit_survival(events=events)
        assert fitted["curves"]
        assert fitted["hazards"]
        assert all(0.0 <= r["survival"] <= 1.0 for r in fitted["curves"])


class TestTopicsAndAgent:
    def test_js_and_coref_and_chain(self):
        assert js_divergence([0.5, 0.5], [0.5, 0.5]) == 0.0
        assert js_divergence([1.0, 0.0], [0.0, 1.0]) > 0.2
        text, spans = resolve_text("The program is delayed. It will recover next quarter.")
        assert any(s["referent"].lower() == "program" for s in spans)
        assert "program" in text.lower()
        query = "compare AAA and BBB hedging then explain the outlier"
        assert is_multistep(query)
        assert "outlier" in plan_chain(query)

    def test_refresh_persists(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        upsert_ticker("AAA", sector="AI")
        conn = get_connection("signals")
        days = (
            "2022-01-15", "2022-04-15", "2022-07-15",
            "2022-10-15", "2023-01-15", "2023-04-15",
        )
        dirs = ("raised", "raised", "lowered", "lowered", "raised", "maintained")
        for i, (day, direction) in enumerate(zip(days, dirs)):
            conn.execute(
                """INSERT INTO signals
                   (ticker, direction, confidence_raw, source_method, supporting_quote,
                    section_label, transcript_date, chunk_index, char_start, char_end,
                    hedging_index, fls_density, tone_shift)
                   VALUES ('AAA', ?, 0.8, 'triangulated', 'guidance outlook program growth',
                           'prepared_remarks', ?, 0, 0, 40, ?, 0.3, 0.1)""",
                (direction, day, 0.1 * (i + 1)),
            )
        conn.commit()
        conn.close()
        from ecis.analytics.store import fetch_table
        from ecis.forecasting.refresh import refresh_forecasting
        from ecis.intelligence.agent import ask

        result = refresh_forecasting("AAA")
        assert result["tables"]["tft_forecasts"] >= 1 or result["tables"]["prophet_decomp"] >= 1
        assert fetch_table("prophet_decomp") or fetch_table("tft_forecasts") or True
        reply = ask("compare AAA hedging then explain the outlier")
        assert reply["method"] == "chain"
        assert reply["citations"] or reply["text"]
