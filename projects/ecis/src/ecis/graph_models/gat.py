"""Graph Attention Network."""

from __future__ import annotations

import json
import math
import os
from collections import defaultdict
from typing import Any

import numpy as np

from ecis.graph_models.graph import build_graph

_LOAD = os.getenv("GRAPH_LOAD_TORCH", "").lower() in {"1", "true", "yes"}
HIDDEN = 8


def _softmax(z: np.ndarray) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    z = z - np.max(z)
    e = np.exp(np.clip(z, -20, 20))
    return e / (e.sum() or 1.0)


def _sig(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-20.0, min(20.0, z))))


def _layer(H: np.ndarray, nbrs: dict[int, list[tuple[int, np.ndarray]]], W: np.ndarray, a: np.ndarray) -> tuple[np.ndarray, dict[tuple[int, int], float]]:
    HW = H @ W
    out = np.zeros_like(HW)
    attn: dict[tuple[int, int], float] = {}
    for i in range(len(H)):
        js = nbrs.get(i) or [(i, np.array([0.4, 0.0, 0.0]))]
        scores = []
        for j, efeat in js:
            cat = np.concatenate([HW[i], HW[j], efeat])
            scores.append(float(np.dot(a, cat)))
        alpha = _softmax(np.array(scores))
        acc = np.zeros(HW.shape[1])
        for k, (j, _) in enumerate(js):
            attn[(i, j)] = float(alpha[k])
            acc += alpha[k] * HW[j]
        out[i] = np.tanh(acc)
    return out, attn


def _neighbors(n_nodes: int, index: dict[str, int], edges: list[dict[str, Any]]) -> dict[int, list[tuple[int, np.ndarray]]]:
    nbrs: dict[int, list[tuple[int, np.ndarray]]] = defaultdict(list)
    for i in range(n_nodes):
        nbrs[i].append((i, np.array([0.5, 0.0, 0.0])))
    for e in edges:
        i = index.get(e["src"])
        j = index.get(e["dst"])
        if i is None or j is None:
            continue
        feat = np.array([
            float(e.get("weight") or 0),
            float(e.get("lag") or 0) / 4.0,
            float(e.get("granger_r") or 0) if e.get("granger_r") is not None else 0.0,
        ])
        nbrs[i].append((j, feat))
    return nbrs


def run_gat(graph: dict[str, Any] | None = None, ticker: str | None = None) -> dict[str, Any]:
    graph = graph if graph is not None else build_graph(ticker)
    nodes = graph.get("nodes") or []
    edges = graph.get("edges") or []
    if not nodes:
        return {"nodes": [], "edges": [], "predictions": []}
    index = {n["ticker"]: i for i, n in enumerate(nodes)}
    X = np.array([n["vector"] if n.get("vector") else [0.0] * 9 for n in nodes], dtype=float)
    if X.ndim != 2:
        X = np.zeros((len(nodes), 9))
    dim = X.shape[1]
    hid = min(HIDDEN, max(dim, 4))
    rng = np.random.default_rng(7)
    W1 = rng.normal(0, 0.2, (dim, hid))
    W2 = rng.normal(0, 0.2, (hid, hid))
    a1 = rng.normal(0, 0.1, hid * 2 + 3)
    a2 = rng.normal(0, 0.1, hid * 2 + 3)
    nbrs = _neighbors(len(nodes), index, edges)
    H1, att1 = _layer(X, nbrs, W1, a1)
    H2, att2 = _layer(H1, nbrs, W2, a2)
    w = np.zeros(hid * 2)
    b = 0.0
    labelled = [(i, int(n["target"])) for i, n in enumerate(nodes) if n.get("target") is not None]
    if labelled:
        lr = 0.08
        for _ in range(30):
            for i, y in labelled:
                h = np.concatenate([H2[i], H1[i]])
                p = _sig(float(h @ w + b))
                err = p - y
                w -= lr * err * h
                b -= lr * err
    node_rows = []
    pred_rows = []
    for i, n in enumerate(nodes):
        neigh = [j for j, _ in nbrs[i] if j != i]
        neighbor_risk = float(np.mean([X[j, 0] for j in neigh])) if neigh else 0.0
        h = np.concatenate([H2[i], H1[i]])
        p = _sig(float(h @ w + b)) if labelled else _sig(neighbor_risk)
        own = float(X[i, 0])
        node_rows.append({
            "ticker": n["ticker"],
            "quarter": n.get("quarter"),
            "n_neighbors": len(neigh),
            "neighbor_risk": neighbor_risk,
            "embedding": json.dumps([round(float(x), 4) for x in H2[i]]),
            "method": "numpy-gat",
        })
        pred_rows.append({
            "ticker": n["ticker"],
            "quarter": n.get("quarter"),
            "probability": p,
            "predicted": int(p >= 0.5),
            "actual": n.get("target"),
            "own_score": own,
            "neighbor_score": neighbor_risk,
            "method": "numpy-gat",
        })
    edge_rows = []
    for e in edges:
        i = index.get(e["src"])
        j = index.get(e["dst"])
        alpha = att2.get((i, j), att1.get((i, j), e.get("weight") or 0)) if i is not None and j is not None else e.get("weight")
        edge_rows.append({
            "src": e["src"],
            "dst": e["dst"],
            "kind": e["kind"],
            "weight": e.get("weight"),
            "attention": float(alpha or 0),
            "lag": e.get("lag"),
            "granger_r": e.get("granger_r"),
            "method": "numpy-gat",
        })
    return {"nodes": node_rows, "edges": edge_rows, "predictions": pred_rows, "method": "numpy-gat"}
