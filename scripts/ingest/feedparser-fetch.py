"""Purpose: Fetch articles from a configured RSS/Atom feed.
Input: JSON object with feed_url/url and optional feed_last_updated, usually from the sources table.
Output: JSON object with articles for data/raw/news-monitoring-agent/.
Side effects: Performs an HTTP GET to the feed URL; optionally writes JSON to the supplied output path.
Idempotent: Yes for the same feed state because it only returns fetched records and does not mutate source state.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import json
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any

from scripts.tools.news_monitoring_agent_shared import emit_json, load_json_input, stable_id


def feedparser_fetch(source: dict[str, Any], timeout: int = 20) -> dict[str, Any]:
    """Purpose: Fetch articles from a configured RSS/Atom feed.
    Input: JSON object with feed_url/url and optional feed_last_updated.
    Output: JSON object with articles parsed from feed entries.
    Side effects: Performs an HTTP GET to the feed URL.
    Idempotent: Yes for unchanged feed content.
    Recipe: recipes/news-monitoring-agent.md
    """
    feed_url = source.get("feed_url") or source.get("url")
    if not feed_url:
        raise ValueError("feedparser_fetch requires feed_url or url")
    with urllib.request.urlopen(str(feed_url), timeout=timeout) as response:
        raw = response.read()
    root = ET.fromstring(raw)
    articles: list[dict[str, Any]] = []
    for item in root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry"):
        title = item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title") or ""
        link = item.findtext("link") or ""
        if not link:
            link_el = item.find("{http://www.w3.org/2005/Atom}link")
            link = link_el.attrib.get("href", "") if link_el is not None else ""
        content = item.findtext("description") or item.findtext("summary") or ""
        published = item.findtext("pubDate") or item.findtext("updated") or ""
        articles.append(
            {
                "id": stable_id(feed_url, link, title, published),
                "title": title.strip(),
                "url": link.strip(),
                "content": content.strip(),
                "published_date": published.strip(),
                "source_name": source.get("source_name") or source.get("name") or feed_url,
                "fetch_lib": "stdlib_xml",
            }
        )
    return {"feed_url": feed_url, "articles": articles, "raw_bytes": len(raw)}


if __name__ == "__main__":
    payload = load_json_input({"feed_url": "https://example.com/feed.xml"})
    try:
        result = feedparser_fetch(payload["data"])
    except Exception as exc:
        result = {"error": str(exc), "sample_input": payload["data"]}
    emit_json(result, payload["output"])
