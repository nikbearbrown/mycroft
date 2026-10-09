from __future__ import annotations

from typing import Any

from ecis.analytics.impact import reaction_windows, signal_price_correlation
from ecis.analytics.management import ceo_cfo_divergence, guidance_language, management_confidence
from ecis.analytics.sector_sentiment import (
    aggregate_sector_sentiment,
    cross_sector_zscores,
    sector_mood_index,
)
from ecis.analytics.store import replace_rows
from ecis.analytics.surprise import surprise_analytics


def refresh_analytics(ticker: str | None = None) -> dict[str, Any]:
    sector = aggregate_sector_sentiment(ticker)
    mood = sector_mood_index(ticker)
    zscores = cross_sector_zscores(ticker)
    conf = management_confidence(ticker)
    guidance = guidance_language(ticker)
    divergence = ceo_cfo_divergence(ticker)
    corr = signal_price_correlation(ticker)
    surprise = surprise_analytics(ticker)
    windows = reaction_windows(ticker)

    counts = {
        "sector_sentiment": replace_rows(
            "sector_sentiment",
            sector,
            (
                "sector", "quarter", "n_signals", "n_tickers",
                "tone_mean", "tone_median", "tone_stdev",
                "hedging_mean", "hedging_median", "hedging_stdev",
                "fls_mean", "fls_median", "fls_stdev", "equal_weighted",
            ),
        ),
        "sector_mood": replace_rows(
            "sector_mood",
            mood,
            ("sector", "quarter", "mood_score", "regime", "mood_shift", "n_signals", "n_tickers"),
        ),
        "cross_sector_z": replace_rows(
            "cross_sector_z",
            zscores,
            ("sector", "quarter", "mood_score", "z_score", "regime"),
        ),
        "management_confidence": replace_rows(
            "management_confidence",
            conf,
            (
                "ticker", "quarter", "n_signals", "confidence",
                "hedging_mean", "fls_mean", "definitive_ratio", "numerical_specificity",
            ),
        ),
        "guidance_language": replace_rows(
            "guidance_language",
            guidance,
            (
                "ticker", "quarter", "prior_quarter", "specificity",
                "specificity_change", "flag", "confidence",
            ),
        ),
        "ceo_cfo_divergence": replace_rows(
            "ceo_cfo_divergence",
            divergence,
            (
                "ticker", "transcript_date", "quarter",
                "ceo_confidence", "cfo_confidence", "confidence_gap",
                "ceo_tone", "cfo_tone", "tone_gap", "flag", "historical_mean_gap",
            ),
        ),
        "signal_price_corr": replace_rows(
            "signal_price_corr",
            corr,
            ("ticker", "quarter", "feature", "window", "n", "pearson", "spearman", "informativeness"),
        ),
        "surprise_analytics": replace_rows(
            "surprise_analytics",
            surprise,
            (
                "ticker", "quarter", "n",
                "nlp_vs_consensus", "consensus_vs_actual", "nlp_vs_actual",
                "nlp_hit_rate", "consensus_hit_rate",
            ),
        ),
        "reaction_windows": replace_rows(
            "reaction_windows",
            windows,
            (
                "direction", "quarter", "confidence_tier", "n",
                "car_same_day", "car_1d", "car_2d", "car_5d", "car_10d", "car_30d",
                "mean_reaction_magnitude", "pattern",
            ),
        ),
    }
    return {"ticker": ticker, "tables": counts}
