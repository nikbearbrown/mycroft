from __future__ import annotations

from typing import Any

from ecis.guidance_models.dodge import aggregate_dodge, score_pairs
from ecis.guidance_models.market_share import score_calls, track_shifts
from ecis.guidance_models.qa_parser import parse_qa_corpus
from ecis.guidance_models.revision_features import FEATURE_NAMES, FEATURE_VERSION, build_revision_rows
from ecis.guidance_models.revision_models import train_revision_models
from ecis.guidance_models.sbert import finetune_status
from ecis.analytics.store import replace_rows


def refresh_guidance_models(ticker: str | None = None) -> dict[str, Any]:
    pairs = score_pairs(parse_qa_corpus(ticker))
    dodge = aggregate_dodge(pairs, ticker=ticker)
    share = score_calls(ticker)
    shifts = track_shifts(ticker)
    features = build_revision_rows(ticker)
    models = train_revision_models(ticker)

    counts = {
        "qa_pairs": replace_rows(
            "qa_pairs",
            pairs,
            (
                "ticker", "transcript_date", "pair_index", "question", "answer",
                "question_speaker", "answer_speaker", "answer_role", "follow_up",
                "question_type", "type_weight", "relevance", "relevance_method",
                "evasion", "dodge", "char_start", "char_end",
            ),
        ),
        "dodge_scores": replace_rows(
            "dodge_scores",
            dodge,
            (
                "ticker", "transcript_date", "quarter", "scope", "speaker_role",
                "n_pairs", "dodge", "forward_looking", "backward_looking",
                "clarification", "confrontational", "flag", "historical_mean",
            ),
        ),
        "market_share_language": replace_rows(
            "market_share_language",
            share,
            (
                "ticker", "transcript_date", "quarter", "score", "label",
                "lexicon_score", "zeroshot_score", "stance_score",
                "agreement", "phrases",
            ),
        ),
        "market_share_shifts": replace_rows(
            "market_share_shifts",
            shifts,
            (
                "ticker", "quarter", "transcript_date", "score", "label",
                "prior_label", "score_change", "flag", "phrases", "agreement",
            ),
        ),
        "revision_features": replace_rows(
            "revision_features",
            [
                {
                    "ticker": r["ticker"],
                    "quarter": r["quarter"],
                    "feature_version": FEATURE_VERSION,
                    "target": r.get("target"),
                    "current_direction": r.get("current_direction"),
                    "next_direction": r.get("next_direction"),
                    **{name: r["features"].get(name) for name in FEATURE_NAMES},
                }
                for r in features
            ],
            (
                "ticker", "quarter", "feature_version", "target",
                "current_direction", "next_direction", *FEATURE_NAMES,
            ),
        ),
        "revision_predictions": replace_rows(
            "revision_predictions",
            models.get("predictions") or [],
            (
                "ticker", "quarter", "model_name", "probability", "predicted",
                "actual", "role", "drivers", "features", "feature_version",
            ),
        ),
        "revision_model_comparison": replace_rows(
            "revision_model_comparison",
            models.get("comparison") or [],
            (
                "model_name", "accuracy", "precision", "recall", "f1", "brier",
                "n", "naive_brier", "brier_lo", "brier_hi", "feature_importance",
            ),
        ),
    }
    return {
        "ticker": ticker,
        "tables": counts,
        "primary": models.get("primary"),
        "fallback": models.get("fallback"),
        "trained": models.get("trained"),
        "sbert": finetune_status(),
    }
