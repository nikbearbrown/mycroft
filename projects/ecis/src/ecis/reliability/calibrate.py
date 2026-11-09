"""Per-signal-type Platt / isotonic calibration and revision-model temperature scaling."""

from __future__ import annotations

import math
from typing import Any

from ecis.depth.decay_by_type import SIGNAL_TYPES, _joined
from ecis.scoring.metrics import expected_calibration_error

DECILES = 10


def _clip01(value: float | None) -> float | None:
    if value is None:
        return None
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return None


def _sigmoid(z: float) -> float:
    if z >= 20:
        return 1.0
    if z <= -20:
        return 0.0
    return 1.0 / (1.0 + pow(2.718281828459045, -z))


def fit_platt(scores: list[float], outcomes: list[int], steps: int = 200) -> dict[str, float]:
    """1-D logistic: P(correct) = sigmoid(a * score + b)."""
    a, b = 1.0, 0.0
    n = max(len(scores), 1)
    for _ in range(steps):
        ga = gb = 0.0
        for x, y in zip(scores, outcomes):
            p = _sigmoid(a * x + b)
            err = p - y
            ga += err * x
            gb += err
        a -= 0.4 * ga / n
        b -= 0.4 * gb / n
    return {"coef": a, "intercept": b}


def apply_platt(score: float, coef: float, intercept: float) -> float:
    return _sigmoid(coef * score + intercept)


def fit_isotonic(scores: list[float], outcomes: list[int]) -> list[tuple[float, float]]:
    """Pool-adjacent-violators; returns (score, calibrated) knots sorted by score."""
    pairs = sorted(zip(scores, outcomes), key=lambda p: p[0])
    if not pairs:
        return []
    blocks: list[list[float]] = [[float(y)] for _, y in pairs]
    xs = [float(x) for x, _ in pairs]
    changed = True
    while changed:
        changed = False
        i = 0
        merged: list[list[float]] = []
        mx: list[float] = []
        while i < len(blocks):
            if i + 1 < len(blocks):
                m0 = sum(blocks[i]) / len(blocks[i])
                m1 = sum(blocks[i + 1]) / len(blocks[i + 1])
                if m0 > m1 + 1e-12:
                    merged.append(blocks[i] + blocks[i + 1])
                    mx.append(xs[i])
                    i += 2
                    changed = True
                    continue
            merged.append(blocks[i])
            mx.append(xs[i])
            i += 1
        blocks, xs = merged, mx
    knots = []
    for x, block in zip(xs, blocks):
        knots.append((x, sum(block) / len(block)))
    return knots


def apply_isotonic(score: float, knots: list[tuple[float, float]]) -> float:
    if not knots:
        return score
    if score <= knots[0][0]:
        return knots[0][1]
    for i in range(1, len(knots)):
        if score <= knots[i][0]:
            x0, y0 = knots[i - 1]
            x1, y1 = knots[i]
            if x1 == x0:
                return y1
            t = (score - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)
    return knots[-1][1]


def fit_temperature(logits: list[float], outcomes: list[int]) -> float:
    """Binary temperature scaling: p = sigmoid(logit / T)."""
    best_t, best_nll = 1.0, 1e9
    for step in range(1, 41):
        t = step / 10.0
        nll = 0.0
        for z, y in zip(logits, outcomes):
            p = min(1 - 1e-6, max(1e-6, _sigmoid(z / t)))
            nll += -(y * math.log(p) + (1 - y) * math.log(1 - p))
        if nll < best_nll:
            best_t, best_nll = t, nll
    return best_t


def _logit(p: float) -> float:
    p = min(1 - 1e-6, max(1e-6, p))
    return math.log(p / (1 - p))


def _ece(scores: list[float], outcomes: list[int]) -> float:
    if len(scores) < 2:
        return 0.0
    value, _ = expected_calibration_error(scores, outcomes, n_bins=min(DECILES, max(len(scores), 1)))
    return float(value)


def _bins(scores: list[float], outcomes: list[int]) -> list[dict[str, Any]]:
    if not scores:
        return []
    _, bins = expected_calibration_error(scores, outcomes, n_bins=DECILES)
    return [
        {
            "decile": i + 1,
            "expected": b["avg_confidence"],
            "observed": b["avg_accuracy"],
            "n": b["count"],
        }
        for i, b in enumerate(bins)
    ]


def _pairs_for_type(name: str, ticker: str | None = None) -> tuple[list[float], list[int]]:
    rows = _joined(ticker)
    xs, ys = [], []
    for row in rows:
        score = _clip01(row.get(name) if name != "confidence" else row.get("confidence"))
        if name in {"hedging_index", "dodge_score"} and score is not None:
            score = 1.0 - score
        outcome = row.get("correct") if "correct" in row else None
        if outcome is None and row.get("excess_return") is not None:
            outcome = 1 if float(row["excess_return"]) > 0 else 0
        if score is None or outcome is None:
            continue
        xs.append(score)
        ys.append(int(outcome))
    return xs, ys


def calibrate_signal_types(ticker: str | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Fit Platt and isotonic per signal type; keep the lower-ECE method."""
    models: list[dict[str, Any]] = []
    curves: list[dict[str, Any]] = []
    for name in SIGNAL_TYPES:
        xs, ys = _pairs_for_type(name, ticker)
        n = len(xs)
        if n < 3:
            models.append({
                "signal_type": name, "method": "none", "ece_platt": None, "ece_isotonic": None,
                "selected": "none", "n": n, "coef": None, "intercept": None,
            })
            continue
        hold = max(1, n // 4)
        train_x, train_y = xs[:-hold] or xs, ys[:-hold] or ys
        val_x, val_y = xs[-hold:] if hold < n else xs, ys[-hold:] if hold < n else ys
        platt = fit_platt(train_x, train_y)
        knots = fit_isotonic(train_x, train_y)
        p_val = [apply_platt(x, platt["coef"], platt["intercept"]) for x in val_x]
        i_val = [apply_isotonic(x, knots) for x in val_x]
        ece_p = _ece(p_val, val_y)
        ece_i = _ece(i_val, val_y)
        selected = "platt" if ece_p <= ece_i else "isotonic"
        calibrated = p_val if selected == "platt" else i_val
        models.append({
            "signal_type": name,
            "method": selected,
            "ece_platt": ece_p,
            "ece_isotonic": ece_i,
            "selected": selected,
            "n": n,
            "coef": platt["coef"],
            "intercept": platt["intercept"],
        })
        for bin_row in _bins(calibrated, val_y):
            curves.append({"signal_type": name, "method": selected, **bin_row, "ece": ece_p if selected == "platt" else ece_i})
    return models, curves


def calibrate_revision_models(ticker: str | None = None) -> list[dict[str, Any]]:
    from ecis.db.init_db import get_connection

    try:
        conn = get_connection("agents")
        rows = [dict(r) for r in conn.execute(
            "SELECT model_name, probability, ticker, quarter FROM revision_predictions"
        ).fetchall()]
        feats = [dict(r) for r in conn.execute(
            "SELECT ticker, quarter, target FROM revision_features WHERE target IS NOT NULL"
        ).fetchall()]
        conn.close()
    except Exception:
        return []
    truth = {(r["ticker"], r["quarter"]): int(r["target"]) for r in feats}
    by_model: dict[str, list[tuple[float, int]]] = {}
    for row in rows:
        key = (row.get("ticker"), row.get("quarter"))
        if key not in truth or row.get("probability") is None:
            continue
        by_model.setdefault(row["model_name"] or "unknown", []).append(
            (float(row["probability"]), truth[key])
        )
    out = []
    for name, pairs in sorted(by_model.items()):
        xs = [p for p, _ in pairs]
        ys = [y for _, y in pairs]
        logits = [_logit(x) for x in xs]
        temp = 1.0 if name != "mlp" else fit_temperature(logits, ys)
        scaled = [_sigmoid(z / temp) for z in logits]
        platt = fit_platt(xs, ys)
        p_cal = [apply_platt(x, platt["coef"], platt["intercept"]) for x in xs]
        ece_raw = _ece(xs, ys)
        ece_t = _ece(scaled, ys)
        ece_p = _ece(p_cal, ys)
        method = "temperature" if name == "mlp" and ece_t <= ece_p else "platt"
        out.append({
            "model_name": name,
            "method": method,
            "temperature": temp if method == "temperature" else None,
            "ece_raw": ece_raw,
            "ece": ece_t if method == "temperature" else ece_p,
            "n": len(pairs),
            "coef": platt["coef"],
            "intercept": platt["intercept"],
        })
    return out
