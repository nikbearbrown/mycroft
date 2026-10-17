# =============================================================================
# Week 7 deliverable — LLM narrative layer (narrative, theme, reception tone).
#
# Turns an entity's top HN story titles into a one-paragraph narrative, a theme
# tag, and a technical-community reception tone. This is the QUALITATIVE layer:
# the deterministic Buzz Score already measures HOW MUCH attention an entity gets
# (Weeks 2-4); this layer describes WHAT the attention is about and how it's being
# received. Per the Week 6 backtest, buzz is treated as an ATTENTION signal, not a
# validated price predictor, so the tone is "technical-community reception," not a
# stock call.
#
# Model decision (see docs/llm_narrative_design.md): default = Groq
# `llama-3.3-70b-versatile` (best free-tier quality for financial-adjacent text);
# `llama-3.1-8b-instant` is the fast/cheap fallback; Claude is the drop-in
# alternative. All configurable via env; NO key -> graceful degrade to a null
# narrative so the deterministic score/digest still ship.
#
# Use as a library:  from llm_narrative import generate_narrative
# Use from the CLI:   python llm_narrative.py --entity OpenAI      (fetches live HN)
#                     python llm_narrative.py --demo               (offline fixture)
#                     python llm_narrative.py --provider claude --entity NVIDIA
# Needs GROQ_API_KEY (or ANTHROPIC_API_KEY for --provider claude) in .env.
# =============================================================================

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

from metric_generation import parse_hit

load_dotenv()

# --- Controlled vocabularies (plan.md "Signals produced") --------------------
THEMES = ["launch", "outage", "funding", "research", "controversy", "hiring"]
TONES = ["bullish", "bearish", "neutral"]

# --- Provider / model config (overridable via env) ---------------------------
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-3-5-haiku-latest")
ANTHROPIC_VERSION = "2023-06-01"

ALGOLIA_URL = "https://hn.algolia.com/api/v1/search_by_date"
TOP_N_STORIES = 5           # titles handed to the LLM; enough context, small token cost
MAX_TITLE_CHARS = 200

WATCHLIST_PATH = Path(__file__).parent / "watchlist.json"


# --- Prompt ------------------------------------------------------------------
def build_messages(entity, ticker, top_stories):
    """Assemble the chat messages. The model sees ONLY the story titles/points we
    give it, and is told to ground its output in them and not invent facts."""
    lines = []
    for i, s in enumerate(top_stories, 1):
        title = (s.get("title") or "").strip()[:MAX_TITLE_CHARS]
        lines.append(f"{i}. [{s.get('points', 0)} pts] {title}")
    stories_block = "\n".join(lines) if lines else "(no stories this window)"

    system = (
        "You are a technical-community analyst for an AI-sector attention tracker. "
        "You read Hacker News story titles about one entity and summarize how the "
        "technical community is discussing it. Buzz measures ATTENTION, not price "
        "direction: an outage and a celebrated launch both draw heavy discussion. "
        "Ground every statement in the provided titles; never invent facts, numbers, "
        "or events not implied by them. Reply with a single JSON object only."
    )
    user = (
        f"Entity: {entity}" + (f" (ticker {ticker})" if ticker else "") + "\n"
        f"Top Hacker News stories this window (most-upvoted first):\n{stories_block}\n\n"
        "Return JSON with exactly these keys:\n"
        '  "narrative": one paragraph, <= 70 words, plain English, grounded in the titles above.\n'
        f'  "theme": the single dominant news type, one of {THEMES}.\n'
        f'  "tone": the technical community\'s reception, one of {TONES} '
        "(bullish = enthusiastic/positive reception, bearish = critical/negative, "
        "neutral = mixed or purely informational).\n"
        "If the titles are too sparse to judge, use theme/tone that best fit and keep "
        "the narrative appropriately hedged."
    )
    return system, user


# --- Provider calls ----------------------------------------------------------
def call_groq(system, user, model, api_key):
    body = {
        "model": model,
        "temperature": 0.3,        # low: consistent, less embellishment
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
        "max_tokens": 400,
        "temperature": 0.3,
        "system": system + " Output only the JSON object, no prose before or after.",
        "messages": [{"role": "user", "content": user}],
    }
    resp = requests.post(ANTHROPIC_URL, json=body, timeout=45, headers={
        "x-api-key": api_key, "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json"})
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


# --- Parse + validate --------------------------------------------------------
def _coerce_enum(value, allowed, fallback):
    """Map a model's value onto the controlled vocabulary; fallback if unrecognized."""
    if isinstance(value, str):
        v = value.strip().lower()
        if v in allowed:
            return v, False
    return fallback, True  # (value, was_coerced)


def parse_and_validate(raw_text):
    """Parse the model's JSON and force theme/tone into the controlled vocab.
    Raises ValueError if the text is not usable JSON with a narrative."""
    # Claude may wrap JSON in stray text; grab the outermost braces defensively.
    text = raw_text.strip()
    if not text.startswith("{"):
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("no JSON object in model output")
        text = text[start:end + 1]
    obj = json.loads(text)

    narrative = (obj.get("narrative") or "").strip()
    if not narrative:
        raise ValueError("model returned empty narrative")

    theme, theme_coerced = _coerce_enum(obj.get("theme"), THEMES, "research")
    tone, tone_coerced = _coerce_enum(obj.get("tone"), TONES, "neutral")
    return {
        "narrative": narrative,
        "theme": theme,
        "tone": tone,
        # Honest flag: the enum wasn't one we asked for and we snapped it. A
        # judgment about a judgment — surfaced, not hidden (SNICKERDOODLE P3).
        "enumCoerced": bool(theme_coerced or tone_coerced),
    }


# --- Public entry point ------------------------------------------------------
def generate_narrative(entity, top_stories, ticker=None, provider=None, model=None):
    """Return {narrative, theme, tone, ...} for one entity, or a DEGRADED record
    (narrative=None) if no key is set or the call/parse fails. Never raises: the
    deterministic score and digest must ship even when the LLM is unavailable."""
    groq_key = os.environ.get("GROQ_API_KEY")
    claude_key = os.environ.get("ANTHROPIC_API_KEY")

    # Auto-select provider by which key exists, unless explicitly asked.
    if provider is None:
        provider = "groq" if groq_key else ("claude" if claude_key else None)

    if provider is None:
        return _degraded("no LLM key set (GROQ_API_KEY / ANTHROPIC_API_KEY)", provider="none")

    system, user = build_messages(entity, ticker, top_stories or [])
    try:
        if provider == "groq":
            if not groq_key:
                return _degraded("GROQ_API_KEY not set", provider="groq")
            raw = call_groq(system, user, model or GROQ_MODEL, groq_key)
            used_model = model or GROQ_MODEL
        elif provider == "claude":
            if not claude_key:
                return _degraded("ANTHROPIC_API_KEY not set", provider="claude")
            raw = call_claude(system, user, model or CLAUDE_MODEL, claude_key)
            used_model = model or CLAUDE_MODEL
        else:
            return _degraded(f"unknown provider '{provider}'", provider=provider)

        parsed = parse_and_validate(raw)
    except Exception as exc:  # noqa: BLE001 — degrade on ANY failure, never crash the run
        return _degraded(f"{type(exc).__name__}: {exc}", provider=provider)

    parsed.update({"entity": entity, "ticker": ticker, "provider": provider,
                   "model": used_model, "degraded": False})
    return parsed


def _degraded(reason, provider):
    return {"entity": None, "ticker": None, "narrative": None, "theme": None,
            "tone": None, "enumCoerced": False, "provider": provider,
            "model": None, "degraded": True, "reason": reason}


# --- CLI helpers -------------------------------------------------------------
def fetch_top_stories(query_terms, days=7):
    """Fetch this entity's top HN stories (by points) over a trailing window,
    reusing the Week-5 quoted/advancedSyntax exact-phrase fix and parse_hit."""
    import time
    since = int(time.time()) - days * 86400
    by_id = {}
    for term in query_terms:
        params = {"query": f'"{term}"', "tags": "story", "advancedSyntax": "true",
                  "numericFilters": f"created_at_i>{since}", "hitsPerPage": 100}
        try:
            r = requests.get(ALGOLIA_URL, params=params, timeout=30)
            r.raise_for_status()
            for hit in r.json().get("hits", []):
                rec = parse_hit(hit)
                if rec["objectID"]:
                    by_id[rec["objectID"]] = rec
        except Exception:
            continue
    hits = sorted(by_id.values(), key=lambda h: h.get("points") or 0, reverse=True)
    return hits[:TOP_N_STORIES]


DEMO_STORIES = [  # offline fixture so the module is testable with no network
    {"title": "OpenAI announces GPT-5 with major reasoning improvements", "points": 1284},
    {"title": "GPT-5 API pricing is higher than expected, developers push back", "points": 542},
    {"title": "Show HN: I rebuilt my startup on the GPT-5 API in a weekend", "points": 310},
]


def main():
    ap = argparse.ArgumentParser(description="Generate LLM narrative/theme/tone for an entity.")
    ap.add_argument("--entity", help="entity name as in watchlist.json (fetches live HN)")
    ap.add_argument("--provider", choices=["groq", "claude"], default=None)
    ap.add_argument("--model", default=None, help="override the model id")
    ap.add_argument("--demo", action="store_true", help="use the offline OpenAI fixture, no network")
    args = ap.parse_args()

    if args.demo:
        entity, ticker, stories = "OpenAI (demo)", None, DEMO_STORIES
    elif args.entity:
        watchlist = json.loads(WATCHLIST_PATH.read_text(encoding="utf-8"))
        match = next((e for e in watchlist if e["entity"] == args.entity), None)
        if not match:
            sys.exit(f"'{args.entity}' not in watchlist.json. "
                     f"Options: {[e['entity'] for e in watchlist]}")
        entity, ticker = match["entity"], match.get("ticker")
        print(f"Fetching top {TOP_N_STORIES} HN stories for {entity}...")
        stories = fetch_top_stories(match["queryTerms"])
        print(f"  got {len(stories)} stories; top: "
              f"{stories[0]['title'][:70] if stories else '(none)'}")
    else:
        sys.exit("Pass --entity <name> or --demo. See --help.")

    result = generate_narrative(entity, stories, ticker=ticker,
                                provider=args.provider, model=args.model)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
