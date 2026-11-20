"""Multi-step plan → execute → synthesise chains with stored traces."""

from __future__ import annotations

import json
import re
from typing import Any
from uuid import uuid4

from ecis.db.init_db import get_connection
from ecis.forecasting.compare import synthesise_comparison
from ecis.intelligence.intent import parse_intent
from ecis.timeseries.rag import hybrid_answer

_MULTI = re.compile(r"(?i)\bthen\b|\boutlier\b|compare.{0,40}explain|explain.{0,20}outlier")


def is_multistep(query: str) -> bool:
    parsed = parse_intent(query or "")
    return bool(_MULTI.search(query or "")) or (
        parsed["intent"] == "comparison" and "explain" in (query or "").lower()
    )


def plan_chain(query: str) -> list[str]:
    parsed = parse_intent(query)
    if is_multistep(query) or parsed["intent"] == "comparison":
        return ["parse", "retrieve", "compare", "outlier", "quotes", "synthesise"]
    if parsed["intent"] == "explanation":
        return ["parse", "shap", "synthesise"]
    if parsed["intent"] == "analysis":
        return ["parse", "scan", "synthesise"]
    return ["parse", "retrieve", "synthesise"]


def _persist_trace(session_id: str, traces: list[dict[str, Any]]) -> None:
    try:
        conn = get_connection("agents")
        for i, step in enumerate(traces):
            conn.execute(
                """INSERT INTO reasoning_traces
                   (session_id, step_index, step_name, input, output)
                   VALUES (?, ?, ?, ?, ?)""",
                (session_id, i, step.get("step"), json.dumps(step.get("input")), json.dumps(step.get("output"))),
            )
        conn.commit()
        conn.close()
    except Exception:
        pass


def run_chain(query: str, session_id: str | None = None) -> dict[str, Any]:
    sid = session_id or uuid4().hex[:16]
    steps = plan_chain(query)
    traces: list[dict[str, Any]] = []
    parsed = parse_intent(query)
    traces.append({"step": "parse", "input": query, "output": parsed})
    comparison = synthesise_comparison(query)
    traces.append({"step": "compare", "input": parsed, "output": {"tickers": comparison.get("tickers")}})
    if "outlier" in steps:
        traces.append({"step": "outlier", "input": comparison.get("tickers"), "output": comparison.get("outlier")})
    hybrid = hybrid_answer(query)
    traces.append({"step": "quotes", "input": query, "output": {"n": len(hybrid.get("quotes") or [])}})
    parts = [comparison.get("text") or "", hybrid.get("text") or ""]
    if comparison.get("outlier"):
        o = comparison["outlier"]
        parts.append(f"explanation: {o.get('ticker')} is the dodge outlier in {o.get('quarter')}.")
    text = "\n\n".join(p for p in parts if p)
    traces.append({"step": "synthesise", "input": steps, "output": {"n_chars": len(text)}})
    _persist_trace(sid, traces)
    return {
        "session_id": sid,
        "intent": comparison.get("intent") or parsed["intent"],
        "tickers": parsed.get("tickers"),
        "tables": comparison.get("tables") or hybrid.get("tables"),
        "text": text,
        "quotes": hybrid.get("quotes") or [],
        "citations": comparison.get("citations") or [],
        "steps": steps,
        "traces": traces,
        "retrieval": "chain",
        "query": query,
    }
