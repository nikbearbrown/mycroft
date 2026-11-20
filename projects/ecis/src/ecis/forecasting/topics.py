"""Topic mix per ticker-quarter. """

from __future__ import annotations

import math
import os
import re
from collections import Counter, defaultdict
from typing import Any

from ecis.analytics.features import quarter_key
from ecis.db.init_db import get_connection
from ecis.db.ticker_registry import get_ticker
from ecis.guidance_models.qa_parser import parse_qa_corpus

_LOAD = os.getenv("FORECASTING_LOAD_BERTOPIC", "").lower() in {"1", "true", "yes"}
_TOKEN = re.compile(r"[a-z]{3,}")
_STOP = {
    "the", "and", "for", "that", "this", "with", "from", "have", "will",
    "our", "you", "are", "was", "were", "not", "but", "about", "into",
}
N_TOPICS = 6


def _tokens(text: str) -> list[str]:
    return [t for t in _TOKEN.findall((text or "").lower()) if t not in _STOP]


def _docs(ticker: str | None = None) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, str], list[str]] = defaultdict(list)
    try:
        conn = get_connection("signals")
        query = "SELECT ticker, transcript_date, supporting_quote FROM signals"
        params: list[str] = []
        if ticker:
            query += " WHERE ticker = ?"
            params.append(ticker.upper())
        for row in conn.execute(query, params).fetchall():
            q = quarter_key(row["transcript_date"])
            buckets[((row["ticker"] or "").upper(), q)].append(row["supporting_quote"] or "")
        conn.close()
    except Exception:
        pass
    for pair in parse_qa_corpus(ticker):
        tkr = (pair.get("ticker") or "").upper()
        q = quarter_key(pair.get("transcript_date"))
        buckets[(tkr, q)].append((pair.get("question") or "") + " " + (pair.get("answer") or ""))
    return [{"ticker": tkr, "quarter": q, "text": " ".join(parts)} for (tkr, q), parts in sorted(buckets.items())]


def _kmeans(vectors: list[list[float]], k: int, rounds: int = 8) -> list[int]:
    if not vectors:
        return []
    k = max(1, min(k, len(vectors)))
    cents = [vectors[i * max(len(vectors) // k, 1) % len(vectors)][:] for i in range(k)]
    assign = [0] * len(vectors)
    for _ in range(rounds):
        for i, vec in enumerate(vectors):
            best, best_d = 0, None
            for j, c in enumerate(cents):
                d = sum((a - b) ** 2 for a, b in zip(vec, c))
                if best_d is None or d < best_d:
                    best, best_d = j, d
            assign[i] = best
        for j in range(k):
            members = [vectors[i] for i, a in enumerate(assign) if a == j]
            if not members:
                continue
            dim = len(members[0])
            cents[j] = [sum(m[d] for m in members) / len(members) for d in range(dim)]
    return assign


def _ctfidf(docs: list[list[str]], assign: list[int], k: int) -> list[str]:
    labels = []
    df = Counter()
    for toks in docs:
        df.update(set(toks))
    a = max(sum(len(t) for t in docs), 1)
    for j in range(k):
        tf = Counter()
        for toks, lab in zip(docs, assign):
            if lab == j:
                tf.update(toks)
        scored = []
        for word, c in tf.items():
            scored.append((c * math.log(1 + a / max(df[word], 1)), word))
        scored.sort(reverse=True)
        labels.append(" ".join(w for _, w in scored[:3]) or f"topic-{j}")
    return labels


def fit_topics(ticker: str | None = None) -> list[dict[str, Any]]:
    if _LOAD:
        try:
            from bertopic import BERTopic  # type: ignore
        except Exception:
            BERTopic = None
        else:
            _ = BERTopic

    records = _docs(ticker)
    tokenized = [_tokens(r["text"]) for r in records]
    vocab = []
    seen = set()
    for toks in tokenized:
        for t in toks:
            if t not in seen:
                seen.add(t)
                vocab.append(t)
            if len(vocab) >= 40:
                break
        if len(vocab) >= 40:
            break
    if not vocab:
        return []
    index = {w: i for i, w in enumerate(vocab)}
    vectors = []
    for toks in tokenized:
        vec = [0.0] * len(vocab)
        for t in toks:
            if t in index:
                vec[index[t]] += 1.0
        n = math.sqrt(sum(x * x for x in vec)) or 1.0
        vectors.append([x / n for x in vec])
    k = min(N_TOPICS, max(1, len(vectors)))
    assign = _kmeans(vectors, k)
    labels = _ctfidf(tokenized, assign, k)
    counts = Counter(assign)
    out: list[dict[str, Any]] = []
    for rec, lab in zip(records, assign):
        sector = "AI"
        try:
            info = get_ticker(rec["ticker"])
            if info:
                sector = info.get("sector") or "AI"
        except Exception:
            pass
        dist = [0.0] * k
        dist[lab] = 1.0
        # soft mix: share of tokens overlapping each cluster's label words
        for j, name in enumerate(labels):
            words = set(name.split())
            toks = set(_tokens(rec["text"]))
            dist[j] = len(words & toks) / max(len(words), 1)
        s = sum(dist) or 1.0
        dist = [d / s for d in dist]
        for j, weight in enumerate(dist):
            if weight <= 0:
                continue
            out.append({
                "ticker": rec["ticker"],
                "quarter": rec["quarter"],
                "sector": sector,
                "topic_id": j,
                "topic_label": labels[j],
                "weight": weight,
                "n_docs": counts[j],
                "method": "ctfidf-kmeans",
            })
    return out
