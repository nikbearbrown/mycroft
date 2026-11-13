"""Persist sequence models, regimes, analyst intelligence, and lag/momentum snapshots."""

from __future__ import annotations

from typing import Any

from ecis.analytics.store import replace_rows
from ecis.timeseries.alignment import score_alignment
from ecis.timeseries.analysts import build_profiles
from ecis.timeseries.difficulty import score_questions
from ecis.timeseries.hmm import fit_regimes
from ecis.timeseries.lag_features import engineer_lags
from ecis.timeseries.momentum import engineer_momentum
from ecis.timeseries.recurrent import fit_sequence_models


def refresh_timeseries(ticker: str | None = None) -> dict[str, Any]:
    models = fit_sequence_models(ticker)
    regimes = fit_regimes(ticker)
    profiles = build_profiles(ticker)
    difficulty = score_questions(ticker)
    alignment = score_alignment(ticker)
    lags = engineer_lags(ticker)
    momentum = engineer_momentum(ticker)

    counts = {
        "sequence_predictions": replace_rows(
            "sequence_predictions",
            models.get("predictions") or [],
            ("ticker", "quarter", "model_name", "probability", "predicted", "actual", "hidden_norm", "n_steps", "method"),
        ),
        "sequence_comparison": replace_rows(
            "sequence_comparison",
            models.get("comparison") or [],
            ("model_name", "accuracy", "auc", "brier", "n", "method"),
        ),
        "market_regimes": replace_rows(
            "market_regimes",
            regimes,
            ("sector", "quarter", "regime", "p_bearish", "p_transitional", "p_bullish", "emission", "method"),
        ),
        "analyst_profiles": replace_rows(
            "analyst_profiles",
            profiles,
            (
                "analyst_key", "display_name", "firm", "n_questions", "follow_up_rate",
                "complexity", "tone", "bullish_score", "tough_score", "forward_looking",
                "backward_looking", "clarification", "confrontational", "stance",
            ),
        ),
        "question_difficulty": replace_rows(
            "question_difficulty",
            difficulty,
            (
                "ticker", "transcript_date", "quarter", "pair_index", "analyst_key",
                "question_type", "difficulty", "specificity", "dodge", "dodge_normalized",
            ),
        ),
        "analyst_alignment": replace_rows(
            "analyst_alignment",
            alignment,
            ("ticker", "quarter", "transcript_date", "analyst_key", "question_type", "similarity", "expected", "alignment", "flag", "method"),
        ),
        "lag_features": replace_rows(
            "lag_features",
            lags,
            ("ticker", "quarter", "feature", "lag", "value", "selected"),
        ),
        "momentum_features": replace_rows(
            "momentum_features",
            momentum,
            ("ticker", "quarter", "signal_type", "level", "momentum", "acceleration", "zscore", "regime"),
        ),
    }
    return {"ticker": ticker, "tables": counts, "trained": models.get("trained"), "method": models.get("method")}
