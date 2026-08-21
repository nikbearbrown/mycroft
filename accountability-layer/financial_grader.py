"""
Financial grader — Week 9/10 analyst skeleton (context/schedule.md).

Thin orchestration only, no ratio engine: fetch EDGAR fundamentals for a
ticker, summarize them into a short context string, then run the *existing*
accountability-mesh pipeline (directive injection, structural parsing,
ADR-07 retry/halt, ReasoningObject audit trail) unchanged. LangFuse traces
the tool call and each LLM attempt from the outside via observability.py.

AgentID.FINANCIAL (schemas.py) is the agent identity used for every run.
No structured recommendation/target_price — the conclusion is the same
free-text <conclusion> block the rest of the pipeline already produces.
Ratio calculations, competitor-filing lookups, and backtesting are
out of scope here (see context/schedule.md Weeks 10/11/13).

ADR: stdlib only for data access (urllib) — reuses the same fetch pattern
as verification.py. langfuse is the one deliberate non-stdlib dependency,
confined to observability.py.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
import uuid
from typing import Callable

from langfuse import observe

from middleware import ValidationLoopResult, run_validation_loop
from observability import make_traced_adapter
from schemas import AgentID

_TIMEOUT_S = 10
_MAX_BYTES = 10_000_000  # large-cap companyfacts JSON can run ~4MB+; cap the read
_USER_AGENT = "accountability-layer/1.0 audit-research@project.local"

_TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
_FACTS_URL_TMPL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

# Headline us-gaap concepts pulled into the LLM context — not a ratio engine,
# just enough real data to make the synthesis call meaningful.
_HEADLINE_CONCEPTS: tuple[str, ...] = ("Assets", "Revenues", "NetIncomeLoss")


class EdgarFetchError(Exception):
    """Raised when an EDGAR fetch fails: network error, non-200, or bad JSON."""


def _http_get_json(url: str) -> dict:
    """Default fetch_fn: real HTTP GET against SEC EDGAR. stdlib urllib only."""
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
            body = resp.read(_MAX_BYTES).decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise EdgarFetchError(f"Failed to fetch {url}: {exc}") from exc
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise EdgarFetchError(f"Non-JSON response from {url}: {exc}") from exc


@observe(as_type="tool")
def lookup_cik(ticker: str, fetch_fn: Callable[[str], dict] | None = None) -> str:
    """
    Resolve a ticker to its zero-padded 10-digit SEC CIK via
    company_tickers.json. fetch_fn(url) -> dict is injectable for tests
    (default: real HTTP GET, no test should hit the network).
    """
    fetch = fetch_fn or _http_get_json
    data = fetch(_TICKER_MAP_URL)
    ticker_upper = ticker.upper().strip()
    for entry in data.values():
        if entry.get("ticker", "").upper() == ticker_upper:
            return f"{int(entry['cik_str']):010d}"
    raise EdgarFetchError(f"Ticker {ticker!r} not found in SEC company_tickers.json")


@observe(as_type="tool")
def fetch_company_facts(
    ticker: str, cik: str, fetch_fn: Callable[[str], dict] | None = None
) -> dict:
    """
    Fetch SEC EDGAR companyfacts JSON for a given ticker/CIK.
    fetch_fn(url) -> dict is injectable for tests (default: real HTTP GET).
    Traced as a LangFuse tool span (as_type="tool") via this decorator.
    """
    fetch = fetch_fn or _http_get_json
    url = _FACTS_URL_TMPL.format(cik=cik)
    return fetch(url)


def _latest_value(facts: dict, concept: str) -> float | None:
    """Most recent numeric value for a us-gaap concept, or None if absent."""
    try:
        units = facts["facts"]["us-gaap"][concept]["units"]
    except (KeyError, TypeError):
        return None
    entries = [
        e
        for unit_entries in units.values()
        for e in unit_entries
        if isinstance(e.get("val"), (int, float))
    ]
    if not entries:
        return None
    latest = max(entries, key=lambda e: e.get("end", ""))
    return float(latest["val"])


def summarize_facts(ticker: str, facts: dict) -> str:
    """Short plain-text context string built from headline EDGAR facts."""
    lines = [f"Ticker: {ticker}"]
    for concept in _HEADLINE_CONCEPTS:
        value = _latest_value(facts, concept)
        lines.append(f"{concept}: {value if value is not None else 'not reported'}")
    return "\n".join(lines)


@observe(name="analyze_ticker")
def analyze_ticker(
    ticker: str,
    cik: str,
    call_agent_fn: Callable,
    *,
    run_id: uuid.UUID | None = None,
    fetch_fn: Callable[[str], dict] | None = None,
) -> ValidationLoopResult:
    """
    Minimal financial-grader skeleton:
      1. Fetch EDGAR fundamentals (traced LangFuse tool call).
      2. Summarize into a short context string.
      3. Run the unmodified accountability-mesh validation loop, with the
         supplied adapter wrapped so each LLM attempt is its own traced
         LangFuse generation span (see observability.make_traced_adapter).

    Returns the same ValidationLoopResult run_validation_loop always returns;
    raises HaltError exactly as run_validation_loop does on double failure.
    """
    if run_id is None:
        run_id = uuid.uuid4()

    facts = fetch_company_facts(ticker, cik, fetch_fn=fetch_fn)
    context = summarize_facts(ticker, facts)

    traced_adapter = make_traced_adapter(call_agent_fn, name=f"llm_call:{ticker}")

    return run_validation_loop(
        ticker,
        context,
        run_id,
        AgentID.FINANCIAL,
        call_agent_fn=traced_adapter,
    )
