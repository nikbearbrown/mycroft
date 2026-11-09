"""Phase 1: environment, credentials template, and package layout."""

from pathlib import Path

from ecis.config.settings import settings

ROOT = Path(__file__).resolve().parents[1]


class TestEnvironment:
    def test_core_rate_limits(self):
        assert settings.edgar_requests_per_second == 10
        assert settings.fmp_daily_limit == 250

    def test_env_example_lists_keys(self):
        example = ROOT / "src" / "ecis" / ".env.example"
        text = example.read_text(encoding="utf-8")
        assert "EDGAR_USER_AGENT" in text
        assert "FMP_API_KEY" in text
        assert "OLLAMA_BASE_URL" in text

    def test_module_layout_exists(self):
        pkg = ROOT / "src" / "ecis"
        for name in (
            "ingestion", "preprocessing", "readers", "extraction",
            "graphs", "db", "config", "scripts",
        ):
            assert (pkg / name).is_dir()

    def test_ensure_dirs(self, tmp_path, monkeypatch):
        monkeypatch.setattr(settings, "data_dir", tmp_path / "data")
        monkeypatch.setattr(settings, "raw_edgar_dir", tmp_path / "data" / "raw" / "edgar")
        monkeypatch.setattr(settings, "raw_fmp_dir", tmp_path / "data" / "raw" / "fmp")
        monkeypatch.setattr(settings, "cleaned_dir", tmp_path / "data" / "processed" / "cleaned")
        monkeypatch.setattr(settings, "normalised_dir", tmp_path / "data" / "processed" / "normalised")
        monkeypatch.setattr(settings, "chunks_dir", tmp_path / "data" / "processed" / "chunks")
        monkeypatch.setattr(settings, "db_dir", tmp_path / "data" / "db")
        settings.ensure_dirs()
        assert settings.raw_edgar_dir.is_dir()
        assert settings.raw_fmp_dir.is_dir()
        assert settings.db_dir.is_dir()
