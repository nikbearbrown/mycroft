"""Compute and persist Phase 17 quality / linguistic / feature tables."""

from __future__ import annotations

from typing import Any

from ecis.analytics.store import replace_rows
from ecis.depth.call_quality import score_calls
from ecis.depth.chaining import chain_signals
from ecis.depth.decay_by_type import analyse_decay
from ecis.depth.discourse import analyse_discourse
from ecis.depth.embedding_drift import monitor_embedding_drift
from ecis.depth.false_positives import analyse_false_positives, cause_summary
from ecis.depth.feature_select import audit_features
from ecis.depth.interactions import discover_interactions
from ecis.depth.metaphor import track_metaphors
from ecis.depth.sarcasm import detect_sarcasm
from ecis.depth.speech_acts import call_distributions


def refresh_depth(ticker: str | None = None) -> dict[str, Any]:
    decay = analyse_decay(ticker)
    fps = analyse_false_positives(ticker)
    causes = cause_summary(fps)
    chains = chain_signals(ticker)
    quality = score_calls(ticker)
    acts = call_distributions(ticker)
    discourse = analyse_discourse(ticker)
    metaphors = track_metaphors(ticker)
    sarcasm = detect_sarcasm(ticker)
    features = audit_features(ticker)
    inter = discover_interactions(ticker)
    drift = monitor_embedding_drift(ticker)

    counts = {
        "signal_decay_types": replace_rows(
            "signal_decay_types",
            decay,
            ("signal_type", "horizon_days", "n", "pearson", "significant", "half_life_days", "weight_hint"),
        ),
        "false_positives": replace_rows(
            "false_positives",
            fps,
            (
                "signal_id", "ticker", "transcript_date", "direction", "confidence",
                "section_label", "root_cause", "sector", "excess_return",
                "confidence_modifier", "quote",
            ),
        ),
        "false_positive_causes": replace_rows(
            "false_positive_causes",
            causes,
            ("root_cause", "n", "mean_confidence"),
        ),
        "signal_chains": replace_rows(
            "signal_chains",
            chains,
            (
                "ticker", "quarter", "hedging_streak", "hedging_direction",
                "confidence_streak", "confidence_trajectory", "dodge_momentum",
                "specificity_drift", "chain_length", "flag", "weight",
            ),
        ),
        "call_quality": replace_rows(
            "call_quality",
            quality,
            (
                "ticker", "transcript_date", "quarter", "completeness", "qa_score",
                "speaker_coverage", "coherence", "formatting", "quality", "flag", "weight",
            ),
        ),
        "speech_acts": replace_rows(
            "speech_acts",
            acts,
            (
                "ticker", "transcript_date", "quarter",
                "p_promise", "p_commitment", "p_hedged_intention",
                "p_prediction", "p_deflection", "p_assertion", "mix_shift",
            ),
        ),
        "discourse_structure": replace_rows(
            "discourse_structure",
            discourse,
            (
                "ticker", "transcript_date", "quarter", "pattern", "n_chunks",
                "start_polarity", "end_polarity", "flag",
            ),
        ),
        "metaphor_density": replace_rows(
            "metaphor_density",
            metaphors,
            (
                "ticker", "transcript_date", "quarter", "speaker_role",
                "density", "hits", "flag", "historical_mean",
            ),
        ),
        "sarcasm_flags": replace_rows(
            "sarcasm_flags",
            sarcasm,
            (
                "ticker", "transcript_date", "quarter", "sarcastic", "method",
                "score", "question", "answer", "call_sarcasm_rate", "contentious",
            ),
        ),
        "feature_audit": replace_rows(
            "feature_audit",
            features,
            (
                "feature", "marginal", "permutation_drop", "lasso_weight",
                "rfe_rank", "redundant_with", "recommendation",
            ),
        ),
        "feature_interactions": replace_rows(
            "feature_interactions",
            inter,
            ("feature_a", "feature_b", "interaction", "pearson", "gain", "p_value"),
        ),
        "embedding_drift": replace_rows(
            "embedding_drift",
            drift,
            (
                "quarter", "n", "centroid_drift", "psi",
                "bullish_var", "bearish_var", "hedging_var", "flag",
            ),
        ),
    }
    return {"ticker": ticker, "tables": counts}
