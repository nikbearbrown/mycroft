"""Recalibration: Platt scaling and isotonic regression for confidence calibration."""

from __future__ import annotations

import json
import logging
from typing import Any

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression

from ecis.db.init_db import get_connection

logger = logging.getLogger(__name__)


def _fetch_calibration_data(
    source_method: str | None = None,
) -> tuple[list[float], list[int]]:
    """Fetch (confidence_raw, correct) pairs for calibration fitting."""
    conn_s = get_connection("signals")
    conn_o = get_connection("outcomes")

    query = "SELECT signal_id, confidence_raw FROM signals"
    if source_method:
        query += " WHERE source_method = ?"
        rows = conn_s.execute(query, (source_method,)).fetchall()
    else:
        rows = conn_s.execute(query).fetchall()
    conn_s.close()

    confidences = []
    outcomes = []
    for row in rows:
        out = conn_o.execute(
            "SELECT correct FROM outcomes WHERE signal_id = ? AND correct IS NOT NULL",
            (row["signal_id"],),
        ).fetchone()
        if out:
            confidences.append(row["confidence_raw"])
            outcomes.append(out["correct"])

    conn_o.close()
    return confidences, outcomes


def fit_platt(source_method: str | None = None) -> dict[str, Any]:
    """Fit Platt scaling (logistic regression) on confidence vs correctness.

    Returns model parameters for later application.
    """
    confidences, outcomes = _fetch_calibration_data(source_method)

    if len(confidences) < 10:
        logger.warning("Insufficient data for Platt scaling (%d samples)", len(confidences))
        return {"fitted": False, "reason": "insufficient_data", "n_samples": len(confidences)}

    X = np.array(confidences).reshape(-1, 1)
    y = np.array(outcomes)

    model = LogisticRegression(solver="lbfgs", max_iter=1000)
    model.fit(X, y)

    params = {
        "fitted": True,
        "method": "platt",
        "source_method": source_method or "all",
        "n_samples": len(confidences),
        "coef": float(model.coef_[0][0]),
        "intercept": float(model.intercept_[0]),
    }

    _store_calibration_params(params)
    logger.info("Platt scaling fitted: coef=%.4f, intercept=%.4f", params["coef"], params["intercept"])
    return params


def fit_isotonic(source_method: str | None = None) -> dict[str, Any]:
    """Fit isotonic regression on confidence vs correctness.

    Returns model parameters.
    """
    confidences, outcomes = _fetch_calibration_data(source_method)

    if len(confidences) < 10:
        logger.warning("Insufficient data for isotonic regression (%d samples)", len(confidences))
        return {"fitted": False, "reason": "insufficient_data", "n_samples": len(confidences)}

    X = np.array(confidences)
    y = np.array(outcomes)

    model = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
    model.fit(X, y)

    params = {
        "fitted": True,
        "method": "isotonic",
        "source_method": source_method or "all",
        "n_samples": len(confidences),
        "x_thresholds": model.X_thresholds_.tolist(),
        "y_thresholds": model.y_thresholds_.tolist(),
    }

    _store_calibration_params(params)
    logger.info("Isotonic regression fitted with %d thresholds", len(params["x_thresholds"]))
    return params


def apply_platt(confidence_raw: float, coef: float, intercept: float) -> float:
    """Apply Platt scaling to a single confidence value."""
    logit = coef * confidence_raw + intercept
    return float(1.0 / (1.0 + np.exp(-logit)))


def apply_isotonic(
    confidence_raw: float,
    x_thresholds: list[float],
    y_thresholds: list[float],
) -> float:
    """Apply isotonic regression to a single confidence value."""
    model = IsotonicRegression(out_of_bounds="clip")
    model.X_thresholds_ = np.array(x_thresholds)
    model.y_thresholds_ = np.array(y_thresholds)
    model.X_min_ = x_thresholds[0]
    model.X_max_ = x_thresholds[-1]
    model.increasing_ = True
    return float(model.predict([confidence_raw])[0])


def recalibrate_signals(method: str = "platt", source_method: str | None = None) -> int:
    """Fit calibration model and update confidence_calibrated for all matching signals.

    Returns number of signals updated.
    """
    if method == "platt":
        params = fit_platt(source_method)
    elif method == "isotonic":
        params = fit_isotonic(source_method)
    else:
        raise ValueError(f"Unknown method: {method}")

    if not params.get("fitted"):
        return 0

    conn = get_connection("signals")
    query = "SELECT signal_id, confidence_raw FROM signals"
    if source_method:
        query += " WHERE source_method = ?"
        rows = conn.execute(query, (source_method,)).fetchall()
    else:
        rows = conn.execute(query).fetchall()

    updated = 0
    for row in rows:
        raw = row["confidence_raw"]
        if method == "platt":
            calibrated = apply_platt(raw, params["coef"], params["intercept"])
        else:
            calibrated = apply_isotonic(raw, params["x_thresholds"], params["y_thresholds"])

        conn.execute(
            "UPDATE signals SET confidence_calibrated = ? WHERE signal_id = ?",
            (round(calibrated, 6), row["signal_id"]),
        )
        updated += 1

    conn.commit()
    conn.close()
    logger.info("Recalibrated %d signals using %s", updated, method)
    return updated


def _store_calibration_params(params: dict[str, Any]) -> None:
    """Store calibration parameters in agent audit log."""
    conn = get_connection("agents")
    conn.execute(
        """INSERT INTO agent_actions (agent_name, observation, action_taken, result)
           VALUES (?, ?, ?, ?)""",
        (
            "recalibrator",
            f"Fitted {params['method']} on {params['n_samples']} samples",
            "calibration_fit",
            json.dumps(params, default=str),
        ),
    )
    conn.commit()
    conn.close()
