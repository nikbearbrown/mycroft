"""Scoring metrics: Brier score, skill score, ECE, Murphy decomposition."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def brier_score(confidences: list[float], outcomes: list[int]) -> float:
    """Compute Brier score: mean((confidence - outcome)^2).

    Lower is better. Range [0, 1].
    """
    c = np.array(confidences)
    o = np.array(outcomes)
    return float(np.mean((c - o) ** 2))


def skill_score(model_brier: float, reference_brier: float) -> float:
    """Compute Brier skill score: 1 - (model / reference).

    Positive means model beats the reference (climatological base rate).
    """
    if reference_brier == 0:
        return 0.0
    return 1.0 - (model_brier / reference_brier)


def expected_calibration_error(
    confidences: list[float],
    outcomes: list[int],
    n_bins: int = 10,
) -> tuple[float, list[dict[str, Any]]]:
    """Compute Expected Calibration Error.

    Returns (ece_value, bin_details).
    Each bin_detail has: bin_lower, bin_upper, avg_confidence, avg_accuracy, count, weight.
    """
    c = np.array(confidences)
    o = np.array(outcomes)
    n = len(c)

    if n == 0:
        return 0.0, []

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bins = []
    ece = 0.0

    for i in range(n_bins):
        lower, upper = bin_boundaries[i], bin_boundaries[i + 1]
        mask = (c > lower) & (c <= upper) if i > 0 else (c >= lower) & (c <= upper)
        count = mask.sum()

        if count == 0:
            bins.append({
                "bin_lower": float(lower),
                "bin_upper": float(upper),
                "avg_confidence": 0.0,
                "avg_accuracy": 0.0,
                "count": 0,
                "weight": 0.0,
            })
            continue

        avg_conf = float(c[mask].mean())
        avg_acc = float(o[mask].mean())
        weight = count / n

        ece += weight * abs(avg_conf - avg_acc)
        bins.append({
            "bin_lower": float(lower),
            "bin_upper": float(upper),
            "avg_confidence": round(avg_conf, 4),
            "avg_accuracy": round(avg_acc, 4),
            "count": int(count),
            "weight": round(weight, 4),
        })

    return round(ece, 6), bins


def murphy_decomposition(
    confidences: list[float],
    outcomes: list[int],
    n_bins: int = 10,
) -> dict[str, float]:
    """Decompose Brier score into reliability, resolution, and uncertainty.

    Brier = reliability - resolution + uncertainty

    - Reliability (lower is better): measures calibration
    - Resolution (higher is better): measures discrimination
    - Uncertainty: base-rate entropy, independent of the model
    """
    c = np.array(confidences)
    o = np.array(outcomes)
    n = len(c)

    if n == 0:
        return {"reliability": 0.0, "resolution": 0.0, "uncertainty": 0.0}

    base_rate = o.mean()
    uncertainty = float(base_rate * (1 - base_rate))

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    reliability = 0.0
    resolution = 0.0

    for i in range(n_bins):
        lower, upper = bin_boundaries[i], bin_boundaries[i + 1]
        mask = (c > lower) & (c <= upper) if i > 0 else (c >= lower) & (c <= upper)
        count = mask.sum()

        if count == 0:
            continue

        avg_conf = c[mask].mean()
        avg_acc = o[mask].mean()
        weight = count / n

        reliability += weight * (avg_conf - avg_acc) ** 2
        resolution += weight * (avg_acc - base_rate) ** 2

    return {
        "reliability": round(float(reliability), 6),
        "resolution": round(float(resolution), 6),
        "uncertainty": round(float(uncertainty), 6),
    }
