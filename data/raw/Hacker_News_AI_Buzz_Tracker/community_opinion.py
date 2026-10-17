# =============================================================================
# Week 9 deliverable — Community Opinion analyzer (comment-text LLM).
#
# This is a DISTINCT layer from Weeks 2-4 (deterministic Buzz Score, "how much
# attention") and Week 7 (title-level narrative/theme/tone, "what the headlines
# are about"). This layer is grounded in what commenters actually WROTE: it
# fetches top-level HN comment text for an entity's top stories and asks the
# LLM for a comment-grounded opinion summary, sentiment label, recurring
# themes, and a few notable verbatim quotes.
#
# Pipeline (per entity):
#   1. fetch_top_stories()      — reuse llm_narrative's Algolia lookup, top 3 by points.
#   2. fetch_comments_for_story() — HN Firebase item API: story.kids -> comment items.
#   3. clean_comment()          — strip HTML tags, decode entities, truncate, drop dead/deleted.
#   4. generate_community_opinion() — LLM call, degrade to null on no comments / no key / failure.
#   5. cluster_sector_themes()  — cross-entity theme clustering into one sector narrative.
#
# Use as a library:  from community_opinion import generate_community_opinion
# Use from the CLI:   python community_opinion.py --entity OpenAI      (fetches live HN)
#                      python community_opinion.py --demo               (offline fixture)
#                      python community_opinion.py --sector --demo      (sector clustering demo)
# Needs GROQ_API_KEY (or ANTHROPIC_API_KEY for --provider claude) in .env.
# See docs/community_opinion_design.md for the comment-fetch strategy and token budget.
# =============================================================================

import argparse
import html
import json
import os
import re
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

from llm_narrative import fetch_top_stories as _fetch_top_stories_ranked

load_dotenv()

# --- Controlled vocabulary (plan.md "Signals produced") ----------------------
SENTIMENTS = ["positive", "negative", "mixed", "neutral"]

# --- Provider / model config (overridable via env, same defaults as Week 7) --
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-3-5-haiku-latest")
ANTHROPIC_VERSION = "2023-06-01"

HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"

# Bounds from plan.md: "Cap at the top 3 stories x top ~10 comments = ~30
# comments per entity to bound API calls and token use."
TOP_N_STORIES = 3
TOP_N_COMMENTS_PER_STORY = 10
MAX_COMMENT_CHARS = 500

WATCHLIST_PATH = Path(__file__).parent / "watchlist.json"


# --- Comment fetch (HN Firebase item API) ------------------------------------
def fetch_item(item_id, timeout=15):
    """One HN Firebase item (story or comment). Returns None on any failure —
    a single missing/deleted item must never fail the whole entity fetch."""
    try:
        resp = requests.get(HN_ITEM_URL.format(id=item_id), timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def fetch_comments_for_story(story_id, top_n=TOP_N_COMMENTS_PER_STORY):
    """Fetch up to top_n top-level comments (by kids order, which Firebase
    returns newest/most-relevant-first) for one story. Skips missing, deleted,
    and dead comments; does not recurse into replies (plan.md scope: top N
    top-level comments only)."""
    story = fetch_item(story_id)
    if not story or not story.get("kids"):
        return []
    comments = []
    for kid_id in story["kids"][: top_n * 2]:  # fetch a few extra to absorb dead/deleted
        if len(comments) >= top_n:
            break
        item = fetch_item(kid_id)
        if not item:
            continue
        if item.get("deleted") or item.get("dead"):
            continue
        text = item.get("text")
        if not text:
            continue
        comments.append(text)
    return comments[:top_n]


_TAG_RE = re.compile(r"<[^>]+>")


def clean_comment(raw_text):
    """Strip HTML tags, decode HTML entities, collapse whitespace, truncate.
    HN comment `text` is HTML (e.g. <p>, <i>, &#x27;, &gt;) — this is the
    Code-node cleaning step from plan.md's Week 9 spec."""
    if not raw_text:
        return None
    text = _TAG_RE.sub(" ", raw_text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return None
    return text[:MAX_COMMENT_CHARS]


def clean_and_dedupe(raw_comments):
    """Clean a list of raw comment texts; drop empties; dedupe exact repeats
    (some HN threads have copy-pasted boilerplate replies)."""
    seen = set()
    cleaned = []
    for raw in raw_comments:
        c = clean_comment(raw)
        if not c or c in seen:
            continue
        seen.add(c)
        cleaned.append(c)
    return cleaned


def fetch_entity_comments(top_stories, top_n_stories=TOP_N_STORIES,
                           top_n_comments=TOP_N_COMMENTS_PER_STORY):
    """Top-level entry: given an entity's ranked stories (objectID present),
    fetch + clean comments across its top N stories. Returns (comments, meta)
    where meta records story/comment counts analyzed (plan.md: persist counts)."""
    stories = [s for s in top_stories if s.get("objectID")][:top_n_stories]
    all_raw = []
    stories_with_comments = 0
    for s in stories:
        raw = fetch_comments_for_story(s["objectID"], top_n_comments)
        if raw:
            stories_with_comments += 1
        all_raw.extend(raw)
    cleaned = clean_and_dedupe(all_raw)
    meta = {
        "storiesAnalyzed": stories_with_comments,
        "commentsAnalyzed": len(cleaned),
    }
    return cleaned, meta


# --- Prompt --------------------------------------------------------------
def build_messages(entity, ticker, comments):
    lines = [f"{i}. {c}" for i, c in enumerate(comments, 1)]
    comments_block = "\n".join(lines) if lines else "(no comments)"

    system = (
        "You are a technical-community analyst for an AI-sector attention tracker. "
        "You read verbatim Hacker News comment text about one entity and summarize "
        "the community's OPINION, grounded only in what commenters actually wrote. "
        "This is distinct from headline-level narrative: it reflects discussion "
        "content, not just story titles. Never invent a fact, quote, or event not "
        "present in the comments given. Reply with a single JSON object only."
    )
    user = (
        f"Entity: {entity}" + (f" (ticker {ticker})" if ticker else "") + "\n"
        f"Top-level Hacker News comments on this entity's top stories this window:\n"
        f"{comments_block}\n\n"
        "Return JSON with exactly these keys:\n"
        '  "summary": 2-3 sentences, plain English, grounded in the comments above.\n'
        f'  "sentiment": overall community sentiment, one of {SENTIMENTS}.\n'
        '  "themes": a short list (<=5) of recurring topics/concerns raised.\n'
        '  "notableOpinions": a list (<=3) of short VERBATIM excerpts from the comments '
        "above that best represent the discussion (quote them exactly, do not paraphrase).\n"
        "If the comments are too sparse to judge, use \"mixed\" or \"neutral\" and keep "
        "the summary appropriately hedged."
    )
    return system, user


def build_sector_messages(entity_opinions):
    """Cluster per-entity Community Opinion summaries into one cross-entity
    sector narrative of the week (plan.md: "Cluster cross entity themes into
    a sector narrative of the week from the per-entity opinions")."""
    lines = []
    for op in entity_opinions:
        if not op or op.get("degraded") or not op.get("summary"):
            continue
        themes = ", ".join(op.get("themes") or [])
        lines.append(f"- {op['entity']}: [{op.get('sentiment')}] {op['summary']} (themes: {themes})")
    entities_block = "\n".join(lines) if lines else "(no non-degraded entity opinions this run)"

    system = (
        "You are a technical-community analyst summarizing this week's AI-sector "
        "discussion across multiple tracked entities. Ground every statement in "
        "the per-entity summaries given; never invent facts about entities not "
        "listed. Reply with a single JSON object only."
    )
    user = (
        f"Per-entity Community Opinion summaries this window:\n{entities_block}\n\n"
        "Return JSON with exactly these keys:\n"
        '  "sectorNarrative": 2-4 sentences describing the shared/cross-cutting themes '
        "and overall mood of this week's AI-sector discussion.\n"
        '  "crossEntityThemes": a short list (<=6) of themes that recur across more than '
        "one entity."
    )
    return system, user


# --- Provider calls (same shape as llm_narrative.py) --------------------------
def call_groq(system, user, model, api_key):
    body = {
        "model": model,
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
    }
    resp = requests.post(GROQ_URL, headers={"Authorization": f"Bearer {api_key}"},
                         json=body, timeout=45)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def call_claude(system, user, model, api_key):
    body = {
        "model": model,
        "max_tokens": 500,
        "temperature": 0.3,
        "system": system + " Output only the JSON object, no prose before or after.",
        "messages": [{"role": "user", "content": user}],
    }
    resp = requests.post(ANTHROPIC_URL, json=body, timeout=45, headers={
        "x-api-key": api_key, "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json"})
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def _call_provider(system, user, provider, model, groq_key, claude_key):
    if provider == "groq":
        if not groq_key:
            raise RuntimeError("GROQ_API_KEY not set")
        return call_groq(system, user, model or GROQ_MODEL, groq_key), (model or GROQ_MODEL)
    if provider == "claude":
        if not claude_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        return call_claude(system, user, model or CLAUDE_MODEL, claude_key), (model or CLAUDE_MODEL)
    raise RuntimeError(f"unknown provider '{provider}'")


# --- Parse + validate ---------------------------------------------------------
def _extract_json_object(text):
    text = text.strip()
    if text.startswith("{"):
        return text
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in model output")
    return text[start:end + 1]


def _coerce_enum(value, allowed, fallback):
    if isinstance(value, str):
        v = value.strip().lower()
        if v in allowed:
            return v, False
    return fallback, True


def parse_and_validate(raw_text):
    obj = json.loads(_extract_json_object(raw_text))
    summary = (obj.get("summary") or "").strip()
    if not summary:
        raise ValueError("model returned empty summary")
    sentiment, coerced = _coerce_enum(obj.get("sentiment"), SENTIMENTS, "neutral")
    themes = obj.get("themes") or []
    if not isinstance(themes, list):
        themes = []
    notable = obj.get("notableOpinions") or []
    if not isinstance(notable, list):
        notable = []
    return {
        "summary": summary,
        "sentiment": sentiment,
        "themes": [str(t) for t in themes][:5],
        "notableOpinions": [str(q) for q in notable][:3],
        "enumCoerced": bool(coerced),
    }


def parse_sector_response(raw_text):
    obj = json.loads(_extract_json_object(raw_text))
    narrative = (obj.get("sectorNarrative") or "").strip()
    if not narrative:
        raise ValueError("model returned empty sectorNarrative")
    themes = obj.get("crossEntityThemes") or []
    if not isinstance(themes, list):
        themes = []
    return {"sectorNarrative": narrative, "crossEntityThemes": [str(t) for t in themes][:6]}


# --- Public entry points -------------------------------------------------------
def generate_community_opinion(entity, top_stories, ticker=None, provider=None, model=None):
    """Return {summary, sentiment, themes, notableOpinions, storiesAnalyzed,
    commentsAnalyzed, ...} for one entity, or a DEGRADED record (summary=None)
    on zero comments, no key, or any failure. Never raises — the deterministic
    score, narrative, and digest must ship even when this layer is unavailable."""
    groq_key = os.environ.get("GROQ_API_KEY")
    claude_key = os.environ.get("ANTHROPIC_API_KEY")

    comments, meta = fetch_entity_comments(top_stories or [])
    if not comments:
        return _degraded("no comments available for this entity's top stories",
                          provider="none", meta=meta)

    if provider is None:
        provider = "groq" if groq_key else ("claude" if claude_key else None)
    if provider is None:
        return _degraded("no LLM key set (GROQ_API_KEY / ANTHROPIC_API_KEY)",
                          provider="none", meta=meta)

    system, user = build_messages(entity, ticker, comments)
    try:
        raw, used_model = _call_provider(system, user, provider, model, groq_key, claude_key)
        parsed = parse_and_validate(raw)
    except Exception as exc:  # noqa: BLE001 — degrade on ANY failure, never crash the run
        return _degraded(f"{type(exc).__name__}: {exc}", provider=provider, meta=meta)

    parsed.update({
        "entity": entity, "ticker": ticker, "provider": provider, "model": used_model,
        "degraded": False, **meta,
    })
    return parsed


def cluster_sector_themes(entity_opinions, provider=None, model=None):
    """Cross-entity clustering into one sector narrative of the week. Degrades
    to null if no LLM key or no usable (non-degraded) entity opinions exist."""
    groq_key = os.environ.get("GROQ_API_KEY")
    claude_key = os.environ.get("ANTHROPIC_API_KEY")
    usable = [op for op in (entity_opinions or []) if op and not op.get("degraded")]
    if not usable:
        return _degraded_sector("no non-degraded entity opinions this run", provider="none")

    if provider is None:
        provider = "groq" if groq_key else ("claude" if claude_key else None)
    if provider is None:
        return _degraded_sector("no LLM key set (GROQ_API_KEY / ANTHROPIC_API_KEY)", provider="none")

    system, user = build_sector_messages(usable)
    try:
        raw, used_model = _call_provider(system, user, provider, model, groq_key, claude_key)
        parsed = parse_sector_response(raw)
    except Exception as exc:  # noqa: BLE001
        return _degraded_sector(f"{type(exc).__name__}: {exc}", provider=provider)

    parsed.update({"provider": provider, "model": used_model, "degraded": False,
                    "entitiesClustered": len(usable)})
    return parsed


def _degraded(reason, provider, meta=None):
    base = {"entity": None, "ticker": None, "summary": None, "sentiment": None,
            "themes": [], "notableOpinions": [], "enumCoerced": False,
            "provider": provider, "model": None, "degraded": True, "reason": reason,
            "storiesAnalyzed": 0, "commentsAnalyzed": 0}
    if meta:
        base.update(meta)
    return base


def _degraded_sector(reason, provider):
    return {"sectorNarrative": None, "crossEntityThemes": [], "provider": provider,
            "model": None, "degraded": True, "reason": reason, "entitiesClustered": 0}


# --- CLI helpers ---------------------------------------------------------------
DEMO_COMMENTS = [  # offline fixture so the module is testable with no network
    "<p>GPT-5's reasoning benchmarks are impressive but the pricing jump is going to hurt "
    "smaller teams. We&#x27;re re-evaluating our stack.",
    "<i>Honestly</i> this is the first model that stopped hallucinating our internal API "
    "docs. Big deal for us.",
    "The pricing complaints are overblown - compute costs went up across the board, this "
    "isn't OpenAI-specific.",
    "Cool benchmarks but where's the actual latency data for production workloads?",
]

DEMO_TOP_STORIES = [
    {"title": "OpenAI announces GPT-5 with major reasoning improvements", "points": 1284,
     "objectID": "demo-1"},
    {"title": "GPT-5 API pricing is higher than expected, developers push back", "points": 542,
     "objectID": "demo-2"},
]


def main():
    ap = argparse.ArgumentParser(description="Generate LLM Community Opinion for an entity.")
    ap.add_argument("--entity", help="entity name as in watchlist.json (fetches live HN)")
    ap.add_argument("--provider", choices=["groq", "claude"], default=None)
    ap.add_argument("--model", default=None, help="override the model id")
    ap.add_argument("--demo", action="store_true", help="use the offline comment fixture, no network")
    ap.add_argument("--sector", action="store_true",
                     help="run sector-theme clustering (requires --demo, or two --entity runs piped)")
    args = ap.parse_args()

    if args.sector:
        if not args.demo:
            sys.exit("--sector currently supports --demo only from the CLI; use the library "
                     "function cluster_sector_themes() to cluster real per-entity results.")
        demo_opinions = [
            {"entity": "OpenAI", "degraded": False, "sentiment": "mixed",
             "summary": "Community is impressed by GPT-5's reasoning gains but frustrated by pricing.",
             "themes": ["pricing", "reasoning quality"]},
            {"entity": "Anthropic", "degraded": False, "sentiment": "positive",
             "summary": "Developers praise Claude's coding reliability; some note higher latency.",
             "themes": ["coding reliability", "latency"]},
        ]
        result = cluster_sector_themes(demo_opinions)
        print(json.dumps(result, indent=2))
        return

    if args.demo:
        entity, ticker, comments = "OpenAI (demo)", None, clean_and_dedupe(DEMO_COMMENTS)
        meta = {"storiesAnalyzed": len(DEMO_TOP_STORIES), "commentsAnalyzed": len(comments)}
        groq_key = os.environ.get("GROQ_API_KEY")
        claude_key = os.environ.get("ANTHROPIC_API_KEY")
        provider = args.provider or ("groq" if groq_key else ("claude" if claude_key else None))
        if not comments or provider is None:
            result = _degraded("no comments" if not comments else "no LLM key set",
                                provider=provider or "none", meta=meta)
        else:
            system, user = build_messages(entity, ticker, comments)
            try:
                raw, used_model = _call_provider(system, user, provider, args.model, groq_key, claude_key)
                result = parse_and_validate(raw)
                result.update({"entity": entity, "ticker": ticker, "provider": provider,
                               "model": used_model, "degraded": False, **meta})
            except Exception as exc:
                result = _degraded(f"{type(exc).__name__}: {exc}", provider=provider, meta=meta)
        print(json.dumps(result, indent=2))
        return

    if not args.entity:
        sys.exit("Pass --entity NAME, --demo, or --sector --demo. See --help.")

    watchlist = json.loads(WATCHLIST_PATH.read_text(encoding="utf-8"))
    match = next((e for e in watchlist if e["entity"] == args.entity), None)
    if not match:
        sys.exit(f"'{args.entity}' not in watchlist.json. "
                 f"Options: {[e['entity'] for e in watchlist]}")
    entity, ticker = match["entity"], match.get("ticker")
    print(f"Fetching top {TOP_N_STORIES} HN stories for {entity}...")
    top_stories = _fetch_top_stories_ranked(match["queryTerms"])
    print(f"Fetching comments across {min(len(top_stories), TOP_N_STORIES)} stories...")
    result = generate_community_opinion(entity, top_stories, ticker=ticker, provider=args.provider,
                                         model=args.model)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
