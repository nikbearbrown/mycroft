"""Offensive / defensive competitive language: lexicon, zero-shot fallback, stance ensemble."""

from __future__ import annotations

import os
from collections import defaultdict
from typing import Any

from ecis.guidance_models.finbert_ensemble import ensemble_polarity, lexicon_polarity
from ecis.guidance_models.qa_parser import iter_normalised_transcripts
from ecis.analytics.features import quarter_key
from ecis.db.init_db import get_connection

_LOAD_ZEROSHOT = os.getenv("GUIDANCE_LOAD_ZEROSHOT", "").lower() in {"1", "true", "yes"}
_ZEROSHOT_MODEL = os.getenv("ZEROSHOT_MODEL", "facebook/bart-large-mnli")

OFFENSIVE = (
    "gaining share", "gain share", "expanding into", "capturing", "growing faster than",
    "taking market", "take share", "outgrowing", "winning share", "share gains",
)
DEFENSIVE = (
    "maintaining position", "protecting margins", "defending", "holding steady",
    "retaining", "defend share", "hold share", "protect share", "maintain share",
)

_LABELS = ("offensive", "defensive", "neutral")


def _count_hits(text: str, phrases: tuple[str, ...]) -> list[str]:
    blob = (text or "").lower()
    return [p for p in phrases if p in blob]


def lexicon_score(text: str) -> dict[str, Any]:
    off = _count_hits(text, OFFENSIVE)
    deff = _count_hits(text, DEFENSIVE)
    polarity = lexicon_polarity(text)
    raw = (len(off) - len(deff))
    # FinBERT-style context: polarity can flip a lone ambiguous hit.
    if off and not deff and polarity < -0.25:
        raw -= 0.5
    if deff and not off and polarity > 0.25:
        raw += 0.5
    denom = len(off) + len(deff) + 1
    score = max(-1.0, min(1.0, raw / denom))
    label = "offensive" if score > 0.15 else "defensive" if score < -0.15 else "neutral"
    return {
        "score": score,
        "label": label,
        "offensive_phrases": off,
        "defensive_phrases": deff,
        "method": "lexicon",
    }


def zeroshot_score(text: str) -> dict[str, Any]:
    """BART-MNLI when GUIDANCE_LOAD_ZEROSHOT=1, else a lexicon-shaped fallback."""
    if _LOAD_ZEROSHOT and text:
        try:
            from transformers import pipeline

            clf = pipeline("zero-shot-classification", model=_ZEROSHOT_MODEL)
            out = clf(text[:800], candidate_labels=list(_LABELS))
            labels = list(out["labels"])
            scores = list(out["scores"])
            dist = {l: float(s) for l, s in zip(labels, scores)}
            for lab in _LABELS:
                dist.setdefault(lab, 0.0)
            score = dist["offensive"] - dist["defensive"]
            label = max(_LABELS, key=lambda k: dist[k])
            return {"score": score, "label": label, "method": "bart-mnli", "distribution": dist}
        except Exception:
            pass
    base = lexicon_score(text)
    base["method"] = "zeroshot_fallback"
    return base


def stance_score(text: str) -> dict[str, Any]:
    """Financial stance: lexicon direction mixed with ensemble polarity."""
    lex = lexicon_score(text)
    ens = ensemble_polarity(text)
    score = 0.65 * lex["score"] + 0.35 * ens["polarity"]
    label = "offensive" if score > 0.15 else "defensive" if score < -0.15 else "neutral"
    return {"score": score, "label": label, "method": "stance", "polarity": ens["polarity"]}


def ensemble_market_share(text: str) -> dict[str, Any]:
    lex = lexicon_score(text)
    zero = zeroshot_score(text)
    stance = stance_score(text)
    score = (lex["score"] + zero["score"] + stance["score"]) / 3.0
    label = "offensive" if score > 0.15 else "defensive" if score < -0.15 else "neutral"
    agree = sum(1 for r in (lex, zero, stance) if r["label"] == label)
    phrases = sorted(set(lex.get("offensive_phrases") or []) | set(lex.get("defensive_phrases") or []))
    return {
        "score": score,
        "label": label,
        "lexicon_score": lex["score"],
        "zeroshot_score": zero["score"],
        "stance_score": stance["score"],
        "agreement": agree / 3.0,
        "phrases": phrases,
    }


def _call_texts(ticker: str | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    files = iter_normalised_transcripts(ticker)
    if files:
        for tkr, day, path in files:
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            rows.append({"ticker": tkr, "transcript_date": day, "text": text})
        return rows
    conn = get_connection("signals")
    query = "SELECT ticker, transcript_date, supporting_quote FROM signals"
    params: list[str] = []
    if ticker:
        query += " WHERE ticker = ?"
        params.append(ticker.upper())
    buckets: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in conn.execute(query, params).fetchall():
        buckets[((row["ticker"] or "").upper(), (row["transcript_date"] or "")[:10])].append(row["supporting_quote"] or "")
    conn.close()
    for (tkr, day), quotes in buckets.items():
        rows.append({"ticker": tkr, "transcript_date": day, "text": " ".join(quotes)})
    return rows


def score_calls(ticker: str | None = None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in _call_texts(ticker):
        ens = ensemble_market_share(row["text"])
        out.append({
            "ticker": row["ticker"],
            "transcript_date": row["transcript_date"],
            "quarter": quarter_key(row["transcript_date"]),
            **ens,
        })
    return out


def track_shifts(ticker: str | None = None) -> list[dict[str, Any]]:
    calls = sorted(score_calls(ticker), key=lambda r: (r["ticker"], r["quarter"], r["transcript_date"]))
    by_tkr: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in calls:
        by_tkr[row["ticker"]].append(row)
    out: list[dict[str, Any]] = []
    for tkr, items in by_tkr.items():
        prev = None
        for row in items:
            change = None
            flag = "stable"
            if prev is not None:
                change = row["score"] - prev["score"]
                flipped = row["label"] != prev["label"] and row["label"] != "neutral" and prev["label"] != "neutral"
                if flipped:
                    flag = "flip"
                elif change is not None and abs(change) >= 0.25:
                    flag = "drift"
            out.append({
                "ticker": tkr,
                "quarter": row["quarter"],
                "transcript_date": row["transcript_date"],
                "score": row["score"],
                "label": row["label"],
                "prior_label": None if prev is None else prev["label"],
                "score_change": change,
                "flag": flag,
                "phrases": row.get("phrases") or [],
                "agreement": row.get("agreement"),
            })
            prev = row
    return out
