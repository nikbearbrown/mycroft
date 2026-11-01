"""The `docs` tools as plain functions: open a filing through `edgar_pit`, address it by id.

A document key is `"<cik>/<accession>/<file name>"`, exactly the three things `edgar_pit` needs, so
the docs layer can never read a document the point-in-time rule would refuse: every open goes through
`PointInTimeEdgar.raw`, and a refusal propagates. Parsed documents are cached on disk under
`$AI_DEBT_DATA/docs_cache/` (a filing never changes once accepted), but the rule is checked on every
open, cached or not.

Every response is bounded (a page of results plus a cursor), the pattern the Private AI Valuation
Agent's MCP server settled on: a 424B prospectus has thousands of sentences, and a model handed all of
them reads none of them.
"""

from __future__ import annotations

import json
import re
import urllib.error
from pathlib import Path

from .. import config
from .parse import Document, parse_html

MAX_CHARS = 16_000
DEFAULT_LIMIT = 40
KEY = re.compile(r"^(\d{1,10})/(\d{10}-\d{2}-\d{6})/([\w.-]+)$")


class DocumentStore:
    def __init__(self, pit, cache_dir: Path | None = None):
        self.pit = pit
        self.cache_dir = cache_dir or config.data_dir() / "docs_cache"
        self._mem: dict[str, Document] = {}

    def open(self, key: str) -> Document:
        m = KEY.match(key or "")
        if not m:
            raise ValueError("document key must be '<cik>/<accession>/<file name>'")
        cik, accession, name = int(m.group(1)), m.group(2), m.group(3)
        raw = None
        path = self.cache_dir / accession / f"{name}.json"
        if key in self._mem:
            self.pit._check(cik, accession)        # the rule holds for cached documents too
            return self._mem[key]
        if path.exists():
            self.pit._check(cik, accession)
            doc = Document.from_json(json.loads(path.read_text(encoding="utf-8")))
        else:
            try:
                raw = self.pit.raw(cik, accession, name)
            except urllib.error.HTTPError as ex:
                if ex.code == 404:
                    raise ValueError(f"no document named {name!r} in filing {accession}") from None
                raise
            doc = parse_html(raw, key)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(doc.to_json()), encoding="utf-8")
        self._mem[key] = doc
        return doc


# ------------------------------------------------------------------------------------ tools
def _page(items: list, offset: int, limit: int, render) -> dict:
    out, used, i = [], 0, offset
    while i < len(items) and len(out) < limit:
        r = render(items[i])
        size = len(json.dumps(r))
        if out and used + size > MAX_CHARS:
            break
        out.append(r)
        used += size
        i += 1
    return {"total": len(items), "offset": offset, "returned": len(out),
            "next_offset": i if i < len(items) else None, "items": out}


def sections(doc: Document) -> dict:
    counts = {}
    for s in doc.sentences:
        counts[s["section"]] = counts.get(s["section"], 0) + 1
    tcounts = {}
    for t in doc.tables:
        tcounts[t.section] = tcounts.get(t.section, 0) + 1
    rows = [{"id": None, "text": "(before the first heading)", "sentences": counts.get(None, 0),
             "tables": tcounts.get(None, 0)}] if counts.get(None) or tcounts.get(None) else []
    rows += [{"id": h["id"], "text": h["text"], "sentences": counts.get(h["id"], 0), "tables": tcounts.get(h["id"], 0)}
             for h in doc.headings]
    return {"key": doc.key, "title": doc.title, "sentences": len(doc.sentences), "tables": len(doc.tables),
            "sections": rows}


def sentences(doc: Document, section: str | None = None, offset: int = 0, limit: int = DEFAULT_LIMIT) -> dict:
    items = doc.sentences if section is None else [s for s in doc.sentences if s["section"] == section]
    return _page(items, offset, limit, lambda s: {"id": s["id"], "text": s["text"]})


def tables(doc: Document, offset: int = 0, limit: int = 10, max_rows: int = 12) -> dict:
    """Tables with their first rows; `span(doc, "t3")` returns a whole table."""
    def render(t):
        rows = [{"id": f"{t.id}.r{i}", "cells": r} for i, r in enumerate(t.rows[:max_rows])]
        return {"id": t.id, "caption": t.caption, "n_rows": len(t.rows), "rows": rows,
                "truncated": len(t.rows) > max_rows}
    return _page(doc.tables, offset, limit, render)


def _terms(query: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9][a-z0-9.%$,/-]*", query.lower()) if len(t) > 1 or t.isdigit()]


def search(doc: Document, query: str, limit: int = 10) -> dict:
    """Sentences and table rows ranked by how many query terms they contain (whole phrase first).
    Deterministic and explainable; it narrows a 100-page indenture to the few places worth reading."""
    terms = _terms(query)
    phrase = " ".join(query.lower().split())
    if not terms:
        return {"query": query, "total": 0, "items": []}
    cands = [(s["id"], s["text"]) for s in doc.sentences]
    for t in doc.tables:
        cands += [(f"{t.id}.r{i}", " | ".join(r)) for i, r in enumerate(t.rows)]
    scored = []
    for order, (cid, text) in enumerate(cands):
        low = text.lower()
        hits = sum(1 for t in set(terms) if t in low)
        if not hits:
            continue
        score = hits + (len(terms) if phrase in low else 0)
        scored.append((-score, order, cid, text))
    scored.sort()
    items = [{"id": cid, "score": -s, "text": text[:400]} for s, _, cid, text in scored[:limit]]
    return {"query": query, "total": len(scored), "items": items}


def span(doc: Document, sid: str) -> dict:
    """The exact text behind an id — what code parses a number from, and what a citation shows."""
    m = re.fullmatch(r"t(\d+)(?:\.r(\d+)(?:\.c(\d+))?)?", sid or "")
    if m:
        t = next((t for t in doc.tables if t.id == f"t{m.group(1)}"), None)
        if t is None:
            raise KeyError(sid)
        if m.group(2) is None:
            return {"id": sid, "kind": "table", "caption": t.caption,
                    "rows": [{"id": f"{t.id}.r{i}", "cells": r} for i, r in enumerate(t.rows)]}
        r = int(m.group(2))
        if r >= len(t.rows):
            raise KeyError(sid)
        if m.group(3) is None:
            return {"id": sid, "kind": "row", "cells": t.rows[r], "text": " | ".join(t.rows[r])}
        c = int(m.group(3))
        if c >= len(t.rows[r]):
            raise KeyError(sid)
        return {"id": sid, "kind": "cell", "text": t.rows[r][c], "row": t.rows[r]}
    for s in doc.sentences:
        if s["id"] == sid:
            return {"id": sid, "kind": "sentence", "section": s["section"], "text": s["text"]}
    for h in doc.headings:
        if h["id"] == sid:
            return {"id": sid, "kind": "heading", "text": h["text"]}
    raise KeyError(sid)
