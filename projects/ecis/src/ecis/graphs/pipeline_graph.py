"""Top-level LangGraph pipeline connecting all extraction components."""

from __future__ import annotations

import hashlib
import logging
import re
from datetime import date
from pathlib import Path
from typing import Any

from langgraph.graph import END, StateGraph

from ecis.config.settings import settings
from ecis.extraction.conflict_resolver import resolve_conflict
from ecis.extraction.deduplicator import deduplicate_signals
from ecis.extraction.triangulator import log_signal, triangulate_chunk
from ecis.graphs.orchestration_agent import classify_chunks
from ecis.preprocessing.cleaner import clean_file
from ecis.preprocessing.normaliser import normalise_transcript
from ecis.readers import (
    finbert_read_batch,
    keyword_read_batch,
    ner_read_batch,
)
from ecis.schemas.signal import FastPassResult, GuidanceDirection, SignalRecord
from ecis.schemas.state import EscalationCategory, PipelineState

logger = logging.getLogger(__name__)

_DATE_IN_NAME = re.compile(r"(20\d{2}-\d{2}-\d{2})")


def _transcript_date_from_path(transcript_path: str) -> str:
    """Prefer period-of-report from file_metadata; else parse filename; else today."""
    try:
        from ecis.db.init_db import get_connection

        conn = get_connection("agents")
        row = conn.execute(
            "SELECT period_of_report, filing_date FROM file_metadata WHERE file_path = ?",
            (transcript_path,),
        ).fetchone()
        conn.close()
        if row:
            for key in ("period_of_report", "filing_date"):
                value = row[key]
                if value:
                    return str(value)[:10]
    except Exception:
        pass
    stem = Path(transcript_path).stem
    match = _DATE_IN_NAME.search(stem)
    if match:
        try:
            return str(date.fromisoformat(match.group(1)))
        except ValueError:
            pass
    logger.warning("Could not parse transcript date from %s; using today", transcript_path)
    return str(date.today())


def ingestion_node(state: PipelineState) -> dict:
    """Load and clean a transcript file."""
    path = Path(state["transcript_path"])
    if not path.exists():
        return {"errors": [f"File not found: {path}"], "transcript_text": ""}

    cleaned = clean_file(path)
    normalised = normalise_transcript(cleaned)
    return {"transcript_text": normalised}


def chunking_node(state: PipelineState) -> dict:
    """Chunk the normalised transcript text."""
    from ecis.preprocessing.chunker import _parse_sections, chunk_text

    text = state.get("transcript_text", "")
    ticker = state.get("ticker", "UNKNOWN")
    transcript_date = _transcript_date_from_path(state.get("transcript_path", ""))
    sections = _parse_sections(text)

    chunks: list[dict[str, Any]] = []
    idx = 0
    for section in sections:
        raw_chunks = chunk_text(section["text"])
        for chunk_str, char_start, char_end in raw_chunks:
            chunks.append({
                "chunk_index": idx,
                "text": chunk_str,
                "ticker": ticker,
                "transcript_date": transcript_date,
                "section_label": section["section_label"],
                "speaker": section["speaker"],
                "char_start": char_start,
                "char_end": char_end,
                "source_file": state.get("transcript_path", ""),
                "content_hash": hashlib.sha256(chunk_str.strip().lower().encode("utf-8")).hexdigest()[:16],
            })
            idx += 1

    from ecis.preprocessing.chunk_validator import filter_chunks, log_rejections

    accepted, rejected = filter_chunks(chunks)
    if rejected:
        log_rejections(rejected)
        logger.info("Rejected %d chunks before extraction", len(rejected))
        for i, chunk in enumerate(accepted):
            chunk["chunk_index"] = i

    return {"chunks": accepted, "rejected_chunks": rejected}


def fast_pass_node(state: PipelineState) -> dict:
    """Run keyword and FinBERT readers on all chunks in parallel."""
    chunks = state.get("chunks", [])
    if not chunks:
        return {"fast_pass_results": []}

    kw_results = keyword_read_batch(chunks)
    fb_results = finbert_read_batch(chunks)

    fast_pass_results: list[FastPassResult] = []
    for i, chunk in enumerate(chunks):
        kw = kw_results[i] if i < len(kw_results) else {}
        fb = fb_results[i] if i < len(fb_results) else {}

        fp = FastPassResult(
            chunk_index=chunk["chunk_index"],
            chunk_text=chunk["text"],
            keyword_matched=kw.get("matched", False),
            keyword_direction=GuidanceDirection(kw["direction"]) if kw.get("direction") else None,
            keyword_phrases=kw.get("phrases", []),
            keyword_confidence=kw.get("confidence", 0.0),
            finbert_positive=fb.get("positive", 0.0),
            finbert_negative=fb.get("negative", 0.0),
            finbert_neutral=fb.get("neutral", 0.0),
            finbert_dominant=fb.get("dominant"),
            finbert_confidence=fb.get("confidence", 0.0),
            finbert_direction=fb.get("direction"),
        )
        fast_pass_results.append(fp)

    return {
        "fast_pass_results": fast_pass_results,
        "keyword_signals": kw_results,
        "finbert_signals": fb_results,
    }


def escalation_node(state: PipelineState) -> dict:
    """Classify chunks into A/B/C/D categories."""
    fp_results = state.get("fast_pass_results", [])
    chunks = state.get("chunks", [])
    transcript_date = chunks[0].get("transcript_date") if chunks else None
    categories = classify_chunks(
        fp_results,
        ticker=state.get("ticker"),
        transcript_date=transcript_date,
    )
    return {
        "category_a_indices": categories.get(EscalationCategory.A, []),
        "category_b_indices": categories.get(EscalationCategory.B, []),
        "category_c_indices": categories.get(EscalationCategory.C, []),
        "category_d_indices": categories.get(EscalationCategory.D, []),
    }


def llm_extraction_node(state: PipelineState) -> dict:
    """Run LLM extraction on Category A and B chunks."""
    from ecis.readers.llm_reader import read_chunks as llm_read_chunks

    chunks = state.get("chunks", [])
    a_indices = set(state.get("category_a_indices", []))
    b_indices = set(state.get("category_b_indices", []))
    target_indices = a_indices | b_indices

    target_chunks = [c for c in chunks if c["chunk_index"] in target_indices]
    if not target_chunks:
        return {"llm_signals": []}

    ticker = state.get("ticker", "UNKNOWN")
    model = state.get("llm_model") or settings.llm_model
    results = llm_read_chunks(target_chunks, ticker, model=model)
    chunk_models = dict(state.get("chunk_models") or {})
    for chunk in target_chunks:
        chunk_models[chunk["chunk_index"]] = model
    return {"llm_signals": results, "chunk_models": chunk_models}


def conflict_resolution_node(state: PipelineState) -> dict:
    """Resolve conflicts for Category C chunks."""
    chunks = state.get("chunks", [])
    c_indices = set(state.get("category_c_indices", []))
    fp_results = state.get("fast_pass_results", [])

    chunk_map = {c["chunk_index"]: c for c in chunks}
    fp_map = {fp.chunk_index: fp for fp in fp_results}

    resolutions = []
    for idx in c_indices:
        chunk = chunk_map.get(idx)
        fp = fp_map.get(idx)
        if not chunk or not fp:
            continue

        kw_result = {
            "direction": fp.keyword_direction.value if fp.keyword_direction else None,
            "phrases": fp.keyword_phrases,
        }
        fb_result = {
            "direction": fp.finbert_direction.value if fp.finbert_direction else None,
            "positive": fp.finbert_positive,
            "negative": fp.finbert_negative,
            "neutral": fp.finbert_neutral,
        }

        result = resolve_conflict(
            chunk_text=chunk["text"],
            ticker=state.get("ticker", "UNKNOWN"),
            chunk_index=idx,
            keyword_result=kw_result,
            finbert_result=fb_result,
        )
        result["chunk_index"] = idx
        resolutions.append(result)

    return {"conflict_resolutions": resolutions}


def ner_node(state: PipelineState) -> dict:
    """Run NER on chunks that have signals (A, B, C categories)."""
    chunks = state.get("chunks", [])
    a = set(state.get("category_a_indices", []))
    b = set(state.get("category_b_indices", []))
    c = set(state.get("category_c_indices", []))
    target_indices = a | b | c

    target_chunks = [c for c in chunks if c["chunk_index"] in target_indices]
    if not target_chunks:
        return {"ner_results": []}

    results = ner_read_batch(target_chunks)
    return {"ner_results": results}


def triangulation_node(state: PipelineState) -> dict:
    """Combine all reader outputs into unified signals."""
    chunks = state.get("chunks", [])
    kw_signals = state.get("keyword_signals", [])
    fb_signals = state.get("finbert_signals", [])
    llm_signals = state.get("llm_signals", [])
    ner_results = state.get("ner_results", [])
    conflict_resolutions = state.get("conflict_resolutions", [])

    chunk_map = {c["chunk_index"]: c for c in chunks}
    kw_map = {s.get("chunk_index", i): s for i, s in enumerate(kw_signals)}
    fb_map = {s.get("chunk_index", i): s for i, s in enumerate(fb_signals)}
    llm_map = {s.get("chunk_index"): s for s in llm_signals}
    ner_map = {s.get("chunk_index"): s for s in ner_results}
    cr_map = {s.get("chunk_index"): s for s in conflict_resolutions}

    a = set(state.get("category_a_indices", []))
    b = set(state.get("category_b_indices", []))
    c = set(state.get("category_c_indices", []))
    signal_indices = a | b | c

    signals: list[SignalRecord] = []
    for idx in sorted(signal_indices):
        chunk = chunk_map.get(idx)
        if not chunk:
            continue

        llm_result = llm_map.get(idx)
        if idx in c and not llm_result:
            cr = cr_map.get(idx)
            if cr:
                llm_result = {
                    "direction": cr.get("resolved_direction"),
                    "confidence": cr.get("confidence", 0.0),
                    "supporting_quote": chunk["text"][:200],
                    "reasoning": cr.get("reasoning", ""),
                    "llm_model": state.get("llm_model"),
                }

        signal = triangulate_chunk(
            chunk=chunk,
            keyword_result=kw_map.get(idx),
            finbert_result=fb_map.get(idx),
            llm_result=llm_result,
            ner_result=ner_map.get(idx),
        )
        if signal:
            signals.append(signal)

    return {"triangulated_signals": signals}


def deduplication_node(state: PipelineState) -> dict:
    """Deduplicate signals within the transcript."""
    signals = state.get("triangulated_signals", [])
    if not signals:
        return {"final_signals": []}

    signal_dicts = [s.model_dump() for s in signals]
    deduplicated, flagged = deduplicate_signals(signal_dicts)

    if flagged:
        logger.warning("Deduplication flagged %d conflicts for review", len(flagged))

    final: list[SignalRecord] = []
    for d in deduplicated:
        try:
            d.pop("quote_embedding", None)
            d.pop("merged_from", None)
            final.append(SignalRecord(**d))
        except Exception as exc:
            logger.error("Failed to re-create SignalRecord: %s", exc)

    return {"final_signals": final}


def logging_node(state: PipelineState) -> dict:
    """Write all final signals to the append-only decision log."""
    signals = state.get("final_signals", [])
    for signal in signals:
        try:
            log_signal(signal)
        except Exception as exc:
            logger.error("Failed to log signal: %s", exc)

    ticker = state.get("ticker")
    if ticker:
        try:
            from ecis.db.ticker_registry import mark_extraction

            mark_extraction(ticker, "complete" if signals else "empty")
        except Exception as exc:
            logger.debug("Ticker registry update failed: %s", exc)

    logger.info("Pipeline complete: %d signals logged for %s", len(signals), ticker)
    return {}


def build_pipeline_graph() -> StateGraph:
    """Build and return the top-level extraction pipeline graph."""
    graph = StateGraph(PipelineState)

    graph.add_node("ingestion", ingestion_node)
    graph.add_node("chunking", chunking_node)
    graph.add_node("fast_pass", fast_pass_node)
    graph.add_node("escalation", escalation_node)
    graph.add_node("llm_extraction", llm_extraction_node)
    graph.add_node("conflict_resolution", conflict_resolution_node)
    graph.add_node("ner", ner_node)
    graph.add_node("triangulation", triangulation_node)
    graph.add_node("deduplication", deduplication_node)
    graph.add_node("logging", logging_node)

    graph.set_entry_point("ingestion")
    graph.add_edge("ingestion", "chunking")
    graph.add_edge("chunking", "fast_pass")
    graph.add_edge("fast_pass", "escalation")
    graph.add_edge("escalation", "llm_extraction")
    graph.add_edge("llm_extraction", "conflict_resolution")
    graph.add_edge("conflict_resolution", "ner")
    graph.add_edge("ner", "triangulation")
    graph.add_edge("triangulation", "deduplication")
    graph.add_edge("deduplication", "logging")
    graph.add_edge("logging", END)

    return graph


def compile_pipeline(**kwargs):
    graph = build_pipeline_graph()
    return graph.compile(**kwargs)


def _default_checkpointer():
    try:
        import sqlite3

        from langgraph.checkpoint.sqlite import SqliteSaver

        path = settings.db_dir / "langgraph_checkpoints.db"
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(path), check_same_thread=False)
        return SqliteSaver(conn)
    except Exception as exc:
        logger.debug("LangGraph checkpointer unavailable: %s", exc)
        return None


def run_pipeline(
    ticker: str,
    transcript_path: str,
    *,
    checkpointer=None,
    llm_model: str | None = None,
) -> list[SignalRecord]:
    compile_kwargs = {}
    saver = checkpointer if checkpointer is not None else _default_checkpointer()
    if saver:
        compile_kwargs["checkpointer"] = saver

    app = compile_pipeline(**compile_kwargs)
    model = llm_model or settings.llm_model

    initial_state: PipelineState = {
        "ticker": ticker,
        "transcript_path": transcript_path,
        "transcript_text": "",
        "chunks": [],
        "fast_pass_results": [],
        "category_a_indices": [],
        "category_b_indices": [],
        "category_c_indices": [],
        "category_d_indices": [],
        "keyword_signals": [],
        "finbert_signals": [],
        "ner_results": [],
        "llm_signals": [],
        "conflict_resolutions": [],
        "triangulated_signals": [],
        "final_signals": [],
        "current_chunk_index": 0,
        "errors": [],
        "llm_model": model,
        "chunk_models": {},
        "rejected_chunks": [],
    }

    config = {"configurable": {"thread_id": f"{ticker}_{transcript_path}"}}
    final_state = app.invoke(initial_state, config=config)
    return final_state.get("final_signals", [])
