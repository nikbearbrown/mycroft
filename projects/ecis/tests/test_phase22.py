from ecis.db.init_db import get_connection, init_all, insert_default_weights
from ecis.db.ticker_registry import upsert_ticker
from ecis.graph_models.arguments import mine_sentence
from ecis.graph_models.entity_link import link_text
from ecis.graph_models.gat import run_gat
from ecis.graph_models.summarize import summarize_calls
from ecis.graph_models.vae import detect_anomalies
from ecis.graph_models.wavelet import haar_levels


def _init(tmp_path, monkeypatch):
    from ecis.config.settings import settings

    monkeypatch.setattr(settings, "db_dir", tmp_path)
    monkeypatch.setattr(settings, "fmp_api_key", "")
    monkeypatch.setattr(settings, "normalised_dir", tmp_path / "normalised")
    settings.normalised_dir.mkdir(parents=True, exist_ok=True)
    init_all()
    insert_default_weights()


class TestGraphModels:
    def test_gat_attention(self):
        graph = {
            "nodes": [
                {"ticker": "AAA", "vector": [0.8] * 9, "target": 1, "quarter": "2023-Q1"},
                {"ticker": "BBB", "vector": [0.1] * 9, "target": 0, "quarter": "2023-Q1"},
                {"ticker": "CCC", "vector": [0.2] * 9, "target": 0, "quarter": "2023-Q1"},
            ],
            "edges": [
                {"src": "AAA", "dst": "BBB", "kind": "sector", "weight": 0.5, "lag": 0, "granger_r": 0.4},
                {"src": "BBB", "dst": "CCC", "kind": "supply", "weight": 0.6, "lag": 1, "granger_r": 0.3},
            ],
        }
        result = run_gat(graph=graph)
        assert result["edges"]
        assert all(0.0 <= e["attention"] <= 1.0 for e in result["edges"])
        assert any(e["src"] == "AAA" and e["dst"] == "BBB" for e in result["edges"])
        aaa = next(n for n in result["nodes"] if n["ticker"] == "AAA")
        assert aaa["n_neighbors"] >= 1
        assert aaa["embedding"]

    def test_vae_outlier_flag(self):
        import numpy as np

        rng = np.random.default_rng(0)
        X = rng.normal(0, 0.1, (20, 9))
        X[-1] = 8.0
        rows = detect_anomalies(matrix=X)
        assert any(r["flag"] == "anomaly" for r in rows)
        assert rows[-1]["flag"] == "anomaly"
        assert rows[-1]["recon_error"] > rows[0]["recon_error"]

    def test_entity_link_aaa(self):
        hits = link_text(
            "We compete with AAA on the enterprise pipeline.",
            "BBB",
            {"aaa": ("AAA", 0.95)},
        )
        assert hits
        assert hits[0]["linked_ticker"] == "AAA"
        assert hits[0]["confidence"] >= 0.9

    def test_summary_paragraphs_argument_wavelet(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        upsert_ticker("AAA", company_name="Alpha Analytics", sector="AI")
        conn = get_connection("signals")
        quote = (
            "We expect revenue growth to accelerate, driven by 40% increase in enterprise pipeline. "
            "Guidance outlook remains raised for the year. Hedging language is limited this quarter. "
            "The program will recover next quarter after delayed shipments."
        )
        conn.execute(
            """INSERT INTO signals
               (ticker, direction, confidence_raw, source_method, supporting_quote,
                section_label, transcript_date, chunk_index, char_start, char_end,
                hedging_index, fls_density, tone_shift)
               VALUES ('AAA', 'raised', 0.8, 'triangulated', ?,
                       'prepared_remarks', '2023-01-15', 0, 0, 80, 0.2, 0.3, 0.1)""",
            (quote,),
        )
        conn.commit()
        conn.close()
        rows = summarize_calls("AAA")
        assert rows
        paras = [p for p in (rows[0]["abstractive"] or "").split("\n\n") if p.strip()]
        assert len(paras) >= 3
        mined = mine_sentence(
            "We expect revenue growth to accelerate, driven by 40% increase in enterprise pipeline."
        )
        assert mined is not None
        assert "expect" in mined["claim"].lower()
        assert mined["evidence"]
        assert mined["strength"] > 0.5
        parts = haar_levels([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
        assert len(parts["low"]) == 8
        assert len(parts["mid"]) == 8
        assert len(parts["high"]) == 8


class TestRefresh:
    def test_refresh_persists(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        upsert_ticker("AAA", company_name="Alpha Analytics", sector="AI")
        upsert_ticker("BBB", company_name="Beta Systems", sector="AI")
        conn = get_connection("signals")
        days = (
            "2022-01-15", "2022-04-15", "2022-07-15",
            "2022-10-15", "2023-01-15", "2023-04-15",
        )
        dirs = ("raised", "raised", "lowered", "lowered", "raised", "maintained")
        for i, (day, direction) in enumerate(zip(days, dirs)):
            quote = (
                f"We expect guidance outlook to hold. Driven by {10 + i} percent pipeline. "
                f"BBB remains a competitor this quarter."
            )
            conn.execute(
                """INSERT INTO signals
                   (ticker, direction, confidence_raw, source_method, supporting_quote,
                    section_label, transcript_date, chunk_index, char_start, char_end,
                    hedging_index, fls_density, tone_shift)
                   VALUES ('AAA', ?, 0.8, 'triangulated', ?,
                           'prepared_remarks', ?, 0, 0, 80, ?, 0.3, 0.1)""",
                (direction, quote, day, 0.1 * (i + 1)),
            )
            conn.execute(
                """INSERT INTO signals
                   (ticker, direction, confidence_raw, source_method, supporting_quote,
                    section_label, transcript_date, chunk_index, char_start, char_end,
                    hedging_index, fls_density, tone_shift)
                   VALUES ('BBB', ?, 0.7, 'triangulated', 'We expect demand. Driven by 12 percent growth.',
                           'prepared_remarks', ?, 0, 0, 40, ?, 0.2, 0.05)""",
                (direction, day, 0.05 * (i + 1)),
            )
        conn.commit()
        conn.close()
        from ecis.analytics.store import fetch_table
        from ecis.graph_models.refresh import refresh_graph_models

        result = refresh_graph_models("AAA")
        assert result["tables"]["graph_nodes"] >= 1
        assert result["tables"]["call_summaries"] >= 1
        assert result["domain_lm"]["skipped"] is True
        assert fetch_table("graph_nodes")
        assert fetch_table("arguments") or fetch_table("call_summaries")
        mentions = fetch_table("entity_mentions")
        assert any(m.get("linked_ticker") == "BBB" for m in mentions)
        wave = fetch_table("wavelet_components")
        assert wave
        assert all(r.get("method") == "haar" for r in wave)
