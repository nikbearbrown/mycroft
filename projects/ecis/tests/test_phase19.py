"""Uncertainty, contagion, lags, and the conversational agent."""

from ecis.db.init_db import get_connection, init_all, insert_default_weights
from ecis.db.ticker_registry import upsert_ticker
from ecis.intelligence.conformal import conformal_intervals
from ecis.intelligence.disagreement import ensemble_disagreement
from ecis.intelligence.intent import parse_intent
from ecis.intelligence.selective import decide_abstention
from ecis.intelligence.supply_chain import upsert_link


def _init(tmp_path, monkeypatch):
    from ecis.config.settings import settings

    monkeypatch.setattr(settings, "db_dir", tmp_path)
    monkeypatch.setattr(settings, "fmp_api_key", "")
    monkeypatch.setattr(settings, "normalised_dir", tmp_path / "normalised")
    settings.normalised_dir.mkdir(parents=True, exist_ok=True)
    init_all()
    insert_default_weights()


def _pred(ticker, quarter, model, prob, actual):
    conn = get_connection("agents")
    conn.execute(
        """INSERT INTO revision_predictions
           (ticker, quarter, model_name, probability, predicted, actual)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (ticker, quarter, model, prob, int(prob >= 0.5), actual),
    )
    conn.commit()
    conn.close()


class TestUncertainty:
    def test_conformal_and_disagreement(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        for q, p, a in (("2023Q1", 0.8, 1), ("2023Q2", 0.7, 1), ("2023Q3", 0.4, 0), ("2023Q4", 0.9, 1)):
            _pred("AAA", q, "logistic", p, a)
            _pred("AAA", q, "mlp", p - 0.15, a)
        rows = conformal_intervals("AAA")
        assert rows
        assert all(r["lower"] <= r["probability"] <= r["upper"] for r in rows)
        dis = ensemble_disagreement("AAA")
        assert dis
        assert dis[0]["n_models"] >= 2
        sel = decide_abstention(rows, [], dis)
        assert sel

    def test_intent_routing(self):
        assert parse_intent("what was AAA dodge score last quarter")["intent"] == "retrieval"
        cmp = parse_intent("compare AAA and BBB hedging")
        assert cmp["intent"] == "comparison"
        assert "AAA" in cmp["tickers"] and "BBB" in cmp["tickers"]
        assert parse_intent("which companies show deterioration")["intent"] == "analysis"
        assert parse_intent("why was AAA flagged")["intent"] == "explanation"


class TestContagionAndLag:
    def test_supply_link_and_lag_refresh(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        upsert_ticker("AAA", sector="AI")
        upsert_ticker("BBB", sector="AI")
        upsert_link("AAA", "BBB")
        conn = get_connection("signals")
        for i, day in enumerate(("2023-01-15", "2023-04-15", "2023-07-15", "2023-10-15")):
            conn.execute(
                """INSERT INTO signals
                   (ticker, direction, confidence_raw, source_method, supporting_quote,
                    section_label, transcript_date, chunk_index, char_start, char_end,
                    hedging_index, fls_density, tone_shift)
                   VALUES ('AAA', 'raised', 0.8, 'triangulated', 'quote', 'prepared_remarks',
                           ?, 0, 0, 20, ?, 0.3, 0.1)""",
                (day, 0.1 * (i + 1)),
            )
            conn.execute(
                """INSERT INTO signals
                   (ticker, direction, confidence_raw, source_method, supporting_quote,
                    section_label, transcript_date, chunk_index, char_start, char_end,
                    hedging_index, fls_density, tone_shift)
                   VALUES ('BBB', 'raised', 0.7, 'triangulated', 'quote', 'prepared_remarks',
                           ?, 0, 0, 20, ?, 0.2, 0.0)""",
                (day, 0.08 * (i + 1)),
            )
        sid = conn.execute("SELECT signal_id FROM signals LIMIT 1").fetchone()[0]
        conn.commit()
        conn.close()
        conn = get_connection("outcomes")
        conn.execute(
            """INSERT INTO outcomes
               (signal_id, horizon_days, excess_return, correct, transcript_date, ret_same_day)
               VALUES (?, 30, 0.02, 1, '2023-01-15', 0.01)""",
            (sid,),
        )
        conn.commit()
        conn.close()
        from ecis.analytics.store import fetch_table
        from ecis.intelligence.refresh import refresh_intelligence

        result = refresh_intelligence()
        assert result["tables"]["temporal_lags"] >= 1
        assert fetch_table("temporal_lags")
        from ecis.intelligence.agent import ask
        reply = ask("why was AAA flagged")
        assert reply["intent"] == "explanation"
        assert reply["session_id"]
