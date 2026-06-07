"""Shared utilities for Workflow A -- Extract & Store Raw Data.

Purpose: Normalize AI-news feed payloads into raw_intelligence records.
Input: Raw RSS, Atom, JSON, or item records from data/raw/aeo-workflow-a/.
Output: JSON-compatible raw_intelligence records for data/verified/aeo-workflow-a/.
Side effects: Optional file writes through caller scripts; no network calls.
Idempotent: Yes; parsing and row preparation are deterministic for the same input.
Recipe: recipes/workflow-a-extract-store-raw-data.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


sys.path.append(str(repo_root()))


def load_input(sample: Any | None = None) -> dict[str, Any]:
    """Load JSON/text input from --input or stdin and return data plus output path."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="JSON string, raw text, or path to an input file.")
    parser.add_argument("--output", help="Optional path to write JSON output.")
    parser.add_argument("--url", help="Optional source URL for fetch scripts.")
    args = parser.parse_args()
    data: Any
    if args.input:
        candidate = Path(args.input)
        text = candidate.read_text() if candidate.exists() else args.input
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = text
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
        if text.strip():
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                data = text
        else:
            data = sample
    else:
        data = sample
    return {"data": data, "output": args.output, "url": args.url}


def emit(data: Any, output_path: str | None = None) -> None:
    """Print JSON and optionally write it to an explicit output path."""
    text = json.dumps(data, indent=2, sort_keys=True, default=str)
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n")
    print(text)


def stable_id(*parts: Any) -> str:
    payload = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def clean_text(value: Any, limit: int | None = None) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:limit] if limit else text


def first_text(node: ET.Element, names: list[str]) -> str:
    for name in names:
        value = node.findtext(name)
        if value:
            return value
    for child in list(node):
        if child.tag.split("}")[-1] in names and child.text:
            return child.text
    return ""


def parse_rss_or_atom(raw: str, source_name: str, source_type: str, topic_tag: str) -> list[dict[str, Any]]:
    """Parse RSS or Atom text into raw_intelligence-like item records."""
    root = ET.fromstring(raw.encode("utf-8") if isinstance(raw, str) else raw)
    nodes = root.findall(".//item")
    if not nodes:
        nodes = root.findall(".//{http://www.w3.org/2005/Atom}entry")
    items: list[dict[str, Any]] = []
    for node in nodes:
        link = first_text(node, ["link"])
        if not link:
            link_node = node.find("{http://www.w3.org/2005/Atom}link")
            link = link_node.attrib.get("href", "") if link_node is not None else ""
        title = first_text(node, ["title"])
        published = first_text(node, ["pubDate", "published", "updated"])
        content = first_text(node, ["description", "summary", "content", "encoded"])
        items.append(
            {
                "id": stable_id(source_name, link, title, published),
                "title": clean_text(title, 500),
                "source_name": source_name,
                "source_type": source_type,
                "url": clean_text(link),
                "raw_content": clean_text(content, 1000),
                "published_date": clean_text(published),
                "pulled_date": datetime.now(timezone.utc).isoformat(),
                "topic_tag": topic_tag,
                "processed": False,
            }
        )
    return items


def parse_reddit_json(payload: dict[str, Any], topic_tag: str = "ai") -> list[dict[str, Any]]:
    """Parse Reddit listing JSON into raw_intelligence-like item records."""
    children = payload.get("data", {}).get("children", []) if isinstance(payload, dict) else []
    items: list[dict[str, Any]] = []
    for child in children:
        data = child.get("data", {}) if isinstance(child, dict) else {}
        permalink = data.get("permalink") or ""
        url = data.get("url") or f"https://www.reddit.com{permalink}"
        created = data.get("created_utc")
        published = datetime.fromtimestamp(created, timezone.utc).isoformat() if isinstance(created, (int, float)) else ""
        content = data.get("selftext") or data.get("title") or ""
        items.append(
            {
                "id": stable_id("Reddit", url, data.get("title"), published),
                "title": clean_text(data.get("title"), 500),
                "source_name": "Reddit",
                "source_type": "community",
                "url": clean_text(url),
                "raw_content": clean_text(content, 1000),
                "published_date": published,
                "pulled_date": datetime.now(timezone.utc).isoformat(),
                "topic_tag": topic_tag,
                "processed": False,
            }
        )
    return items


def prepare_store_rows(items: list[dict[str, Any]], source_name: str) -> list[dict[str, Any]]:
    """Prepare idempotent row payloads for raw_intelligence storage."""
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items:
        url = clean_text(item.get("url"))
        if not url or url in seen:
            continue
        seen.add(url)
        rows.append(
            {
                "title": clean_text(item.get("title"), 500),
                "source_name": item.get("source_name") or source_name,
                "source_type": item.get("source_type") or "news",
                "url": url,
                "raw_content": clean_text(item.get("raw_content") or item.get("content"), 1000),
                "published_date": item.get("published_date") or "",
                "pulled_date": item.get("pulled_date") or datetime.now(timezone.utc).isoformat(),
                "topic_tag": item.get("topic_tag") or "ai",
                "processed": False,
                "conflict_key": "url",
            }
        )
    return rows


def count_new_items(rows: list[dict[str, Any]]) -> dict[str, int]:
    """Count candidate new items and rows pulled in this cycle."""
    return {"new_items": len([row for row in rows if not row.get("processed")]), "this_cycle": len(rows)}
