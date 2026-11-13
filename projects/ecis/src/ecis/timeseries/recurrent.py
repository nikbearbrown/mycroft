"""LSTM and GRU next-quarter revision heads. Torch stays off unless TIMESERIES_LOAD_TORCH=1."""

from __future__ import annotations

import os
from typing import Any

import numpy as np

from ecis.analytics.store import fetch_table
from ecis.timeseries.sequences import build_sequences

_LOAD = os.getenv("TIMESERIES_LOAD_TORCH", "").lower() in {"1", "true", "yes"}
HIDDEN = int(os.getenv("TIMESERIES_HIDDEN", "128" if _LOAD else "16"))
DROPOUT = 0.3
EPOCHS = int(os.getenv("TIMESERIES_EPOCHS", "40"))


def _sig(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -20, 20)))


def _auc(y: np.ndarray, p: np.ndarray) -> float | None:
    pos = p[y == 1]
    neg = p[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return None
    n = 0.0
    for a in pos:
        n += float(np.sum(a > neg) + 0.5 * np.sum(a == neg))
    return n / (len(pos) * len(neg))


def _metrics(y: list[int], p: np.ndarray) -> dict[str, Any]:
    y_arr = np.asarray(y, dtype=float)
    pred = (p >= 0.5).astype(int)
    acc = float((pred == y_arr).mean()) if len(y) else 0.0
    brier = float(np.mean((p - y_arr) ** 2)) if len(y) else None
    return {"accuracy": acc, "auc": _auc(y_arr, p), "brier": brier, "n": len(y)}


def _lstm_step(x, h, c, W, U, b, hid):
    z = W @ x + U @ h + b
    i = _sig(z[:hid])
    f = _sig(z[hid : 2 * hid])
    g = np.tanh(z[2 * hid : 3 * hid])
    o = _sig(z[3 * hid :])
    c = f * c + i * g
    h = o * np.tanh(c)
    return h, c


def _gru_step(x, h, W, U, b, hid):
    zlin = W @ x + U @ h + b
    zz = _sig(zlin[:hid])
    r = _sig(zlin[hid : 2 * hid])
    n = np.tanh((W[2 * hid :] @ x) + (U[2 * hid :] @ (r * h)) + b[2 * hid :])
    return (1 - zz) * h + zz * n


def _encode_lstm(seq: np.ndarray, W, U, b, hid: int) -> np.ndarray:
    h = np.zeros(hid)
    c = np.zeros(hid)
    for x in seq:
        h, c = _lstm_step(x, h, c, W, U, b, hid)
    return h


def _encode_gru(seq: np.ndarray, W, U, b, hid: int) -> np.ndarray:
    h = np.zeros(hid)
    for x in seq:
        h = _gru_step(x, h, W, U, b, hid)
    return h


def _init_gates(dim: int, hid: int, n_gates: int, rng: np.random.Generator):
    scale = 0.15 / max(dim, 1) ** 0.5
    W = rng.normal(0, scale, (n_gates * hid, dim))
    U = rng.normal(0, scale, (n_gates * hid, hid))
    b = np.zeros(n_gates * hid)
    if n_gates == 4:
        b[hid : 2 * hid] = 1.0  # forget bias
    return W, U, b


def _train_numpy(seqs: list[dict[str, Any]], kind: str, rng: np.random.Generator) -> dict[str, Any]:
    labelled = [s for s in seqs if s.get("target") is not None]
    dim = len(seqs[0]["X"][0]) if seqs else 1
    hid = min(HIDDEN, 32)
    n_gates = 4 if kind == "lstm" else 3
    W, U, b = _init_gates(dim, hid, n_gates, rng)
    w = np.zeros(hid)
    bias = 0.0
    encode = (lambda s: _encode_lstm(s, W, U, b, hid)) if kind == "lstm" else (lambda s: _encode_gru(s, W, U, b, hid))
    lr = 0.08
    train = labelled[:- max(1, len(labelled) // 4)] or labelled
    for _ in range(EPOCHS):
        for row in train:
            seq = np.asarray(row["X"], dtype=float)
            h = encode(seq)
            p = float(_sig(np.array([bias + h @ w]))[0])
            err = p - float(row["target"])
            w -= lr * err * h
            bias -= lr * err
            # truncated last-step recurrent update
            x = seq[-1]
            if kind == "lstm":
                h0 = encode(seq[:-1]) if len(seq) > 1 else np.zeros(hid)
                c0 = np.zeros(hid)
                h1, _ = _lstm_step(x, h0, c0, W, U, b, hid)
                grad_h = err * w
                W -= lr * 0.15 * np.outer(np.concatenate([grad_h, grad_h, grad_h, grad_h])[: 4 * hid], x)
            else:
                h0 = encode(seq[:-1]) if len(seq) > 1 else np.zeros(hid)
                h1 = _gru_step(x, h0, W, U, b, hid)
                grad_h = err * w
                W -= lr * 0.15 * np.outer(np.concatenate([grad_h, grad_h, grad_h])[: 3 * hid], x)
    return {"W": W, "U": U, "b": b, "w": w, "bias": bias, "hid": hid, "kind": kind, "method": "numpy"}


def _predict_numpy(seqs: list[dict[str, Any]], model: dict[str, Any]) -> list[dict[str, Any]]:
    hid = model["hid"]
    encode = (
        (lambda s: _encode_lstm(s, model["W"], model["U"], model["b"], hid))
        if model["kind"] == "lstm"
        else (lambda s: _encode_gru(s, model["W"], model["U"], model["b"], hid))
    )
    out = []
    for row in seqs:
        seq = np.asarray(row["X"], dtype=float)
        h = encode(seq)
        p = float(_sig(np.array([model["bias"] + h @ model["w"]]))[0])
        out.append({
            "ticker": row["ticker"],
            "quarter": row["quarter"],
            "model_name": model["kind"],
            "probability": p,
            "predicted": int(p >= 0.5),
            "actual": row.get("target"),
            "hidden_norm": float(np.linalg.norm(h)),
            "n_steps": row.get("n_steps"),
            "method": model["method"],
        })
    return out


def _torch_fit(seqs: list[dict[str, Any]], kind: str) -> dict[str, Any] | None:
    if not _LOAD:
        return None
    try:
        import torch
        from torch import nn
    except Exception:
        return None
    labelled = [s for s in seqs if s.get("target") is not None]
    if len(labelled) < 3:
        return None
    dim = len(seqs[0]["X"][0])
    hid = HIDDEN
    Cell = nn.LSTM if kind == "lstm" else nn.GRU
    cell = Cell(dim, hid, num_layers=2, dropout=DROPOUT, batch_first=True)
    head = nn.Linear(hid, 1)
    opt = torch.optim.Adam(list(cell.parameters()) + list(head.parameters()), lr=0.01)
    train = labelled[:- max(1, len(labelled) // 4)] or labelled
    cell.train()
    head.train()
    for _ in range(min(EPOCHS, 25)):
        for row in train:
            x = torch.tensor([row["X"]], dtype=torch.float32)
            y = torch.tensor([[float(row["target"])]], dtype=torch.float32)
            out, _ = cell(x)
            p = torch.sigmoid(head(out[:, -1, :]))
            loss = nn.functional.binary_cross_entropy(p, y)
            opt.zero_grad()
            loss.backward()
            opt.step()
    return {"cell": cell, "head": head, "kind": kind, "method": "torch"}


def _predict_torch(seqs: list[dict[str, Any]], model: dict[str, Any]) -> list[dict[str, Any]]:
    import torch

    cell, head = model["cell"], model["head"]
    cell.eval()
    head.eval()
    out = []
    with torch.no_grad():
        for row in seqs:
            x = torch.tensor([row["X"]], dtype=torch.float32)
            h, _ = cell(x)
            p = float(torch.sigmoid(head(h[:, -1, :])).item())
            hid = h[:, -1, :].numpy().ravel()
            out.append({
                "ticker": row["ticker"],
                "quarter": row["quarter"],
                "model_name": model["kind"],
                "probability": p,
                "predicted": int(p >= 0.5),
                "actual": row.get("target"),
                "hidden_norm": float(np.linalg.norm(hid)),
                "n_steps": row.get("n_steps"),
                "method": "torch",
            })
    return out


def _tree_rows() -> list[dict[str, Any]]:
    try:
        return fetch_table("revision_predictions", limit=500)
    except Exception:
        return []


def fit_sequence_models(ticker: str | None = None, sequences: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    seqs = sequences if sequences is not None else build_sequences(ticker)
    if not seqs:
        return {"predictions": [], "comparison": [], "trained": False, "method": "none"}
    rng = np.random.default_rng(7)
    preds: list[dict[str, Any]] = []
    comparison: list[dict[str, Any]] = []
    methods = {}
    for kind in ("lstm", "gru"):
        torch_model = _torch_fit(seqs, kind)
        if torch_model:
            rows = _predict_torch(seqs, torch_model)
            methods[kind] = "torch"
        else:
            model = _train_numpy(seqs, kind, rng)
            rows = _predict_numpy(seqs, model)
            methods[kind] = model["method"]
        preds.extend(rows)
        labelled = [r for r in rows if r.get("actual") is not None]
        if labelled:
            comparison.append({
                "model_name": kind,
                **_metrics([int(r["actual"]) for r in labelled], np.array([r["probability"] for r in labelled])),
                "method": methods[kind],
            })
    trees = _tree_rows()
    if ticker:
        trees = [r for r in trees if (r.get("ticker") or "").upper() == ticker.upper()]
    by_model: dict[str, list[dict[str, Any]]] = {}
    for row in trees:
        by_model.setdefault(row.get("model_name") or "tree", []).append(row)
    for name, items in by_model.items():
        labelled = [r for r in items if r.get("actual") is not None and r.get("probability") is not None]
        if not labelled:
            continue
        comparison.append({
            "model_name": name,
            **_metrics([int(r["actual"]) for r in labelled], np.array([float(r["probability"]) for r in labelled])),
            "method": "tree",
        })
    return {
        "predictions": preds,
        "comparison": comparison,
        "trained": True,
        "method": methods.get("lstm", "numpy"),
    }
