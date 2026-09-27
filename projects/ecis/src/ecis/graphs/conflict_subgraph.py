"""Four-node LangGraph subgraph for resolving reader conflicts (Category C chunks)."""

from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import END, StateGraph

from ecis.extraction.conflict_resolver import resolve_conflict, retrieve_surrounding_chunks
from ecis.schemas.state import ConflictState

logger = logging.getLogger(__name__)


def context_retrieval_node(state: ConflictState) -> dict:
    """Node 1: Retrieve surrounding chunks for context."""
    preceding, following = retrieve_surrounding_chunks(
        state["ticker"],
        state["chunk_index"],
    )
    return {
        "preceding_chunk": preceding or None,
        "following_chunk": following or None,
    }


def disagreement_prompt_node(state: ConflictState) -> dict:
    """Node 2: Build the disagreement resolution prompt."""
    keyword_info = (
        f"Direction: {state.get('keyword_direction', 'N/A')}, "
        f"Phrases: {state.get('keyword_phrases', [])}"
    )
    finbert_scores = state.get("finbert_scores", {})
    finbert_info = (
        f"Direction: {state.get('finbert_direction', 'N/A')}, "
        f"Positive: {finbert_scores.get('positive', 0):.3f}, "
        f"Negative: {finbert_scores.get('negative', 0):.3f}, "
        f"Neutral: {finbert_scores.get('neutral', 0):.3f}"
    )

    prompt = (
        f"Keyword reader: {keyword_info}\n"
        f"FinBERT: {finbert_info}\n"
        f"Preceding: {state.get('preceding_chunk', '(N/A)')}\n"
        f"Chunk: {state['chunk_text']}\n"
        f"Following: {state.get('following_chunk', '(N/A)')}"
    )
    return {"resolution_prompt": prompt}


def llm_resolution_node(state: ConflictState) -> dict:
    """Node 3: Call the LLM to resolve the conflict."""
    keyword_result = {
        "direction": state.get("keyword_direction"),
        "phrases": state.get("keyword_phrases", []),
    }
    finbert_result = {
        "direction": state.get("finbert_direction"),
        **(state.get("finbert_scores") or {}),
    }

    result = resolve_conflict(
        chunk_text=state["chunk_text"],
        ticker=state["ticker"],
        chunk_index=state["chunk_index"],
        keyword_result=keyword_result,
        finbert_result=finbert_result,
    )

    return {
        "resolved_direction": result.get("resolved_direction"),
        "resolved_confidence": result.get("confidence", 0.0),
        "vindicated_reader": result.get("vindicated_reader"),
        "resolution_reasoning": result.get("reasoning", ""),
    }


def vindication_recording_node(state: ConflictState) -> dict:
    """Node 4: Record which reader was vindicated (already done in resolve_conflict)."""
    logger.info(
        "Conflict resolved for chunk %d: direction=%s, vindicated=%s",
        state["chunk_index"],
        state.get("resolved_direction"),
        state.get("vindicated_reader"),
    )
    return {}


def build_conflict_subgraph() -> StateGraph:
    """Build and compile the four-node conflict resolution subgraph."""
    graph = StateGraph(ConflictState)

    graph.add_node("context_retrieval", context_retrieval_node)
    graph.add_node("disagreement_prompt", disagreement_prompt_node)
    graph.add_node("llm_resolution", llm_resolution_node)
    graph.add_node("vindication_recording", vindication_recording_node)

    graph.set_entry_point("context_retrieval")
    graph.add_edge("context_retrieval", "disagreement_prompt")
    graph.add_edge("disagreement_prompt", "llm_resolution")
    graph.add_edge("llm_resolution", "vindication_recording")
    graph.add_edge("vindication_recording", END)

    return graph


_compiled_subgraph = None


def get_conflict_subgraph():
    """Return the compiled conflict resolution subgraph (singleton)."""
    global _compiled_subgraph
    if _compiled_subgraph is None:
        _compiled_subgraph = build_conflict_subgraph().compile()
    return _compiled_subgraph
