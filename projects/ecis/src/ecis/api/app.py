"""ECIS FastAPI — REST endpoints for signals, scores, and RAG queries."""

from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="ECIS API", version="0.1.0")


class RAGQuery(BaseModel):
    query: str
    n_results: int = 5
    ticker: str | None = None
    section_label: str | None = None


class RAGResult(BaseModel):
    text: str
    metadata: dict[str, Any]
    similarity: float


class ExtractRequest(BaseModel):
    ticker: str
    transcript_path: str | None = None
    transcript_text: str | None = None
    model: str | None = None  # llama | mistral | qwen | both | all | ollama tag


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/signals")
def list_signals(
    ticker: str | None = Query(None),
    direction: str | None = Query(None),
    source_method: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """Query extracted signals with optional filters."""
    from ecis.db.init_db import get_connection

    conn = get_connection("signals")
    query = "SELECT * FROM signals"
    conditions = []
    params: list[Any] = []

    if ticker:
        conditions.append("ticker = ?")
        params.append(ticker)
    if direction:
        conditions.append("direction = ?")
        params.append(direction)
    if source_method:
        conditions.append("source_method = ?")
        params.append(source_method)
    if date_from:
        conditions.append("transcript_date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("transcript_date <= ?")
        params.append(date_to)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/signals/{signal_id}")
def get_signal(signal_id: int):
    """Get a single signal by ID."""
    from ecis.db.init_db import get_connection

    conn = get_connection("signals")
    row = conn.execute("SELECT * FROM signals WHERE signal_id = ?", (signal_id,)).fetchone()
    conn.close()

    if not row:
        raise HTTPException(404, f"Signal {signal_id} not found")
    return dict(row)


@app.get("/signals/{signal_id}/outcomes")
def get_signal_outcomes(signal_id: int):
    """Get outcomes for a specific signal."""
    from ecis.db.init_db import get_connection

    conn = get_connection("outcomes")
    rows = conn.execute("SELECT * FROM outcomes WHERE signal_id = ?", (signal_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/scores")
def get_scores(
    ticker: str | None = Query(None),
    horizon: int | None = Query(None),
):
    """Get scoring metrics for all readers."""
    from ecis.scoring.scorer import score_all_readers

    results = score_all_readers(ticker=ticker, horizon=horizon)
    for r in results:
        r.pop("ece_bins", None)
    return results


@app.get("/scores/{source_method}")
def get_reader_score(
    source_method: str,
    ticker: str | None = Query(None),
    horizon: int | None = Query(None),
):
    """Get detailed scoring metrics for a specific reader."""
    from ecis.scoring.scorer import score_reader

    return score_reader(source_method=source_method, ticker=ticker, horizon=horizon)


@app.post("/query", response_model=list[RAGResult])
def rag_query(body: RAGQuery):
    """Semantic similarity search over transcript chunks."""
    from ecis.embedding.embedder import query_similar

    results = query_similar(
        body.query,
        n_results=body.n_results,
        ticker=body.ticker,
        section_label=body.section_label,
    )

    return [
        RAGResult(
            text=r["text"],
            metadata=r["metadata"],
            similarity=round(1.0 - r["distance"], 4),
        )
        for r in results
    ]


@app.get("/tickers")
def list_tickers():
    """List tickers from the registry, falling back to the signals log."""
    try:
        from ecis.db.ticker_registry import list_tickers as registry_list

        rows = registry_list()
        if rows:
            return rows
    except Exception:
        pass

    from ecis.db.init_db import get_connection

    conn = get_connection("signals")
    rows = conn.execute("SELECT DISTINCT ticker FROM signals ORDER BY ticker").fetchall()
    conn.close()
    return [r["ticker"] for r in rows]


@app.post("/extract")
def extract_transcript(body: ExtractRequest):
    """Run the extraction pipeline on a transcript file or inline text."""
    import tempfile
    from pathlib import Path

    from ecis.config.settings import settings
    from ecis.graphs.pipeline_graph import run_pipeline

    ticker = body.ticker.upper().strip()
    if not ticker:
        raise HTTPException(400, "ticker is required")

    transcript_path = body.transcript_path
    tmp_path = None
    if not transcript_path:
        if not body.transcript_text:
            raise HTTPException(400, "Provide transcript_path or transcript_text")
        tmp = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            prefix=f"{ticker}_",
            delete=False,
            encoding="utf-8",
        )
        tmp.write(body.transcript_text)
        tmp.close()
        transcript_path = tmp.name
        tmp_path = Path(transcript_path)

    models = settings.resolve_llm_models(body.model)
    all_signals: list[dict[str, Any]] = []
    try:
        for model in models:
            signals = run_pipeline(ticker, transcript_path, llm_model=model)
            for s in signals:
                payload = s.model_dump(mode="json")
                payload["llm_model"] = s.llm_model or model
                all_signals.append(payload)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, f"Extraction failed: {exc}") from exc
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)

    return {
        "ticker": ticker,
        "models": models,
        "n_signals": len(all_signals),
        "signals": all_signals,
    }


@app.get("/scorecard")
def get_scorecard(
    ticker: str | None = Query(None),
    horizon: int | None = Query(None),
):
    """Full scoring report: readers, models, recent agent activity, pending HITL."""
    from ecis.db.init_db import get_connection
    from ecis.scoring.scorer import score_all_readers, score_by_llm_model, score_by_trend

    readers = score_all_readers(ticker=ticker, horizon=horizon)
    for r in readers:
        r.pop("ece_bins", None)

    conn = get_connection("agents")
    actions = conn.execute(
        "SELECT * FROM agent_actions ORDER BY created_at DESC LIMIT 25"
    ).fetchall()
    pending = conn.execute(
        "SELECT approval_id, agent_name, action_type, status, created_at "
        "FROM pending_approvals WHERE status = 'pending' ORDER BY created_at DESC"
    ).fetchall()
    weights = conn.execute("SELECT * FROM reader_weights").fetchall()
    conn.close()

    return {
        "readers": readers,
        "by_model": score_by_llm_model(ticker=ticker, horizon=horizon),
        "by_trend": score_by_trend(ticker=ticker, horizon=horizon),
        "reader_weights": [dict(r) for r in weights],
        "pending_approvals": [dict(r) for r in pending],
        "recent_agent_activity": [dict(r) for r in actions],
    }


@app.get("/approvals")
def list_approvals():
    from ecis.db.approvals import list_pending

    return list_pending()


class ApprovalDecision(BaseModel):
    note: str = ""


@app.post("/approvals/{approval_id}/approve")
def approve(approval_id: int, body: ApprovalDecision | None = None):
    from ecis.db.approvals import resolve_approval

    try:
        return resolve_approval(approval_id, approved=True, note=(body.note if body else ""))
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post("/approvals/{approval_id}/reject")
def reject(approval_id: int, body: ApprovalDecision | None = None):
    from ecis.db.approvals import resolve_approval

    try:
        return resolve_approval(approval_id, approved=False, note=(body.note if body else ""))
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
