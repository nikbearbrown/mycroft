"""Six-model guidance-revision ensemble with sklearn fallbacks and comparison."""

from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np

from ecis.guidance_models.revision_features import FEATURE_NAMES, build_revision_rows, normalize_vectors
from ecis.scoring.bootstrap import bootstrap_ci
from ecis.scoring.significance import paired_permutation_diff

MODEL_VERSION = "rev-v1"
NAMES = ("logistic", "xgboost", "random_forest", "lightgbm", "mlp", "catboost")


def _temporal_folds(rows: list[dict[str, Any]]) -> list[tuple[list[dict[str, Any]], list[dict[str, Any]]]]:
    labelled = [r for r in rows if r.get("target") is not None]
    quarters = sorted({r["quarter"] for r in labelled})
    if len(quarters) < 2:
        return []
    hold = quarters[-1]
    train = [r for r in labelled if r["quarter"] != hold]
    test = [r for r in labelled if r["quarter"] == hold]
    if not train or not test:
        return []
    return [(train, test)]


class _ProbaClf:
    def __init__(self, intercept: float, weights: np.ndarray | None = None, importance: np.ndarray | None = None):
        self.intercept = intercept
        self.weights = weights
        self.classes_ = np.array([0, 1])
        self.coef_ = None if weights is None else np.asarray([weights])
        self.feature_importances_ = importance

    def predict_proba(self, X):
        X = np.asarray(X, dtype=float)
        if self.weights is None:
            z = np.full(len(X), self.intercept)
        else:
            z = self.intercept + X @ self.weights
        p = 1.0 / (1.0 + np.exp(-np.clip(z, -20, 20)))
        return np.column_stack([1.0 - p, p])


def _numpy_logistic(X, y, l2: float = 0.1, steps: int = 80):
    X = np.asarray(X, dtype=float)
    yv = np.asarray(y, dtype=float)
    w = np.zeros(X.shape[1])
    b = 0.0
    lr = 0.15
    for _ in range(steps):
        z = b + X @ w
        p = 1.0 / (1.0 + np.exp(-np.clip(z, -20, 20)))
        err = p - yv
        w -= lr * (X.T @ err / max(len(X), 1) + l2 * w)
        b -= lr * float(err.mean())
    return _ProbaClf(b, w, np.abs(w))


def _fitters():
    try:
        from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.neural_network import MLPClassifier
    except ImportError:
        return {
            "logistic": lambda X, y: _numpy_logistic(X, y, 0.05),
            "xgboost": lambda X, y: _numpy_logistic(X, y, 0.15),
            "random_forest": lambda X, y: _numpy_logistic(X, y, 0.25),
            "lightgbm": lambda X, y: _numpy_logistic(X, y, 0.35),
            "mlp": lambda X, y: _numpy_logistic(X, y, 0.10),
            "catboost": lambda X, y: _numpy_logistic(X, y, 0.20),
        }

    def logistic(X, y):
        clf = LogisticRegression(max_iter=400, class_weight="balanced")
        clf.fit(X, y)
        return clf

    def xgb(X, y):
        try:
            from xgboost import XGBClassifier

            clf = XGBClassifier(n_estimators=80, max_depth=3, learning_rate=0.1, eval_metric="logloss", verbosity=0)
            clf.fit(X, y)
            return clf
        except Exception:
            from sklearn.ensemble import GradientBoostingClassifier

            clf = GradientBoostingClassifier(n_estimators=80, max_depth=2)
            clf.fit(X, y)
            return clf

    def rf(X, y):
        clf = RandomForestClassifier(n_estimators=80, max_depth=4, class_weight="balanced", random_state=0)
        clf.fit(X, y)
        return clf

    def lgbm(X, y):
        try:
            from lightgbm import LGBMClassifier

            clf = LGBMClassifier(n_estimators=80, max_depth=3, verbose=-1)
            clf.fit(X, y)
            return clf
        except Exception:
            clf = ExtraTreesClassifier(n_estimators=80, max_depth=4, random_state=0, class_weight="balanced")
            clf.fit(X, y)
            return clf

    def mlp(X, y):
        clf = MLPClassifier(
            hidden_layer_sizes=(64, 32),
            activation="relu",
            alpha=0.01,
            max_iter=400,
            early_stopping=len(X) >= 12,
            random_state=0,
        )
        clf.fit(X, y)
        return clf

    def cat(X, y):
        try:
            from catboost import CatBoostClassifier

            clf = CatBoostClassifier(iterations=80, depth=3, verbose=False)
            clf.fit(X, y)
            return clf
        except Exception:
            clf = HistGradientBoostingClassifier(max_depth=3, max_iter=80)
            clf.fit(X, y)
            return clf

    return {
        "logistic": logistic,
        "xgboost": xgb,
        "random_forest": rf,
        "lightgbm": lgbm,
        "mlp": mlp,
        "catboost": cat,
    }


def _positive_proba(clf, X: np.ndarray) -> np.ndarray:
    raw = clf.predict_proba(X)
    classes = list(getattr(clf, "classes_", [0, 1]))
    if raw.ndim == 1:
        return raw
    if 1 in classes:
        idx = classes.index(1)
        return raw[:, idx]
    return raw[:, -1]


def _metrics(y: list[int], p: np.ndarray) -> dict[str, float]:
    y_arr = np.array(y, dtype=float)
    pred = (p >= 0.5).astype(int)
    tp = int(((pred == 1) & (y_arr == 1)).sum())
    fp = int(((pred == 1) & (y_arr == 0)).sum())
    fn = int(((pred == 0) & (y_arr == 1)).sum())
    tn = int(((pred == 0) & (y_arr == 0)).sum())
    acc = (tp + tn) / max(len(y), 1)
    prec = tp / max(tp + fp, 1)
    rec = tp / max(tp + fn, 1)
    f1 = 0.0 if prec + rec == 0 else 2 * prec * rec / (prec + rec)
    brier = float(np.mean((p - y_arr) ** 2))
    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "brier": brier,
        "n": len(y),
    }


def _importance(clf) -> list[tuple[str, float]]:
    if hasattr(clf, "coef_"):
        coef = np.abs(np.ravel(clf.coef_))
        return sorted(zip(FEATURE_NAMES, coef.tolist()), key=lambda p: p[1], reverse=True)
    if hasattr(clf, "feature_importances_"):
        return sorted(zip(FEATURE_NAMES, clf.feature_importances_.tolist()), key=lambda p: p[1], reverse=True)
    return []


def train_revision_models(ticker: str | None = None) -> dict[str, Any]:
    rows = normalize_vectors(build_revision_rows(ticker))
    labelled = [r for r in rows if r.get("target") is not None]
    forecast = [r for r in rows if r.get("target") is None]
    folds = _temporal_folds(rows)
    if len(labelled) < 3 or not folds:
        return {
            "trained": False,
            "reason": "need labelled quarters on both sides of a temporal holdout",
            "n_labelled": len(labelled),
            "predictions": [],
            "comparison": [],
        }

    train, test = folds[0]
    X_train = np.array([r["vector"] for r in train], dtype=float)
    y_train = [int(r["target"]) for r in train]
    X_test = np.array([r["vector"] for r in test], dtype=float)
    y_test = [int(r["target"]) for r in test]
    naive = np.zeros(len(y_test), dtype=float)

    fitters = _fitters()
    fitted: dict[str, Any] = {}
    test_probs: dict[str, np.ndarray] = {"naive": naive}
    comparison: list[dict[str, Any]] = []
    for name in NAMES:
        clf = fitters[name](X_train, y_train)
        fitted[name] = clf
        probs = _positive_proba(clf, X_test)
        test_probs[name] = probs
        metrics = _metrics(y_test, probs)
        sq = list((probs - np.array(y_test, dtype=float)) ** 2)
        brier_ci = bootstrap_ci(sq) if len(y_test) >= 5 else None
        comparison.append({
            "model_name": name,
            **metrics,
            "naive_brier": _metrics(y_test, naive)["brier"],
            "brier_lo": None if not brier_ci else brier_ci["lo"],
            "brier_hi": None if not brier_ci else brier_ci["hi"],
            "feature_importance": _importance(clf)[:8],
        })

    y_arr = np.array(y_test, dtype=float)
    pairs = []
    names = list(NAMES)
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            se_a = list((test_probs[a] - y_arr) ** 2)
            se_b = list((test_probs[b] - y_arr) ** 2)
            perm = paired_permutation_diff(se_a, se_b, n_perm=400)
            pairs.append({
                "model_a": a,
                "model_b": b,
                "diff": perm["observed_diff"],
                "p_value": perm["p_value"],
            })

    ranked = sorted(comparison, key=lambda r: r["brier"])
    primary = ranked[0]["model_name"]
    fallback = ranked[1]["model_name"] if len(ranked) > 1 else primary

    to_score = test + forecast
    if not to_score:
        to_score = labelled[-1:]
    X_all = np.array([r["vector"] for r in to_score], dtype=float)
    predictions: list[dict[str, Any]] = []
    for name, clf in fitted.items():
        probs = _positive_proba(clf, X_all)
        for row, p in zip(to_score, probs):
            drivers = _importance(clf)[:5]
            predictions.append({
                "ticker": row["ticker"],
                "quarter": row["quarter"],
                "model_name": name,
                "probability": float(p),
                "predicted": int(p >= 0.5),
                "actual": row.get("target"),
                "role": "primary" if name == primary else "fallback" if name == fallback else "candidate",
                "drivers": drivers,
                "features": row["features"],
                "feature_version": MODEL_VERSION,
            })

    return {
        "trained": True,
        "n_train": len(train),
        "n_test": len(test),
        "class_counts": dict(Counter(y_train)),
        "primary": primary,
        "fallback": fallback,
        "comparison": comparison,
        "pairwise": pairs,
        "naive_brier": _metrics(y_test, naive)["brier"],
        "predictions": predictions,
        "importances": {row["model_name"]: row["feature_importance"] for row in comparison},
    }
