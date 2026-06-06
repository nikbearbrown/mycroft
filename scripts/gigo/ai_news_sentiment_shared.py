"""Shared utilities for the AI News & Sentiment Agent.

Purpose: Normalize AI news articles, assign lightweight sentiment, and prepare Airtable/email payloads.
Input: NewsAPI-style JSON or verified article records from data/raw/ai-news-sentiment-agent/.
Output: Sentiment records, Airtable payloads, and email handoff records.
Side effects: Optional file writes through caller scripts; no network, Airtable, or email calls.
Idempotent: Yes; local transformations are deterministic.
Recipe: recipes/ai-news-sentiment-agent.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_input(sample: Any | None = None) -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="JSON string or path to JSON file.")
    parser.add_argument("--output", help="Optional path to write JSON output.")
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


def ticker_config(payload: dict[str, Any] | None = None) -> dict[str, str]:
    payload = payload or {}
    return {"ticker": str(payload.get("ticker") or "AI"), "query": str(payload.get("query") or "nvidia")}


def split_articles(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [article for article in payload.get("articles", []) if isinstance(article, dict)]


def score_sentiment(article: dict[str, Any]) -> dict[str, Any]:
    title = str(article.get("title") or "").lower()
    if any(word in title for word in ("gain", "raise", "rally", "beat", "surge")):
        sentiment = "positive"
    elif any(word in title for word in ("loss", "drop", "fall", "probe", "cuts")):
        sentiment = "negative"
    else:
        sentiment = "neutral"
    source = article.get("source", {})
    return {
        "title": article.get("title", ""),
        "sentiment": sentiment,
        "source": source.get("name") if isinstance(source, dict) else str(source),
        "publishedAt": article.get("publishedAt", ""),
        "url": article.get("url", ""),
    }


def airtable_payload(record: dict[str, Any]) -> dict[str, Any]:
    return {"operation": "create", "destination": "airtable", "approval_required": True, "fields": dict(record)}


def negative_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record for record in records if "negative" in str(record.get("sentiment", "")).lower()]


def email_handoff(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "approval_required",
        "smtp_env": ["SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"],
        "subject": "Negative AI News Detected",
        "body": f"Negative sentiment article found: {record.get('title')} ({record.get('url')})",
        "sent": False,
    }
