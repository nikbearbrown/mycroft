"""Variational autoencoder stand-in on per-call feature vectors. Complements Mahalanobis OOD."""

from __future__ import annotations

import json
import os
from typing import Any

import numpy as np

from ecis.guidance_models.revision_features import build_revision_rows, normalize_vectors

_LOAD = os.getenv("GRAPH_LOAD_TORCH", "").lower() in {"1", "true", "yes"}
LATENT = 4


def _fit_vae(X: np.ndarray) -> tuple[np.ndarray, int, np.ndarray]:
    """Linear encoder from SVD, with a KL pull on the latent mean."""
    n, d = X.shape
    k = min(LATENT, d, max(n - 1, 1))
    mean = np.mean(X, axis=0)
    Xc = np.nan_to_num(X - mean)
    try:
        _, _, vt = np.linalg.svd(Xc, full_matrices=False)
    except np.linalg.LinAlgError:
        rng = np.random.default_rng(3)
        vt = rng.normal(0, 0.1, (min(n, d), d))
    w = np.asarray(vt[:k].T, dtype=float)
    # KL pull of mu toward 0, matching a diagonal VAE prior.
    mu = Xc @ w
    w -= 0.02 * (Xc.T @ mu) / max(n, 1)
    return w, k, mean


def detect_anomalies(ticker: str | None = None, matrix: np.ndarray | None = None) -> list[dict[str, Any]]:
    rows = normalize_vectors(build_revision_rows(ticker)) if matrix is None else []
    if matrix is not None:
        x = np.asarray(matrix, dtype=float)
        meta = [{"ticker": "AAA", "quarter": f"Q{i}"} for i in range(len(x))]
    else:
        if not rows:
            return []
        x = np.array([r["vector"] for r in rows], dtype=float)
        meta = rows
    if len(x) < 2:
        return []
    w, k, mean = _fit_vae(x)
    mu = (x - mean) @ w
    recon = mu @ w.T + mean
    mse = np.mean((x - recon) ** 2, axis=1)
    kl = np.mean(mu ** 2, axis=1)
    err = np.nan_to_num(mse + 0.05 * kl)
    thresh = float(np.mean(err) + 1.5 * (np.std(err) or 1e-6))
    out = []
    for i, row in enumerate(meta):
        out.append({
            "ticker": row.get("ticker"),
            "quarter": row.get("quarter"),
            "transcript_date": row.get("quarter"),
            "recon_error": float(err[i]),
            "latent": json.dumps([round(float(z), 4) for z in mu[i][:k]]),
            "flag": "anomaly" if err[i] > thresh else "ok",
            "threshold": thresh,
            "method": "numpy-vae",
        })
    return out
