from __future__ import annotations

from typing import Any

from ecis.analytics.store import replace_rows
from ecis.reliability.calibrate import calibrate_revision_models, calibrate_signal_types
from ecis.reliability.contradictions import detect_contradictions
from ecis.reliability.explanations import explain_predictions
from ecis.reliability.ood import detect_ood
from ecis.reliability.shap_explain import explain_revisions


def refresh_reliability(ticker: str | None = None) -> dict[str, Any]:
    models, curves = calibrate_signal_types(ticker)
    revision = calibrate_revision_models(ticker)
    conflicts = detect_contradictions(ticker)
    shap_rows = explain_revisions(ticker)
    texts = explain_predictions(shap_rows)
    ood = detect_ood(ticker)

    shap_flat = []
    for row in shap_rows:
        for item in row.get("contributions") or []:
            shap_flat.append({
                "ticker": row.get("ticker"),
                "quarter": row.get("quarter"),
                "model_name": row.get("model_name"),
                "feature": item.get("feature"),
                "shap": item.get("shap"),
                "method": row.get("method"),
            })

    counts = {
        "calibration_models": replace_rows(
            "calibration_models",
            models,
            ("signal_type", "method", "ece_platt", "ece_isotonic", "selected", "n", "coef", "intercept"),
        ),
        "calibration_curves": replace_rows(
            "calibration_curves",
            curves,
            ("signal_type", "method", "decile", "expected", "observed", "n", "ece"),
        ),
        "revision_calibration": replace_rows(
            "revision_calibration",
            revision,
            ("model_name", "method", "temperature", "ece_raw", "ece", "n", "coef", "intercept"),
        ),
        "contradictions": replace_rows(
            "contradictions",
            conflicts,
            (
                "ticker", "transcript_date", "quarter", "rule", "severity",
                "resolution", "tone", "hedging", "confidence", "dodge", "tier",
            ),
        ),
        "shap_values": replace_rows(
            "shap_values",
            shap_flat,
            ("ticker", "quarter", "model_name", "feature", "shap", "method"),
        ),
        "explanations": replace_rows(
            "explanations",
            texts,
            ("ticker", "quarter", "model_name", "text", "top_features"),
        ),
        "ood_flags": replace_rows(
            "ood_flags",
            ood,
            (
                "ticker", "transcript_date", "quarter", "mahalanobis", "isolation",
                "score", "flag", "penalty", "tier",
            ),
        ),
    }
    return {"ticker": ticker, "tables": counts}
