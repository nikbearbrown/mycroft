"""Phase 16: Q&A dodge, market-share language, guidance-revision models."""

from ecis.guidance_models.dodge import aggregate_dodge, score_pair
from ecis.guidance_models.finbert_ensemble import lexicon_polarity
from ecis.guidance_models.market_share import ensemble_market_share, lexicon_score
from ecis.guidance_models.qa_parser import parse_qa
from ecis.guidance_models.question_types import classify_question
from ecis.guidance_models.reranker import lexical_relevance, relevance_score
from ecis.guidance_models.sbert import finetune_status
from ecis.db.init_db import get_connection, init_all, insert_default_weights
from ecis.db.ticker_registry import upsert_ticker


def _init(tmp_path, monkeypatch):
    from ecis.config.settings import settings

    monkeypatch.setattr(settings, "db_dir", tmp_path)
    monkeypatch.setattr(settings, "fmp_api_key", "")
    monkeypatch.setattr(settings, "normalised_dir", tmp_path / "normalised")
    settings.normalised_dir.mkdir(parents=True, exist_ok=True)
    init_all()
    insert_default_weights()


SAMPLE = """
[SECTION: prepared_remarks]
[SPEAKER: Jane Doe, CEO]
We will grow revenue 12% in FY2025.

[SECTION: qa]
[SPEAKER: Alex Smith, Analyst]
What is the outlook for next quarter guidance?

[SPEAKER: Jane Doe, CEO]
We will grow revenue 12% next quarter and are expanding into new markets.

[SPEAKER: Alex Smith, Analyst]
Why should we believe that after the shortfall? Can you justify the miss?

[SPEAKER: Pat Lee, CFO]
As I said, we already covered that and I don't want to speculate.

[SPEAKER: Alex Smith, Analyst]
Just to confirm last quarter margins?

[SPEAKER: Pat Lee, CFO]
Last quarter operating margin was 18%.
"""


class TestQAParser:
    def test_pairs_questions_with_answers(self):
        pairs = parse_qa(SAMPLE, ticker="AAA", transcript_date="2024-01-15")
        assert len(pairs) >= 2
        assert pairs[0]["question"]
        assert pairs[0]["answer"]
        assert pairs[0]["answer_role"] in {"ceo", "cfo"}
        assert pairs[0]["char_end"] >= pairs[0]["char_start"]


class TestQuestionTypesAndDodge:
    def test_types(self):
        assert classify_question("What is the outlook for next quarter guidance?") == "forward-looking"
        assert classify_question("Why should we believe that after the shortfall?") == "confrontational"
        assert classify_question("Just to confirm last quarter margins?") in {"clarification", "backward-looking"}

    def test_lexical_relevance_and_dodge(self):
        rel, method = relevance_score("outlook guidance next quarter", "outlook guidance next quarter growth")
        assert method == "lexical"
        assert rel > lexical_relevance("outlook", "unrelated weather")
        row = score_pair({
            "ticker": "AAA",
            "transcript_date": "2024-01-15",
            "question": "Why should we believe that after the shortfall?",
            "answer": "As I said, we already covered that and I don't want to speculate.",
            "answer_role": "cfo",
        })
        assert row["question_type"] == "confrontational"
        assert row["dodge"] > 0.2

    def test_aggregate_flags(self):
        pairs = parse_qa(SAMPLE, ticker="AAA", transcript_date="2024-01-15")
        rows = aggregate_dodge(pairs)
        calls = [r for r in rows if r["scope"] == "call"]
        assert calls
        assert calls[0]["dodge"] is not None


class TestMarketShare:
    def test_lexicon_and_ensemble(self):
        off = lexicon_score("We are gaining share and expanding into new markets.")
        deff = lexicon_score("We are protecting margins and holding steady.")
        assert off["score"] > deff["score"]
        ens = ensemble_market_share("We are gaining share and expanding into new markets.")
        assert ens["label"] in {"offensive", "neutral"}
        assert ens["agreement"] >= 0
        assert lexicon_polarity("strong growth beat") > 0


class TestRevision:
    def test_features_and_models(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        upsert_ticker("AAA", sector="AI")
        conn = get_connection("signals")
        days = [
            ("2023-01-15", "raised", 0.2, 0.6, 0.3),
            ("2023-04-15", "raised", 0.25, 0.5, 0.2),
            ("2023-07-15", "maintained", 0.4, 0.3, 0.0),
            ("2023-10-15", "lowered", 0.6, 0.2, -0.3),
            ("2024-01-15", "lowered", 0.55, 0.25, -0.2),
        ]
        for day, direction, hedge, fls, tone in days:
            conn.execute(
                """INSERT INTO signals
                   (ticker, direction, confidence_raw, source_method, supporting_quote,
                    section_label, transcript_date, chunk_index, char_start, char_end,
                    hedging_index, fls_density, tone_shift)
                   VALUES ('AAA', ?, 0.8, 'triangulated', 'We will grow revenue 12%.',
                           'prepared_remarks', ?, 0, 0, 40, ?, ?, ?)""",
                (direction, day, hedge, fls, tone),
            )
        conn.commit()
        conn.close()

        from ecis.guidance_models.revision_features import build_revision_rows
        from ecis.guidance_models.revision_models import train_revision_models

        rows = build_revision_rows("AAA")
        assert any(r["target"] in {0, 1} for r in rows)
        result = train_revision_models("AAA")
        assert result["trained"] is True
        assert result["primary"] in result["importances"]
        assert result["naive_brier"] is not None


class TestRefresh:
    def test_refresh_and_sbert_skip(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        upsert_ticker("AAA", sector="AI")
        folder = tmp_path / "normalised" / "AAA"
        folder.mkdir(parents=True)
        (folder / "2024-01-15.txt").write_text(SAMPLE, encoding="utf-8")
        conn = get_connection("signals")
        conn.execute(
            """INSERT INTO signals
               (ticker, direction, confidence_raw, source_method, supporting_quote,
                section_label, transcript_date, chunk_index, char_start, char_end)
               VALUES ('AAA', 'raised', 0.8, 'triangulated', 'gaining share',
                       'prepared_remarks', '2024-01-15', 0, 0, 40)"""
        )
        conn.commit()
        conn.close()
        from ecis.guidance_models.refresh import refresh_guidance_models
        from ecis.analytics.store import fetch_table

        result = refresh_guidance_models("AAA")
        assert result["tables"]["qa_pairs"] >= 1
        assert result["tables"]["dodge_scores"] >= 1
        assert fetch_table("dodge_scores")
        assert finetune_status()["skipped"] is True
