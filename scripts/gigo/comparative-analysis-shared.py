"""Shared utilities for ComparativeAnalysisAgent.

Purpose: Build peer groups, fetch/normalize external data specs, and compute comparative metrics.
Input: Subsector configs, Alpha Vantage payloads, NewsAPI payloads, SerpAPI patent payloads, or local exports.
Output: Peer records, financial metrics, news sentiment summaries, patent summaries, and aggregate reports.
Side effects: Optional file writes through caller scripts; no network calls unless used by ingest wrappers.
Idempotent: Yes; local transformations are deterministic.
Recipe: recipes/comparativeanalysisagent.md
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_input(sample: Any | None = None) -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="JSON string or path.")
    parser.add_argument("--output", help="Optional output path.")
    args = parser.parse_args()
    if args.input:
        candidate = Path(args.input)
        data = json.loads(candidate.read_text() if candidate.exists() else args.input)
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
        data = json.loads(text) if text else sample
    else:
        data = sample
    return {"data": data, "output": args.output}


def emit(data: Any, output_path: str | None = None) -> None:
    text = json.dumps(data, indent=2, sort_keys=True, default=str)
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n")
    print(text)


PEERS = {
    "Cloud Infrastructure": [
        {"rank": 1, "ticker": "MSFT", "company_name": "Microsoft"},
        {"rank": 2, "ticker": "AMZN", "company_name": "Amazon"},
        {"rank": 3, "ticker": "GOOGL", "company_name": "Google"},
        {"rank": 4, "ticker": "ORCL", "company_name": "Oracle"},
    ],
    "Semiconductors": [
        {"rank": 1, "ticker": "NVDA", "company_name": "NVIDIA"},
        {"rank": 2, "ticker": "AMD", "company_name": "AMD"},
        {"rank": 3, "ticker": "INTC", "company_name": "Intel"},
        {"rank": 4, "ticker": "AVGO", "company_name": "Broadcom"},
    ],
    "LLM Developers": [
        {"rank": 1, "ticker": "MSFT", "company_name": "Microsoft (OpenAI)"},
        {"rank": 2, "ticker": "GOOGL", "company_name": "Google (Gemini)"},
        {"rank": 3, "ticker": "META", "company_name": "Meta (Llama)"},
        {"rank": 4, "ticker": "AMZN", "company_name": "Amazon (Claude/Bedrock)"},
    ],
    "Enterprise AI": [
        {"rank": 1, "ticker": "CRM", "company_name": "Salesforce"},
        {"rank": 2, "ticker": "NOW", "company_name": "ServiceNow"},
        {"rank": 3, "ticker": "PLTR", "company_name": "Palantir"},
        {"rank": 4, "ticker": "SNOW", "company_name": "Snowflake"},
    ],
}


def peer_companies(subsector: str = "Cloud Infrastructure") -> list[dict[str, Any]]:
    return [{**row, "subsector": subsector} for row in PEERS.get(subsector, PEERS["Cloud Infrastructure"])]


def config_for(companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{**company, "analysis_start_time": datetime.now(timezone.utc).isoformat(), "alpha_vantage_env": "ALPHA_VANTAGE_API_KEY", "newsapi_env": "NEWSAPI_KEY", "serpapi_env": "SERPAPI_KEY", "total_companies": len(companies)} for company in companies]


def fetch_alpha_vantage(function: str, ticker: str, timeout: int = 20) -> dict[str, Any]:
    return {"source": "Alpha Vantage", "function": function, "ticker": ticker, "credential_env": "ALPHA_VANTAGE_API_KEY", "timeout_seconds": timeout, "live_call_performed": False, "status": "approval_required_handoff"}


def fetch_newsapi(company_name: str, timeout: int = 20) -> dict[str, Any]:
    return {"source": "NewsAPI", "company_name": company_name, "credential_env": "NEWSAPI_KEY", "timeout_seconds": timeout, "live_call_performed": False, "status": "approval_required_handoff", "articles": []}


def fetch_patents(company_name: str, timeout: int = 20) -> dict[str, Any]:
    return {"source": "SerpAPI Google Patents", "company_name": company_name, "credential_env": "SERPAPI_KEY", "timeout_seconds": timeout, "live_call_performed": False, "status": "approval_required_handoff", "organic_results": []}


def number(value: Any) -> float | None:
    if value in (None, "", "None", "-"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def financial_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    overview = payload.get("overview", payload)
    ts = payload.get("time_series", payload).get("Time Series (Daily)", {})
    dates = sorted(ts.keys(), reverse=True)
    current = number(ts.get(dates[0], {}).get("4. close")) if dates else None
    old = number(ts.get(dates[29], {}).get("4. close")) if len(dates) > 29 else current
    momentum = (current - old) / old if current and old else None
    metrics = {
        "ticker": payload.get("ticker") or overview.get("Symbol"),
        "company_name": payload.get("company_name") or overview.get("Name"),
        "market_cap": number(overview.get("MarketCapitalization")),
        "pe_ratio": number(overview.get("PERatio")),
        "profit_margin": number(overview.get("ProfitMargin")),
        "operating_margin": number(overview.get("OperatingMarginTTM")),
        "revenue_growth": number(overview.get("QuarterlyRevenueGrowthYOY")),
        "roe": number(overview.get("ReturnOnEquityTTM")),
        "roa": number(overview.get("ReturnOnAssetsTTM")),
        "beta": number(overview.get("Beta")),
        "price_momentum_30d": momentum,
    }
    score_inputs = [v for v in [metrics["profit_margin"], metrics["operating_margin"], metrics["revenue_growth"], metrics["roe"], metrics["price_momentum_30d"]] if isinstance(v, float)]
    metrics["financial_health_score"] = round(sum(score_inputs) / len(score_inputs), 4) if score_inputs else None
    return metrics


def news_sentiment(payload: dict[str, Any]) -> dict[str, Any]:
    articles = payload.get("articles", [])
    pos_words = ["growth", "beat", "strong", "record", "gain", "surge", "profit", "upgrade"]
    neg_words = ["loss", "drop", "fall", "downgrade", "lawsuit", "weak", "risk", "probe"]
    pos = neg = 0
    for article in articles:
        text = f"{article.get('title', '')} {article.get('description', '')}".lower()
        pos += sum(text.count(w) for w in pos_words)
        neg += sum(text.count(w) for w in neg_words)
    total = max(pos + neg, 1)
    return {"company_name": payload.get("company_name", "UNKNOWN"), "article_count": len(articles), "positive_score": round(pos / total, 3), "negative_score": round(neg / total, 3), "dominant_sentiment": "positive" if pos > neg else "negative" if neg > pos else "neutral"}


def patent_summary(payload: dict[str, Any]) -> dict[str, Any]:
    patents = payload.get("organic_results", [])
    assignees = sorted({p.get("assignee") or p.get("assignee_name") for p in patents if p.get("assignee") or p.get("assignee_name")})
    return {"company_name": payload.get("company_name", assignees[0] if assignees else "UNKNOWN"), "patent_count": len(patents), "assignees": assignees[:5], "ai_patent_signal": "high" if len(patents) >= 20 else "medium" if patents else "missing"}


def aggregate_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {"record_count": len(records), "records": records, "generated_at": datetime.now(timezone.utc).isoformat()}
