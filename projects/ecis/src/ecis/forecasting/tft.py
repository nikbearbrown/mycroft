"""Multi-horizon Temporal Fusion Transformer stand-in."""

from __future__ import annotations

import json
import math
import os
from typing import Any

import numpy as np

from ecis.analytics.store import fetch_table
from ecis.timeseries.sequences import build_sequences

HORIZONS = (1, 2, 5, 10)
_LOAD = os.getenv("FORECASTING_LOAD_TFT", "").lower() in {"1", "true", "yes"}


def _softmax(z: np.ndarray) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    z = z - np.max(z)
    e = np.exp(np.clip(z, -20, 20))
    s = e.sum() or 1.0
    return e / s


def _sig(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-20.0, min(20.0, z))))


def _variable_weights(seq: np.ndarray) -> np.ndarray:
    last = seq[-1]
    mag = np.abs(last) + 1e-6
    return _softmax(mag)


def _attention(seq: np.ndarray) -> np.ndarray:
    q = seq[-1]
    scores = seq @ q
    return _softmax(scores)


def _encode(seq: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sel = _variable_weights(seq)
    att = _attention(seq)
    selected = seq * sel
    context = att @ selected
    last = selected[-1]
    return np.concatenate([last, context]), att, sel


def _fan(p: float, horizon: int, residual: float) -> tuple[float, float, float]:
    width = min(0.45, 0.08 * math.sqrt(horizon) + 0.5 * residual)
    lo = max(0.0, p - width)
    hi = min(1.0, p + width)
    return lo, p, hi


def _numpy_forecast(seqs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    labelled = [s for s in seqs if s.get("target") is not None]
    residual = 0.12
    if labelled:
        residual = float(np.std([float(s["target"]) for s in labelled])) or 0.12
    # last-step logistic on encoded history
    w = None
    b = 0.0
    if labelled:
        dim = len(_encode(np.asarray(labelled[0]["X"], dtype=float))[0])
        w = np.zeros(dim)
        lr = 0.12
        train = labelled[:- max(1, len(labelled) // 4)] or labelled
        for _ in range(40):
            for row in train:
                h, _, _ = _encode(np.asarray(row["X"], dtype=float))
                p = _sig(float(h @ w + b))
                err = p - float(row["target"])
                w -= lr * err * h
                b -= lr * err
    out: list[dict[str, Any]] = []
    by_tkr: dict[str, list[dict[str, Any]]] = {}
    for row in seqs:
        by_tkr.setdefault(row["ticker"], []).append(row)
    for tkr, items in by_tkr.items():
        items = sorted(items, key=lambda r: r["quarter"])
        last = items[-1]
        h, att, sel = _encode(np.asarray(last["X"], dtype=float))
        base = _sig(float(h @ w + b)) if w is not None else float(np.mean(last["X"][-1]))
        for horizon in HORIZONS:
            drift = 0.03 * (horizon - 1)
            p = max(0.0, min(1.0, base + drift * (base - 0.5)))
            lo, mid, hi = _fan(p, horizon, residual)
            out.append({
                "ticker": tkr,
                "quarter": last["quarter"],
                "horizon": horizon,
                "p10": lo,
                "p50": mid,
                "p90": hi,
                "probability": mid,
                "attention": json.dumps([round(float(x), 4) for x in att]),
                "selection": json.dumps([round(float(x), 4) for x in sel]),
                "method": "numpy-tft",
            })
    return out


def _torch_forecast(seqs: list[dict[str, Any]]) -> list[dict[str, Any]] | None:
    if not _LOAD:
        return None
    try:
        import torch
        from torch import nn
    except Exception:
        return None
    if not seqs:
        return None
    dim = len(seqs[0]["X"][0])
    labelled = [s for s in seqs if s.get("target") is not None]
    if len(labelled) < 3:
        return None
    lstm = nn.LSTM(dim, 32, num_layers=1, batch_first=True)
    attn = nn.Linear(32, 1)
    head = nn.Linear(32, 1)
    opt = torch.optim.Adam(list(lstm.parameters()) + list(attn.parameters()) + list(head.parameters()), lr=0.02)
    train = labelled[:- max(1, len(labelled) // 4)] or labelled
    for _ in range(20):
        for row in train:
            x = torch.tensor([row["X"]], dtype=torch.float32)
            y = torch.tensor([[float(row["target"])]], dtype=torch.float32)
            h, _ = lstm(x)
            w = torch.softmax(attn(h).squeeze(-1), dim=-1)
            ctx = (w.unsqueeze(-1) * h).sum(dim=1)
            p = torch.sigmoid(head(ctx))
            loss = nn.functional.binary_cross_entropy(p, y)
            opt.zero_grad()
            loss.backward()
            opt.step()
    out = []
    lstm.eval()
    head.eval()
    with torch.no_grad():
        by_tkr: dict[str, list[dict[str, Any]]] = {}
        for row in seqs:
            by_tkr.setdefault(row["ticker"], []).append(row)
        for tkr, items in by_tkr.items():
            last = sorted(items, key=lambda r: r["quarter"])[-1]
            x = torch.tensor([last["X"]], dtype=torch.float32)
            h, _ = lstm(x)
            w = torch.softmax(attn(h).squeeze(-1), dim=-1)
            ctx = (w.unsqueeze(-1) * h).sum(dim=1)
            base = float(torch.sigmoid(head(ctx)).item())
            att = [round(float(v), 4) for v in w.squeeze().tolist()] if w.numel() else []
            for horizon in HORIZONS:
                p = max(0.0, min(1.0, base + 0.03 * (horizon - 1) * (base - 0.5)))
                lo, mid, hi = _fan(p, horizon, 0.12)
                out.append({
                    "ticker": tkr,
                    "quarter": last["quarter"],
                    "horizon": horizon,
                    "p10": lo,
                    "p50": mid,
                    "p90": hi,
                    "probability": mid,
                    "attention": json.dumps(att),
                    "selection": json.dumps([]),
                    "method": "torch-tft",
                })
    return out


def _compare(forecasts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    trees: list[dict[str, Any]] = []
    try:
        trees = fetch_table("sequence_predictions", limit=500)
    except Exception:
        pass
    rows = [{"model_name": "tft", "n": len(forecasts), "horizons": ",".join(str(h) for h in HORIZONS)}]
    if trees:
        rows.append({"model_name": "lstm/gru", "n": len(trees), "horizons": "1"})
    return rows


def fit_tft(ticker: str | None = None, sequences: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    seqs = sequences if sequences is not None else build_sequences(ticker)
    if ticker and seqs:
        seqs = [s for s in seqs if s["ticker"] == ticker.upper()]
    if not seqs:
        return {"forecasts": [], "comparison": [], "method": "none"}
    torch_rows = _torch_forecast(seqs)
    forecasts = torch_rows if torch_rows else _numpy_forecast(seqs)
    return {"forecasts": forecasts, "comparison": _compare(forecasts), "method": (forecasts[0]["method"] if forecasts else "none")}
