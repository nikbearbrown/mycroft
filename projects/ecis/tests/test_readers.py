"""Tests for the keyword, NER, and preprocessing readers.

FinBERT and LLM reader tests are skipped if models are not available.
"""

import pytest

from ecis.readers.keyword_reader import read_chunk as keyword_read


class TestKeywordReader:
    def test_raised_detection(self):
        text = "We are raising guidance for the full year based on strong demand."
        result = keyword_read(text)
        assert result["matched"] is True
        assert result["direction"] == "raised"
        assert result["confidence"] == 1.0
        assert len(result["phrases"]) > 0

    def test_lowered_detection(self):
        text = "Due to macro headwinds, we are lowering guidance for Q4."
        result = keyword_read(text)
        assert result["matched"] is True
        assert result["direction"] == "lowered"

    def test_maintained_detection(self):
        text = "We are reaffirming guidance for the fiscal year."
        result = keyword_read(text)
        assert result["matched"] is True
        assert result["direction"] == "maintained"

    def test_no_match(self):
        text = "Revenue grew 15% year over year driven by cloud adoption."
        result = keyword_read(text)
        assert result["matched"] is False
        assert result["direction"] is None
        assert result["confidence"] == 0.0

    def test_multiple_matches_same_direction(self):
        text = "We are raising guidance and increasing our outlook for the year."
        result = keyword_read(text)
        assert result["matched"] is True
        assert result["direction"] == "raised"
        assert len(result["phrases"]) >= 2

    def test_case_insensitivity(self):
        text = "RAISING GUIDANCE for Q3."
        result = keyword_read(text)
        assert result["matched"] is True
        assert result["direction"] == "raised"


class TestNERReader:
    def test_entity_extraction(self):
        from ecis.readers.ner_reader import read_chunk as ner_read

        text = (
            "The company reported revenue of $35.1 billion in Q2 2025, "
            "with operating margin expanding to 62%. "
            "The CEO highlighted strong data centre demand."
        )
        entities = ner_read(text)

        assert isinstance(entities, dict)
        assert "companies" in entities
        assert "money" in entities
        assert "percentages" in entities
        assert "dates" in entities
        assert "metrics" in entities

        assert len(entities["money"]) > 0 or len(entities["percentages"]) > 0

    def test_financial_metrics(self):
        from ecis.readers.ner_reader import read_chunk as ner_read

        text = "Free cash flow improved and earnings per share exceeded expectations."
        entities = ner_read(text)
        metrics = [m.lower() for m in entities["metrics"]]
        assert any("free cash flow" in m for m in metrics)
        assert any("earnings per share" in m or "eps" in m for m in metrics)


class TestPreprocessing:
    def test_cleaner_html(self):
        from ecis.preprocessing.cleaner import clean_edgar_html

        html = """
        <html><body>
        <script>var x = 1;</script>
        <p>Good morning everyone. Welcome to the Q2 earnings call.</p>
        <p>We are pleased to report strong results.</p>
        </body></html>
        """
        cleaned = clean_edgar_html(html)
        assert "Good morning" in cleaned
        assert "<script>" not in cleaned
        assert "<p>" not in cleaned

    def test_cleaner_fmp_json(self):
        import json
        from ecis.preprocessing.cleaner import clean_fmp_json

        data = [{"content": "This is the transcript content."}]
        cleaned = clean_fmp_json(json.dumps(data))
        assert "transcript content" in cleaned

    def test_normaliser_sections(self):
        from ecis.preprocessing.normaliser import normalise_transcript

        text = (
            "Good morning and welcome to the earnings call.\n\n"
            "We are pleased with our results.\n\n"
            "We will now open the line for questions.\n\n"
            "Analyst: What is your outlook for next quarter?"
        )
        normalised = normalise_transcript(text)
        assert "[SECTION: prepared_remarks]" in normalised
        assert "[SECTION: qa]" in normalised
