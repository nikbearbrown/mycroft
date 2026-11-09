"""Phase 4: pipeline routing, outcomes, Scorecard, recalibration, API."""

import pytest

from ecis.graphs.orchestration_agent import classify_chunks
from ecis.schemas.signal import FastPassResult, GuidanceDirection
from ecis.schemas.state import EscalationCategory
from ecis.scoring.metrics import brier_score, expected_calibration_error, skill_score
from tests.local_import import load_ecis, stub_module


def _outcomes():
    stub_module("yfinance", download=lambda *a, **k: None, Ticker=type("T", (), {}))
    return load_ecis("scoring/outcome_resolver.py", "ecis_outcome_resolver")


class TestPipelineRouting:
    def test_partition_by_category(self):
        rows = [
            FastPassResult(
                chunk_index=0, chunk_text="a",
                keyword_matched=True, keyword_direction=GuidanceDirection.RAISED,
                finbert_direction=GuidanceDirection.RAISED, finbert_confidence=0.9,
            ),
            FastPassResult(chunk_index=1, chunk_text="b"),
        ]
        cats = classify_chunks(rows)
        assert 0 in cats[EscalationCategory.A]
        assert 1 in cats[EscalationCategory.D]


class TestOutcomesAndScorecard:
    def test_horizons_and_grading(self):
        mod = _outcomes()
        assert mod.HORIZONS == (30, 90, 180)
        assert mod._evaluate_correctness("raised", 0.04) == 1
        assert mod._evaluate_correctness("raised", -0.04) == 0
        assert mod._evaluate_correctness("lowered", -0.04) == 1
        assert mod._evaluate_correctness("maintained", 0.01) == 1
        assert mod._evaluate_correctness("raised", 0.001) is None

    def test_brier_skill_ece(self):
        brier = brier_score([0.9, 0.8, 0.2], [1, 1, 0])
        assert 0 <= brier < 0.1
        assert skill_score(0.1, 0.2) == 0.5
        ece, bins = expected_calibration_error([0.9, 0.1], [1, 0], n_bins=2)
        assert ece < 0.2
        assert len(bins) == 2


class TestRecalibration:
    def test_platt_needs_samples(self, tmp_path, monkeypatch):
        pytest.importorskip("sklearn")
        from ecis.config.settings import settings
        from ecis.db.init_db import init_all
        from ecis.scoring.recalibrator import fit_platt

        monkeypatch.setattr(settings, "db_dir", tmp_path)
        init_all()
        result = fit_platt()
        assert result["fitted"] is False
        assert result["n_samples"] < 10


class TestAPI:
    def test_health_and_routes(self):
        pytest.importorskip("fastapi")
        from fastapi.testclient import TestClient

        from ecis.api.app import app

        client = TestClient(app)
        assert client.get("/health").json() == {"status": "ok"}
        paths = {getattr(r, "path", "") for r in app.routes}
        assert "/signals" in paths
        assert "/scores" in paths or "/scorecard" in paths
