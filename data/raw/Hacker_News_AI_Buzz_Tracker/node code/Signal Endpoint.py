# n8n code node: Signal Endpoint  (Week 11 — /webhook/signal transform, schema 1.1)
# Sits between the Postgres read and the Respond to Webhook node. Turns the latest
# complete run row into the schema-1.1 JSON contract (docs/json_signal_contract.md).
#
# 1.1 is ADDITIVE over 1.0: same top-level + entity fields, plus per-entity
# `narrative` (theme/tone) and structured `community_opinion` (no free text), plus
# a top-level `sector` block. Consumers pinned on 1.0 ignore the new fields.
#
# Data source: the persisted `leaderboard` jsonb already carries each entity's
# `narrative` and `communityOpinion` (they're attached before Save Snapshot), so
# the endpoint query does NOT strictly need extra columns. As a fallback it will
# also read top-level `narratives` / `community_opinions` maps if the query selects
# them. The sector block reads `sectorNarrative`/`sector_narrative` if present,
# else emits a well-formed degraded sector.
#
# Suggested query:
#   SELECT run_date, window_hours, complete, watchlist_version,
#          leaderboard, narratives, community_opinions
#   FROM hn_buzz_runs
#   WHERE complete = true AND watchlist_version = 'v1'
#   ORDER BY created_at DESC LIMIT 1;
import json


def _as_list(v):
    if isinstance(v, str):
        try:
            v = json.loads(v)
        except Exception:
            v = []
    return v or []


def _as_map(v):
    if isinstance(v, str):
        try:
            v = json.loads(v)
        except Exception:
            v = {}
    return v or {}


def _narrative_out(n):
    n = n or {}
    return {"theme": n.get("theme"), "tone": n.get("tone")}


def _opinion_out(op):
    op = op or {}
    return {
        "sentiment": op.get("sentiment"),
        "themes": op.get("themes") or [],
        "comments_analyzed": op.get("commentsAnalyzed", 0),
        "low_confidence": op.get("lowConfidence", False),
        "degraded": op.get("degraded", False),
    }


def _sector_out(row):
    sec = row.get("sectorNarrative") or row.get("sector_narrative")
    sec = _as_map(sec)
    if not sec:
        return {"narrative": None, "cross_entity_themes": [], "degraded": True}
    return {
        "narrative": sec.get("narrative"),
        "cross_entity_themes": sec.get("crossEntityThemes") or [],
        "degraded": sec.get("degraded", False),
    }


def func(_items):
    row = _items[0]["json"] if (_items and _items[0].get("json")) else {}

    lb = _as_list(row.get("leaderboard"))
    narratives = _as_map(row.get("narratives"))            # fallback maps (optional)
    opinions = _as_map(row.get("community_opinions"))

    entities = []
    for e in lb:
        ent = e.get("entity")
        narrative = e.get("narrative") or narratives.get(ent)
        opinion = e.get("communityOpinion") or opinions.get(ent)
        entities.append({
            "entity": ent,
            "ticker": e.get("ticker"),
            "buzz_score": e.get("buzzScore"),
            "velocity": e.get("velocity", 0),
            "breakout": e.get("breakout", False),
            "low_confidence": e.get("lowConfidence", False),
            "cold_start": e.get("coldStart", False),
            "narrative": _narrative_out(narrative),
            "community_opinion": _opinion_out(opinion),
        })

    signal = {
        "source": "hacker_news_buzz",
        "schema_version": "1.1",
        "run_date": row.get("run_date"),
        "window_hours": row.get("window_hours", 24),
        "watchlist_version": row.get("watchlist_version", "v1"),
        "complete": bool(row.get("complete")) if lb else False,
        "entities": entities,
        "sector": _sector_out(row),
    }
    return [{"json": signal}]


return func(_items)
