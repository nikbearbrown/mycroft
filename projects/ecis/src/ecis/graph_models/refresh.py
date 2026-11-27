"""Persist GNN, VAE, entity links, summaries, arguments, and wavelet snapshots."""

from __future__ import annotations

from typing import Any

from ecis.analytics.store import replace_rows
from ecis.graph_models.arguments import mine_arguments
from ecis.graph_models.domain_lm import finetune_status
from ecis.graph_models.entity_link import link_mentions
from ecis.graph_models.gat import run_gat
from ecis.graph_models.summarize import summarize_calls
from ecis.graph_models.vae import detect_anomalies
from ecis.graph_models.wavelet import decompose_wavelets


def refresh_graph_models(ticker: str | None = None) -> dict[str, Any]:
    gat = run_gat(ticker=ticker)
    vae = detect_anomalies(ticker)
    entities = link_mentions(ticker)
    summaries = summarize_calls(ticker)
    args = mine_arguments(ticker)
    wave = decompose_wavelets(ticker)
    lm = finetune_status()

    counts = {
        "graph_nodes": replace_rows(
            "graph_nodes",
            gat.get("nodes") or [],
            ("ticker", "quarter", "n_neighbors", "neighbor_risk", "embedding", "method"),
        ),
        "graph_edges": replace_rows(
            "graph_edges",
            gat.get("edges") or [],
            ("src", "dst", "kind", "weight", "attention", "lag", "granger_r", "method"),
        ),
        "graph_predictions": replace_rows(
            "graph_predictions",
            gat.get("predictions") or [],
            ("ticker", "quarter", "probability", "predicted", "actual", "own_score", "neighbor_score", "method"),
        ),
        "vae_anomalies": replace_rows(
            "vae_anomalies",
            vae,
            ("ticker", "quarter", "transcript_date", "recon_error", "latent", "flag", "threshold", "method"),
        ),
        "entity_mentions": replace_rows(
            "entity_mentions",
            entities,
            ("ticker_source", "transcript_date", "quarter", "mention", "linked_ticker", "confidence", "context", "method"),
        ),
        "call_summaries": replace_rows(
            "call_summaries",
            summaries,
            ("ticker", "transcript_date", "quarter", "extractive", "abstractive", "highlights", "n_sentences", "method"),
        ),
        "arguments": replace_rows(
            "arguments",
            args,
            ("ticker", "transcript_date", "quarter", "speaker", "claim", "evidence", "warrant", "strength", "specificity", "method"),
        ),
        "wavelet_components": replace_rows(
            "wavelet_components",
            wave,
            ("ticker", "signal_type", "quarter", "low", "mid", "high", "observed", "method"),
        ),
    }
    return {"ticker": ticker, "tables": counts, "domain_lm": lm, "gat_method": gat.get("method")}
