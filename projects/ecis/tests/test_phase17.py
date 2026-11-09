"""Phase 17: decay by type, false positives, chains, quality, linguistic depth."""

from ecis.db.init_db import get_connection, init_all, insert_default_weights
from ecis.db.ticker_registry import upsert_ticker
from ecis.depth.call_quality import score_text
from ecis.depth.chaining import chain_signals
from ecis.depth.decay_by_type import analyse_decay, half_life
from ecis.depth.discourse import classify_trajectory
from ecis.depth.false_positives import analyse_false_positives, matches_fp_pattern
from ecis.depth.metaphor import density, metaphor_hits
from ecis.depth.sarcasm import score_exchange
from ecis.depth.speech_acts import classify_sentence


def _init(tmp_path, monkeypatch):
    from ecis.config.settings import settings

    monkeypatch.setattr(settings, "db_dir", tmp_path)
    monkeypatch.setattr(settings, "fmp_api_key", "")
    monkeypatch.setattr(settings, "normalised_dir", tmp_path / "normalised")
    settings.normalised_dir.mkdir(parents=True, exist_ok=True)
    init_all()
    insert_default_weights()


def _signal(ticker, day, direction="raised", conf=0.85, quote="We will deliver revenue growth.", section="prepared_remarks", hedge=0.2, tone=0.3, fls=0.5):
    conn = get_connection("signals")
    conn.execute(
        """INSERT INTO signals
           (ticker, direction, confidence_raw, source_method, supporting_quote,
            section_label, transcript_date, chunk_index, char_start, char_end,
            hedging_index, fls_density, tone_shift)
           VALUES (?, ?, ?, 'triangulated', ?, ?, ?, 0, 0, 40, ?, ?, ?)""",
        (ticker, direction, conf, quote, section, day, hedge, fls, tone),
    )
    conn.commit()
    sid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return sid


class TestDecay:
    def test_half_life(self):
        assert half_life([(1, 0.5), (5, 0.4), (10, 0.1), (30, 0.05)]) == 10
        assert half_life([(1, 0.05), (5, 0.04)]) is None

    def test_analyse_decay(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        upsert_ticker("AAA", sector="AI")
        sid = _signal("AAA", "2024-01-15")
        conn = get_connection("outcomes")
        conn.execute(
            """INSERT INTO outcomes
               (signal_id, horizon_days, excess_return, correct, transcript_date, ret_same_day)
               VALUES (?, 30, 0.04, 1, '2024-01-15', 0.02)""",
            (sid,),
        )
        conn.commit()
        conn.close()
        rows = analyse_decay("AAA")
        assert {r["signal_type"] for r in rows} >= {"hedging_index", "confidence"}


class TestFalsePositivesAndChains:
    def test_fp_pattern_and_cluster(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        upsert_ticker("AAA", sector="AI")
        sid = _signal("AAA", "2024-01-15", quote="We may approximately see upside.", conf=0.9)
        conn = get_connection("outcomes")
        conn.execute(
            """INSERT INTO outcomes (signal_id, horizon_days, excess_return, correct, transcript_date)
               VALUES (?, 30, -0.04, 0, '2024-01-15')""",
            (sid,),
        )
        conn.commit()
        conn.close()
        assert matches_fp_pattern("We may approximately see upside.")
        rows = analyse_false_positives("AAA")
        assert rows
        assert rows[0]["root_cause"] == "ambiguous_language"
        assert rows[0]["confidence_modifier"] == 0.75

    def test_deterioration_chain(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        upsert_ticker("AAA", sector="AI")
        _signal("AAA", "2023-01-15", hedge=0.1, conf=0.9)
        _signal("AAA", "2023-04-15", hedge=0.3, conf=0.7)
        _signal("AAA", "2023-07-15", hedge=0.5, conf=0.4)
        chains = chain_signals("AAA")
        assert chains
        assert chains[0]["hedging_streak"] >= 2


class TestLinguistic:
    def test_quality_speech_discourse_metaphor_sarcasm(self):
        text = (
            "[SECTION: prepared_remarks]\n[SPEAKER: CEO]\n"
            "We will deliver growth. We expect margin expansion.\n"
            "[SECTION: qa]\n[SPEAKER: Analyst]\nWhy should we believe the shortfall?\n"
            "[SPEAKER: CFO]\nSure, we are pleased with the result."
        )
        q = score_text(text)
        assert q["completeness"] == 1.0
        assert q["flag"] in {"ok", "low_quality"}
        assert classify_sentence("We will deliver the plan.") == "promise"
        assert classify_sentence("We hope to expand next year.") == "hedged_intention"
        assert classify_sentence("It remains to be seen.") == "deflection"
        assert classify_trajectory([-0.4, 0.0, 0.4]) == "front_load"
        assert classify_trajectory([0.3, -0.4, 0.3]) == "bury"
        assert "headwind" in metaphor_hits("Macro headwinds hit the pipeline.")
        assert density("headwinds tailwinds runway") > 0
        rec = score_exchange("Why should we believe that after the shortfall?", "Sure, we are pleased.")
        assert rec["sarcastic"] == 1


class TestRefresh:
    def test_persists(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        upsert_ticker("AAA", sector="AI")
        folder = tmp_path / "normalised" / "AAA"
        folder.mkdir(parents=True)
        (folder / "2024-01-15.txt").write_text(
            "[SECTION: prepared_remarks]\n[SPEAKER: CEO]\nWe will deliver growth.\n"
            "[SECTION: qa]\n[SPEAKER: Analyst]\nWhat is the outlook?\n"
            "[SPEAKER: CEO]\nWe expect revenue to grow 12%.\n",
            encoding="utf-8",
        )
        sid = _signal("AAA", "2024-01-15")
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
        from ecis.depth.refresh import refresh_depth

        result = refresh_depth("AAA")
        assert result["tables"]["signal_decay_types"] >= 1
        assert fetch_table("signal_decay_types")
        assert fetch_table("speech_acts")
