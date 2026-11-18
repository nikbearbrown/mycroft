"""Sequence models, HMM regimes, analyst intelligence, lags, and hybrid RAG."""

from ecis.db.init_db import get_connection, init_all, insert_default_weights
from ecis.db.ticker_registry import upsert_ticker
from ecis.timeseries.alignment import lexical_similarity, pair_alignment
from ecis.timeseries.analysts import parse_analyst
from ecis.timeseries.difficulty import normalize_dodge, score_difficulty
from ecis.timeseries.hmm import fit_regimes
from ecis.timeseries.recurrent import fit_sequence_models


def _init(tmp_path, monkeypatch):
    from ecis.config.settings import settings

    monkeypatch.setattr(settings, "db_dir", tmp_path)
    monkeypatch.setattr(settings, "fmp_api_key", "")
    monkeypatch.setattr(settings, "normalised_dir", tmp_path / "normalised")
    settings.normalised_dir.mkdir(parents=True, exist_ok=True)
    init_all()
    insert_default_weights()


SAMPLE = """
We will grow revenue 12% in FY2025.

What is the outlook for next quarter guidance?

We will grow revenue 12% next quarter and are expanding into new markets.

Why should we believe that after the shortfall? You said last quarter you were committed.

As I said, we already covered that and I don't want to speculate.
"""


class TestSequenceAndHmm:
    def test_lstm_gru_probabilities(self):
        seqs = []
        for i, (q, target) in enumerate((
            ("2022-Q1", 0), ("2022-Q2", 0), ("2022-Q3", 1),
            ("2022-Q4", 1), ("2023-Q1", 0), ("2023-Q2", None),
        )):
            ramp = [0.1 * (i + 1)] * 9
            seqs.append({
                "ticker": "AAA",
                "quarter": q,
                "X": [ramp[:] for _ in range(4)],
                "target": target,
                "n_steps": 4,
            })
        result = fit_sequence_models(sequences=seqs)
        assert result["trained"]
        names = {r["model_name"] for r in result["predictions"]}
        assert "lstm" in names and "gru" in names
        assert all(0.0 <= r["probability"] <= 1.0 for r in result["predictions"])

    def test_hmm_three_regimes(self):
        series = {"AI": [
            {"quarter": "2021-Q1", "mood_score": -0.5},
            {"quarter": "2021-Q2", "mood_score": -0.4},
            {"quarter": "2021-Q3", "mood_score": 0.0},
            {"quarter": "2021-Q4", "mood_score": 0.05},
            {"quarter": "2022-Q1", "mood_score": 0.45},
            {"quarter": "2022-Q2", "mood_score": 0.5},
        ]}
        rows = fit_regimes(series=series)
        labels = {r["regime"] for r in rows}
        assert labels <= {"bearish", "transitional", "bullish"}
        assert len(labels) >= 2
        assert abs(sum(rows[0][k] for k in ("p_bearish", "p_transitional", "p_bullish")) - 1.0) < 0.05


class TestAnalyst:
    def test_identity_difficulty_alignment(self):
        assert ident["display_name"] == " "
        assert "Contoso" in ident["firm"]
        hard = score_difficulty("Why should we believe that after the shortfall? You said last quarter you were committed.")
        easy = score_difficulty("Just to confirm last quarter margins?")
        assert hard["difficulty"] > easy["difficulty"]
        assert normalize_dodge(0.6, 0.9) < normalize_dodge(0.6, 0.3)
        close = pair_alignment("outlook for next quarter guidance", "outlook for next quarter guidance growth")
        pivot = pair_alignment("what are the risks next quarter", "we see tremendous opportunity in new markets")
        assert close["similarity"] > pivot["similarity"]
        assert lexical_similarity("outlook guidance", "outlook guidance") == 1.0


class TestRefresh:
    def test_persists(self, tmp_path, monkeypatch):
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
                   VALUES ('AAA', ?, 0.8, 'triangulated', 'quote', 'prepared_remarks',
                           ?, 0, 0, 20, ?, 0.3, 0.1)""",
                (direction, day, 0.1 * (i + 1)),
            )
        conn.commit()
        conn.close()
        folder = tmp_path / "normalised" / "AAA"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "AAA_2023-04-15.txt").write_text(SAMPLE, encoding="utf-8")
        from ecis.analytics.store import fetch_table
        from ecis.intelligence.agent import ask
        from ecis.timeseries.refresh import refresh_timeseries

        result = refresh_timeseries("AAA")
        assert result["tables"]["lag_features"] >= 1
        assert result["tables"]["momentum_features"] >= 1
        assert fetch_table("lag_features")
        assert fetch_table("question_difficulty")
        reply = ask("what was AAA dodge score last quarter")
        assert reply["intent"] == "retrieval"
        assert reply["retrieval"] in {"hybrid", "structured"}
