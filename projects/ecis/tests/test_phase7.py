"""Phase 7: prompt boundary, boilerplate, ticker registry."""

from ecis.config.settings import settings
from ecis.db.init_db import init_all, insert_default_weights
from ecis.db.ticker_registry import get_ticker, list_tickers, upsert_ticker
from ecis.preprocessing.boilerplate import boilerplate_token_ratio, strip_boilerplate
from tests.local_import import load_ecis


def _init(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "db_dir", tmp_path)
    monkeypatch.setattr(settings, "raw_edgar_dir", tmp_path / "edgar")
    monkeypatch.setattr(settings, "raw_fmp_dir", tmp_path / "fmp")
    init_all()
    insert_default_weights()


def _keyword():
    return load_ecis("readers/keyword_reader.py", "ecis_keyword_reader")


class TestPromptBoundary:
    def test_reaffirm_is_maintained_not_empty(self):
        hit = _keyword().read_chunk("We are reaffirming guidance for the fiscal year.")
        assert hit["matched"] is True
        assert hit["direction"] == "maintained"

    def test_no_guidance_language_is_not_maintained(self):
        miss = _keyword().read_chunk("Thank you for joining the call today.")
        assert miss["matched"] is False


class TestBoilerplate:
    def test_safe_harbour_stripped(self):
        text = (
            "This release contains forward-looking statements under the safe harbor. "
            "We grew revenue 20 percent."
        )
        stripped = strip_boilerplate(text)
        assert "revenue" in stripped.lower()
        assert boilerplate_token_ratio(
            "forward-looking statements safe harbor Form 8-K risk factors"
        ) > 0.0


class TestTickerRegistry:
    def test_upsert_and_list(self, tmp_path, monkeypatch):
        _init(tmp_path, monkeypatch)
        upsert_ticker("AAA", company_name="Example Co", sector="AI")
        row = get_ticker("aaa")
        assert row is not None
        assert row["ticker"] == "AAA"
        assert row["sector"] == "AI"
        assert row["extraction_status"] == "pending"
        names = {r["ticker"] for r in list_tickers()}
        assert "AAA" in names

    def test_llama_mistral_and_chunk_defaults(self):
        assert settings.chunk_size_tokens == 400
        assert "mistral" in settings.llm_mistral_model
