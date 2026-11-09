"""Per-pair and per-call dodge scores, weighted by question type."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ecis.guidance_models.qa_parser import parse_qa, parse_qa_corpus
from ecis.guidance_models.question_types import classify_question, question_weight
from ecis.guidance_models.reranker import relevance_score
from ecis.analytics.features import quarter_key
from ecis.analytics.stats import mean, stdev

_EVASION = (
    "as i said", "as we said", "we already", "not going to get into",
    "won't speculate", "hard to say", "too early", "we'll get back",
    "i don't want to", "can't comment", "no additional", "as i mentioned",
    "i'd rather not", "beyond what we",
)


def evasion_ratio(answer: str) -> float:
    text = (answer or "").lower()
    if not text.strip():
        return 1.0
    hits = sum(1 for p in _EVASION if p in text)
    tokens = max(len(text.split()), 1)
    return max(0.0, min(1.0, hits / max(tokens / 20.0, 1.0)))


def score_pair(pair: dict[str, Any]) -> dict[str, Any]:
    qtype = classify_question(pair.get("question") or "")
    relevance, method = relevance_score(pair.get("question") or "", pair.get("answer") or "")
    evade = evasion_ratio(pair.get("answer") or "")
    weight = question_weight(qtype)
    dodge = (1.0 - relevance) * weight * (0.45 + 0.55 * evade)
    if not (pair.get("answer") or "").strip():
        dodge = weight
    out = dict(pair)
    out.update({
        "question_type": qtype,
        "type_weight": weight,
        "relevance": relevance,
        "relevance_method": method,
        "evasion": evade,
        "dodge": max(0.0, min(1.0, dodge)),
    })
    return out


def score_pairs(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [score_pair(p) for p in pairs]


def aggregate_dodge(pairs: list[dict[str, Any]] | None = None, ticker: str | None = None) -> list[dict[str, Any]]:
    """Call-level and speaker-level dodge snapshots with historical spike flags."""
    if pairs is None:
        pairs = score_pairs(parse_qa_corpus(ticker))
    else:
        pairs = score_pairs(pairs)

    by_call: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    by_speaker: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    hist: dict[str, list[float]] = defaultdict(list)

    for row in pairs:
        tkr = (row.get("ticker") or "").upper()
        day = (row.get("transcript_date") or "")[:10]
        by_call[(tkr, day)].append(row)
        role = row.get("answer_role") or "unknown"
        by_speaker[(tkr, day, role)].append(row)

    call_rows: list[dict[str, Any]] = []
    for (tkr, day), items in sorted(by_call.items()):
        overall = mean([r["dodge"] for r in items])
        hist[tkr].append(overall if overall is not None else 0.0)
        types: dict[str, list[float]] = defaultdict(list)
        for r in items:
            types[r["question_type"]].append(r["dodge"])
        call_rows.append({
            "ticker": tkr,
            "transcript_date": day,
            "quarter": quarter_key(day),
            "scope": "call",
            "speaker_role": "",
            "n_pairs": len(items),
            "dodge": overall,
            "forward_looking": mean(types.get("forward-looking") or []),
            "backward_looking": mean(types.get("backward-looking") or []),
            "clarification": mean(types.get("clarification") or []),
            "confrontational": mean(types.get("confrontational") or []),
            "flag": "normal",
        })

    for row in call_rows:
        series = hist.get(row["ticker"]) or []
        mu = mean(series)
        sd = stdev(series)
        spiked = row["dodge"] is not None and mu is not None and row["dodge"] > mu + (sd or 0.15)
        row["flag"] = "spike" if spiked else "normal"
        row["historical_mean"] = mu

    speaker_rows: list[dict[str, Any]] = []
    for (tkr, day, role), items in sorted(by_speaker.items()):
        speaker_rows.append({
            "ticker": tkr,
            "transcript_date": day,
            "quarter": quarter_key(day),
            "scope": "speaker",
            "speaker_role": role,
            "n_pairs": len(items),
            "dodge": mean([r["dodge"] for r in items]),
            "forward_looking": None,
            "backward_looking": None,
            "clarification": None,
            "confrontational": None,
            "flag": "normal",
            "historical_mean": None,
        })
    return call_rows + speaker_rows


def score_text(text: str, *, ticker: str = "", transcript_date: str = "") -> list[dict[str, Any]]:
    return aggregate_dodge(parse_qa(text, ticker=ticker, transcript_date=transcript_date))
