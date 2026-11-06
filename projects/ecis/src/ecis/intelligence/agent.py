"""Plan → execute → synthesise. LangGraph is optional; the default path is in-process."""

from __future__ import annotations

import json
import os
from typing import Any
from uuid import uuid4

from ecis.db.init_db import get_connection
from ecis.intelligence.execute import run_query
from ecis.intelligence.intent import parse_intent

_LOAD = os.getenv("INTELLIGENCE_LOAD_LANGGRAPH", "").lower() in {"1", "true", "yes"}


def _session_id(session_id: str | None) -> str:
    return session_id or uuid4().hex[:16]


def _persist(session_id: str, role: str, content: str, intent: str | None = None, payload: dict | None = None) -> None:
    try:
        conn = get_connection("agents")
        conn.execute(
            """INSERT INTO agent_turns (session_id, role, content, intent, payload)
               VALUES (?, ?, ?, ?, ?)""",
            (session_id, role, content, intent, json.dumps(payload) if payload else None),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def plan(query: str) -> list[str]:
    parsed = parse_intent(query)
    intent = parsed["intent"]
    if intent == "comparison":
        return ["parse", "fetch_each", "compare", "synthesise"]
    if intent == "analysis":
        return ["parse", "scan", "synthesise"]
    if intent == "explanation":
        return ["parse", "shap", "synthesise"]
    return ["parse", "retrieve", "synthesise"]


def _langgraph_ask(query: str, session_id: str) -> dict[str, Any] | None:
    if not _LOAD:
        return None
    try:
        from langgraph.graph import END, StateGraph

        def _plan(state: dict) -> dict:
            state["steps"] = plan(state["query"])
            return state

        def _exec(state: dict) -> dict:
            state["result"] = run_query(state["query"])
            return state

        def _synth(state: dict) -> dict:
            result = state.get("result") or {}
            state["text"] = result.get("text") or ""
            return state

        graph = StateGraph(dict)
        graph.add_node("plan", _plan)
        graph.add_node("execute", _exec)
        graph.add_node("synthesise", _synth)
        graph.set_entry_point("plan")
        graph.add_edge("plan", "execute")
        graph.add_edge("execute", "synthesise")
        graph.add_edge("synthesise", END)
        app = graph.compile()
        return app.invoke({"query": query, "session_id": session_id})
    except Exception:
        return None


def ask(query: str, session_id: str | None = None) -> dict[str, Any]:
    sid = _session_id(session_id)
    _persist(sid, "user", query)
    steps = plan(query)
    lg = _langgraph_ask(query, sid)
    result = (lg or {}).get("result") if lg else run_query(query)
    if not result:
        result = run_query(query)
    text = (lg or {}).get("text") or result.get("text") or ""
    payload = {
        "session_id": sid,
        "steps": steps,
        "intent": result.get("intent"),
        "tickers": result.get("tickers"),
        "tables": result.get("tables"),
        "text": text,
        "method": "langgraph" if lg else "direct",
    }
    _persist(sid, "assistant", text, result.get("intent"), payload)
    return payload
