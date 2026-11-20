"""Pronoun coreference for Q&A."""

from __future__ import annotations

import os
import re
from typing import Any

from ecis.analytics.features import quarter_key
from ecis.guidance_models.qa_parser import parse_qa_corpus

_LOAD = os.getenv("FORECASTING_LOAD_COREF", "").lower() in {"1", "true", "yes"}
_PRONOUN = re.compile(r"^(it|they|them|that|this)$", re.I)
_NOUN = re.compile(
    r"^(?:the|our|this|that)?(guidance|outlook|initiative|program|product|margin|"
    r"revenue|forecast|expansion)$",
    re.I,
)


def resolve_text(text: str) -> tuple[str, list[dict[str, str]]]:
    blob = text or ""
    spans: list[dict[str, str]] = []
    last = ""
    out_parts: list[str] = []
    for match in re.finditer(r"\S+|\s+", blob):
        token = match.group(0)
        stripped = token.strip(".,;:?")
        noun = _NOUN.match(stripped)
        if noun:
            last = noun.group(1)
            out_parts.append(token)
        elif last and _PRONOUN.match(stripped):
            spans.append({"pronoun": stripped, "referent": last})
            out_parts.append(last)
        else:
            out_parts.append(token)
    return "".join(out_parts), spans


def resolve_pairs(ticker: str | None = None, pairs: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    if _LOAD:
        try:
            import coreferee  # type: ignore
        except Exception:
            coreferee = None
        else:
            _ = coreferee

    rows = pairs if pairs is not None else parse_qa_corpus(ticker)
    out: list[dict[str, Any]] = []
    for row in rows:
        q_res, q_spans = resolve_text(row.get("question") or "")
        a_res, a_spans = resolve_text(row.get("answer") or "")
        for span in q_spans + a_spans:
            out.append({
                "ticker": (row.get("ticker") or "").upper(),
                "transcript_date": (row.get("transcript_date") or "")[:10],
                "quarter": quarter_key(row.get("transcript_date")),
                "pair_index": row.get("pair_index"),
                "pronoun": span["pronoun"],
                "referent": span["referent"],
                "resolved_question": q_res,
                "resolved_answer": a_res,
                "method": "rule",
            })
        if not q_spans and not a_spans:
            out.append({
                "ticker": (row.get("ticker") or "").upper(),
                "transcript_date": (row.get("transcript_date") or "")[:10],
                "quarter": quarter_key(row.get("transcript_date")),
                "pair_index": row.get("pair_index"),
                "pronoun": None,
                "referent": None,
                "resolved_question": q_res,
                "resolved_answer": a_res,
                "method": "rule",
            })
    return out
