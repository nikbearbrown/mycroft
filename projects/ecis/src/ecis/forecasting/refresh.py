"""Persist TFT, Prophet, survival, topics, coreference, and topic-shift snapshots."""

from __future__ import annotations

from typing import Any

from ecis.analytics.store import replace_rows
from ecis.forecasting.coref import resolve_pairs
from ecis.forecasting.prophet import decompose
from ecis.forecasting.survival import fit_survival
from ecis.forecasting.tft import fit_tft
from ecis.forecasting.topic_shift import track_shifts
from ecis.forecasting.topics import fit_topics


def refresh_forecasting(ticker: str | None = None) -> dict[str, Any]:
    tft = fit_tft(ticker)
    prophet = decompose(ticker)
    survival = fit_survival(ticker)
    topics = fit_topics(ticker)
    shifts = track_shifts(topics)
    coref = resolve_pairs(ticker)

    counts = {
        "tft_forecasts": replace_rows(
            "tft_forecasts",
            tft.get("forecasts") or [],
            ("ticker", "quarter", "horizon", "p10", "p50", "p90", "probability", "attention", "selection", "method"),
        ),
        "prophet_decomp": replace_rows(
            "prophet_decomp",
            prophet,
            ("ticker", "signal_type", "quarter", "observed", "trend", "seasonality", "residual", "flag", "method"),
        ),
        "survival_curves": replace_rows(
            "survival_curves",
            survival.get("curves") or [],
            ("ticker", "horizon", "survival", "hazard", "danger", "method"),
        ),
        "survival_hazards": replace_rows(
            "survival_hazards",
            survival.get("hazards") or [],
            ("ticker", "feature", "hazard_ratio", "coef"),
        ),
        "topics": replace_rows(
            "topics",
            topics,
            ("ticker", "quarter", "sector", "topic_id", "topic_label", "weight", "n_docs", "method"),
        ),
        "topic_shifts": replace_rows(
            "topic_shifts",
            shifts,
            ("scope", "name", "from_quarter", "to_quarter", "js", "flag"),
        ),
        "coreference_spans": replace_rows(
            "coreference_spans",
            coref,
            ("ticker", "transcript_date", "quarter", "pair_index", "pronoun", "referent", "resolved_question", "resolved_answer", "method"),
        ),
    }
    return {"ticker": ticker, "tables": counts, "tft_method": tft.get("method")}
