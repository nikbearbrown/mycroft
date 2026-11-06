"""Persist Phase 19 uncertainty, contagion, lag, and leave the agent session tables in place."""

from __future__ import annotations

from typing import Any

from ecis.analytics.store import replace_rows
from ecis.intelligence.conformal import conformal_intervals
from ecis.intelligence.contagion import contagion_links
from ecis.intelligence.disagreement import ensemble_disagreement
from ecis.intelligence.dropout import mc_dropout
from ecis.intelligence.lag import temporal_lags
from ecis.intelligence.selective import decide_abstention
from ecis.intelligence.supply_chain import supply_propagation


def refresh_intelligence(ticker: str | None = None) -> dict[str, Any]:
    intervals = conformal_intervals(ticker)
    dropout = mc_dropout(ticker)
    disagreement = ensemble_disagreement(ticker)
    selective = decide_abstention(intervals, dropout, disagreement)
    contagion = contagion_links(ticker)
    supply = supply_propagation(ticker)
    lags = temporal_lags(ticker)

    counts = {
        "prediction_intervals": replace_rows(
            "prediction_intervals",
            intervals,
            ("ticker", "quarter", "model_name", "probability", "lower", "upper", "width", "coverage_target", "nonconformity"),
        ),
        "mc_dropout": replace_rows(
            "mc_dropout",
            dropout,
            ("ticker", "quarter", "model_name", "mean", "variance", "stdev", "entropy", "mutual_info", "n_draws"),
        ),
        "ensemble_disagreement": replace_rows(
            "ensemble_disagreement",
            disagreement,
            ("ticker", "quarter", "n_models", "stdev", "max_pairwise", "n_majority", "majority", "disagreement"),
        ),
        "selective_predictions": replace_rows(
            "selective_predictions",
            selective,
            ("ticker", "quarter", "abstain", "reasons", "width", "variance", "disagreement", "uncertainty"),
        ),
        "contagion_links": replace_rows(
            "contagion_links",
            contagion,
            ("leader", "follower", "sector", "signal_type", "granger_r", "lag_quarters", "n", "strength"),
        ),
        "supply_propagation": replace_rows(
            "supply_propagation",
            supply,
            ("supplier", "customer", "signal_type", "same_quarter_r", "lag1_r", "delay_quarters", "early_warning", "n"),
        ),
        "temporal_lags": replace_rows(
            "temporal_lags",
            lags,
            ("signal_type", "lag_days", "pearson", "n", "best", "optimal_lag_days", "weight_hint"),
        ),
    }
    return {"ticker": ticker, "tables": counts}
