"""Shared utilities for the Mycroft News Intelligence Agent.

Purpose: Build company news queries, normalize news articles, score sentiment risk, and prepare alerts.
Input: Company configs, NewsAPI/Google RSS payloads, sentiment scores, or verified local article records.
Output: Query records, normalized article records, risk records, database payloads, alert payloads, and reports.
Side effects: Optional file writes through caller scripts; no network, database, model, or email calls.
Idempotent: Yes; local transformations are deterministic except timestamps.
Recipe: recipes/mycroft-news-intelligence-agent.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def load_input(sample: Any | None = None) -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="JSON string, raw text, or path.")
    parser.add_argument("--output", help="Optional path to write JSON.")
    args = parser.parse_args()
    if args.input:
        candidate = Path(args.input)
        text = candidate.read_text() if candidate.exists() else args.input
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = text
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
        try:
            data = json.loads(text) if text else sample
        except json.JSONDecodeError:
            data = text
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


def company_list() -> list[dict[str, Any]]:
    return [
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "aliases": ["nvidia", "nvda", "jensen huang"], "riskMultiplier": 1.0},
        {"symbol": "AMD", "name": "Advanced Micro Devices", "aliases": ["amd", "lisa su"], "riskMultiplier": 0.9},
        {"symbol": "TSM", "name": "Taiwan Semiconductor Manufacturing Company", "aliases": ["tsmc", "taiwan semiconductor"], "riskMultiplier": 0.85},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "aliases": ["microsoft", "azure", "copilot"], "riskMultiplier": 0.85},
        {"symbol": "AAPL", "name": "Apple Inc.", "aliases": ["apple", "tim cook"], "riskMultiplier": 0.85},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "aliases": ["google", "alphabet", "gemini"], "riskMultiplier": 0.85},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "aliases": ["amazon", "aws"], "riskMultiplier": 0.85},
        {"symbol": "META", "name": "Meta Platforms Inc.", "aliases": ["meta", "facebook", "llama"], "riskMultiplier": 0.9},
        {"symbol": "CRM", "name": "Salesforce Inc.", "aliases": ["salesforce", "crm"], "riskMultiplier": 0.8},
        {"symbol": "SNOW", "name": "Snowflake Inc.", "aliases": ["snowflake", "snow"], "riskMultiplier": 0.8},
        {"symbol": "PLTR", "name": "Palantir Technologies", "aliases": ["palantir", "pltr"], "riskMultiplier": 0.9},
    ]


def build_queries(companies: list[dict[str, Any]], lookback_hours: int = 72) -> list[dict[str, Any]]:
    start = (datetime.now(timezone.utc) - timedelta(hours=lookback_hours)).isoformat()
    return [{"q": f"{c['symbol']} OR {c['name']}", "from": start, "language": "en", "sortBy": "publishedAt", "pageSize": 100, "company": c["symbol"], "riskMultiplier": c.get("riskMultiplier", 1.0)} for c in companies]


def fetch_newsapi(query: dict[str, Any], timeout: int = 20) -> dict[str, Any]:
    return {"source": "NewsAPI", "query": query, "credential_env": "NEWSAPI_KEY", "timeout_seconds": timeout, "live_call_performed": False, "status": "approval_required_handoff", "articles": []}


def fetch_google_rss(company: str, timeout: int = 20) -> dict[str, Any]:
    return {"source": "Google News RSS", "company": company, "timeout_seconds": timeout, "live_call_performed": False, "status": "approval_required_handoff", "raw": ""}


def clean(text: Any) -> str:
    text = re.sub(r"https?://\S+", "", str(text or ""))
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_newsapi(payload: dict[str, Any]) -> list[dict[str, Any]]:
    articles = payload.get("articles", []) if isinstance(payload, dict) else []
    out = []
    for article in articles:
        source = article.get("source", {})
        title = article.get("title", "")
        description = article.get("description", "")
        processed = clean(f"{title} {description}")
        out.append({"title": title, "url": article.get("url", ""), "publishedAt": article.get("publishedAt", ""), "description": description, "processed_text": processed, "content_hash": hashlib.md5(processed.encode()).hexdigest(), "source": source.get("name") if isinstance(source, dict) else str(source), "content": article.get("content", "")})
    return out


def parse_google_rss(raw: str) -> list[dict[str, Any]]:
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return []
    out = []
    for item in root.findall(".//item"):
        title = item.findtext("title") or ""
        description = item.findtext("description") or ""
        out.append({"title": title, "url": item.findtext("link") or "", "description": description, "publishedAt": item.findtext("pubDate") or "", "source": item.findtext("source") or "Google News RSS", "processed_text": clean(f"{title} {description}")})
    return out


def finbert_spec(article: dict[str, Any]) -> dict[str, Any]:
    return {"provider": "huggingface", "model": "ProsusAI/finbert", "credential_env": "HUGGINGFACE_API_TOKEN", "live_call_performed": False, "input": article.get("processed_text") or article.get("title", "")}


def lexical_sentiment_scores(text: str) -> list[dict[str, float | str]]:
    lower = text.lower()
    neg = sum(lower.count(w) for w in ["loss", "drop", "fall", "lawsuit", "downgrade", "probe", "risk"])
    pos = sum(lower.count(w) for w in ["gain", "raise", "beat", "surge", "upgrade", "profit"])
    total = max(pos + neg, 1)
    negative = neg / total
    positive = pos / total
    neutral = max(0.0, 1.0 - negative - positive)
    return [{"label": "positive", "score": positive}, {"label": "negative", "score": negative}, {"label": "neutral", "score": neutral}]


def risk_record(scores: list[dict[str, Any]], item_number: int = 0, multiplier: float = 1.0) -> dict[str, Any]:
    by_label = {row["label"]: float(row["score"]) for row in scores}
    negative = by_label.get("negative", 0.0) * multiplier
    if negative > 0.7:
        level = "CRITICAL"
    elif negative > 0.5:
        level = "HIGH"
    elif negative > 0.3:
        level = "MEDIUM"
    elif negative > 0.1:
        level = "LOW"
    else:
        level = "MINIMAL"
    dominant = max(by_label, key=by_label.get) if by_label else "neutral"
    return {"item_number": item_number, "sentiment_positive": round(by_label.get("positive", 0), 3), "sentiment_negative": round(by_label.get("negative", 0), 3), "sentiment_neutral": round(by_label.get("neutral", 0), 3), "dominant_sentiment": dominant, "risk_score": round(negative, 3), "risk_level": level, "processed_at": datetime.now(timezone.utc).isoformat()}


def db_payload(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"table": "financial_intelligence", "operation": "insert", "approval_required": True, "row": record} for record in records]


def alerts(records: list[dict[str, Any]]) -> dict[str, Any]:
    alert_rows = []
    summary = {"total_articles": len(records), "critical_alerts": 0, "high_alerts": 0, "medium_alerts": 0, "low_alerts": 0}
    for record in records:
        level = record.get("risk_level", "UNKNOWN")
        if level == "CRITICAL":
            summary["critical_alerts"] += 1
        elif level == "HIGH":
            summary["high_alerts"] += 1
        elif level == "MEDIUM":
            summary["medium_alerts"] += 1
        else:
            summary["low_alerts"] += 1
        if level in {"HIGH", "CRITICAL"}:
            alert_rows.append({"alert_type": f"{level}_RISK_DETECTED", "risk_level": level, "risk_score": record.get("risk_score", 0), "requires_attention": True})
    return {"summary": summary, "alerts": alert_rows, "alert_count": len(alert_rows), "needs_immediate_attention": any(a["risk_level"] == "CRITICAL" for a in alert_rows)}


def email_handoff(alert_payload: dict[str, Any]) -> dict[str, Any]:
    return {"status": "approval_required", "smtp_env": ["SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"], "subject": f"Financial Risk Alert - {datetime.now(timezone.utc).date().isoformat()}", "body": alert_payload, "sent": False}


def daily_report(records: list[dict[str, Any]], email_handoffs: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    email_handoffs = email_handoffs or []
    return {"report_metadata": {"report_type": "DAILY_FINANCIAL_INTELLIGENCE", "report_date": datetime.now(timezone.utc).date().isoformat(), "analysis_period": "24_hours"}, "executive_summary": {"total_articles_analyzed": len(records), "alerts_generated": sum(1 for r in records if r.get("risk_level") in {"HIGH", "CRITICAL"}), "emails_prepared": len(email_handoffs), "system_status": "DIALOGIC_REVIEW_REQUIRED"}, "records": records}
