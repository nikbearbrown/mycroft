"""Shared utilities for the AI Talent Intelligence Agent.

Purpose: Normalize AI talent signals and prepare report/database/email payloads.
Input: ArXiv XML/API payloads, Serper news JSON, mock researcher rows, or verified local exports.
Output: JSON-compatible talent signals, aggregate statistics, reports, and handoff payloads.
Side effects: Optional file writes through caller scripts; no network, database, email, or LLM calls.
Idempotent: Yes; local parsing and scoring are deterministic except generated timestamps.
Recipe: recipes/ai-talent-intelligence-agent.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_input(sample: Any | None = None) -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="JSON string, raw text, or path to an input file.")
    parser.add_argument("--output", help="Optional path to write JSON output.")
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
        if text:
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                data = text
        else:
            data = sample
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


def text_words(value: str) -> set[str]:
    return {word.lower() for word in re.findall(r"[A-Za-z][A-Za-z0-9.-]+", value) if len(word) > 2}


def parse_arxiv_payload(payload: str | dict[str, Any]) -> list[dict[str, Any]]:
    """Parse ArXiv API XML or JSON fixture into research-paper signals."""
    raw = payload.get("raw", payload.get("body", "")) if isinstance(payload, dict) else payload
    if isinstance(raw, list):
        return raw
    records: list[dict[str, Any]] = []
    try:
        root = ET.fromstring(str(raw).encode("utf-8"))
        entries = root.findall(".//{http://www.w3.org/2005/Atom}entry") or root.findall(".//entry")
        for entry in entries:
            title = (entry.findtext("{http://www.w3.org/2005/Atom}title") or entry.findtext("title") or "").strip()
            summary = (entry.findtext("{http://www.w3.org/2005/Atom}summary") or entry.findtext("summary") or "").strip()
            link_el = entry.find("{http://www.w3.org/2005/Atom}id") or entry.find("id")
            url = link_el.text.strip() if link_el is not None and link_el.text else ""
            authors = [a.findtext("{http://www.w3.org/2005/Atom}name") or a.findtext("name") or "" for a in entry.findall(".//{http://www.w3.org/2005/Atom}author")]
            records.append(make_signal(title, summary, url, "ArXiv", "research", authors))
    except ET.ParseError:
        records.append(make_signal("ArXiv sample AI paper", str(raw)[:1000], "local-arxiv-sample", "ArXiv", "research", []))
    return records


def parse_news_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse Serper-style news JSON into talent movement signals."""
    articles = payload.get("news") or payload.get("raw", {}).get("news", []) if isinstance(payload, dict) else []
    return [
        make_signal(
            article.get("title", ""),
            article.get("snippet", ""),
            article.get("link") or article.get("url", ""),
            article.get("source") or "Serper News",
            "news",
            [],
            article.get("date", ""),
        )
        for article in articles
        if isinstance(article, dict)
    ]


def mock_researcher_rows() -> list[dict[str, Any]]:
    """Return local prototype researcher records from the n8n workflow."""
    now = datetime.now(timezone.utc).isoformat()
    return [
        {"name": "Ilya Sutskever", "current_company": "OpenAI", "h_index": 118, "influence_score": 98, "last_updated": now},
        {"name": "Dario Amodei", "current_company": "Anthropic", "h_index": 72, "influence_score": 92, "last_updated": now},
        {"name": "Demis Hassabis", "current_company": "Google DeepMind", "h_index": 95, "influence_score": 96, "last_updated": now},
        {"name": "Yann LeCun", "current_company": "Meta AI", "h_index": 150, "influence_score": 94, "last_updated": now},
    ]


def make_signal(title: str, body: str, url: str, source: str, source_type: str, authors: list[str], date: str = "") -> dict[str, Any]:
    companies = extract_companies(f"{title} {body} {source}")
    researchers = [name for name in authors if name] + extract_researchers(f"{title} {body}")
    tech = extract_technologies(f"{title} {body}")
    significance = min(10, 3 + len(companies) + len(researchers) + len(tech))
    return {
        "title": title.strip(),
        "snippet": body.strip()[:1000],
        "url": url,
        "source": source,
        "source_type": source_type,
        "date": date,
        "companies": companies,
        "researchers": researchers,
        "technologies": tech,
        "sentiment": "positive" if significance >= 7 else "neutral",
        "significance": significance,
        "discovered_at": datetime.now(timezone.utc).isoformat(),
    }


def extract_companies(text: str) -> list[str]:
    known = ["OpenAI", "Anthropic", "Google DeepMind", "Google", "Meta", "Microsoft", "DeepLearning.AI"]
    return [company for company in known if company.lower() in text.lower()]


def extract_researchers(text: str) -> list[str]:
    known = ["Ilya Sutskever", "Dario Amodei", "Demis Hassabis", "Yann LeCun", "Andrew Ng"]
    return [name for name in known if name.lower() in text.lower()]


def extract_technologies(text: str) -> list[str]:
    known = ["GPT-4", "Claude", "LLaMA", "Gemini", "AI Safety", "LLM", "multimodal"]
    lower = text.lower()
    return [tech for tech in known if tech.lower() in lower]


def filter_high_significance(signals: list[dict[str, Any]], threshold: int = 5) -> list[dict[str, Any]]:
    return [signal for signal in signals if int(signal.get("significance") or 0) > threshold]


def aggregate_statistics(signals: list[dict[str, Any]]) -> dict[str, Any]:
    companies = sorted({company for signal in signals for company in signal.get("companies", [])})
    researchers = sorted({person for signal in signals for person in signal.get("researchers", [])})
    technologies = sorted({tech for signal in signals for tech in signal.get("technologies", [])})
    scores = [int(signal.get("significance") or 0) for signal in signals]
    return {
        "total_signals": len(signals),
        "unique_companies": len(companies),
        "unique_researchers": len(researchers),
        "companies": companies,
        "researchers": researchers,
        "technologies": technologies,
        "avg_significance": round(sum(scores) / len(scores), 2) if scores else 0,
        "signals": signals,
    }


def intelligence_report(stats: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_signals": stats.get("total_signals", 0),
            "unique_companies": stats.get("unique_companies", 0),
            "unique_researchers": stats.get("unique_researchers", 0),
            "avg_significance": stats.get("avg_significance", 0),
        },
        "companies": stats.get("companies", []),
        "top_researchers": stats.get("researchers", []),
        "technologies": stats.get("technologies", []),
        "signals": stats.get("signals", []),
        "prototype_note": "Some researcher records in the original n8n workflow are mock/demo data and require provenance review.",
    }


def database_payload(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for company in report.get("companies", []):
        rows.append({"table": "company_metrics", "operation": "upsert", "company_name": company, "metric_date": datetime.now(timezone.utc).date().isoformat(), "talent_score": 75})
    return rows


def email_payload(report: dict[str, Any]) -> dict[str, str]:
    summary = report.get("summary", {})
    html = f"<h1>AI Talent Intelligence Report</h1><p>Total signals: {summary.get('total_signals', 0)}</p><p>Companies: {', '.join(report.get('companies', []))}</p>"
    return {"subject": "AI Talent Intelligence Report", "html": html}


def llm_invocation_spec(payload: dict[str, Any]) -> dict[str, Any]:
    return {"provider": "groq", "model": "llama-3.1-8b-instant", "credential_env": "GROQ_API_KEY", "live_call_performed": False, "input_preview": json.dumps(payload, default=str)[:1000]}
