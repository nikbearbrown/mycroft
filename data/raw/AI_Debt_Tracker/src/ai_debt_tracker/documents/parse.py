"""Turn an SEC filing's HTML into addressable pieces: headings, sentences and table cells.

DESIGN.md §7.1 rule 1: the AI never types a number — it points at a sentence or a cell, and code
reads the number from what it points at. That needs every sentence and cell of a filing to have a
stable id. This module is the parser behind the `docs` MCP server (week 3):

    h<n>          a heading (section)              "h3"
    s<n>          a sentence                       "s41"
    t<n>          a table                          "t2"
    t<n>.r<i>     a table row                      "t2.r3"
    t<n>.r<i>.c<j> a table cell                    "t2.r3.c1"

Ids follow document order and are deterministic, so a citation made today resolves to the same
text tomorrow. Parsing is plain code (stdlib `html.parser`); nothing here is a model.

Things real filings do that this handles, each from a document read in weeks 1–2:
* inline XBRL wraps every number in `ix:` tags and carries a hidden `ix:header` full of contexts —
  the header (and anything `display:none`) is skipped, the inline tags are transparent;
* tables split one value across cells (`$` | `1,250` | `%`) — currency and percent cells are merged
  into their neighbours, empty cells dropped (the convention `scripts/handcheck.py` validated);
* sentence ends are not every full stop: "$700.0 million", "U.S. Bank", "Inc.", "No. 333-275203",
  "Sept. 15" and initials do not end a sentence (a naive split cut "$700.0 million" in Week 2).
"""

from __future__ import annotations

import html
import re
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser

BLOCK_TAGS = {"p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article",
              "header", "footer", "blockquote", "center", "pre", "hr", "dt", "dd"}
SKIP_TAGS = {"script", "style", "ix:header", "head", "title"}
VOID_TAGS = {"br", "hr", "img", "meta", "link", "input", "col", "area", "base", "wbr", "source"}
ABBREVIATIONS = {"inc", "corp", "co", "ltd", "llc", "l.p", "lp", "n.a", "no", "nos", "u.s", "u.k", "s.a", "b.v", "n.v",
                 "plc", "e.g", "i.e", "approx", "mr", "ms", "mrs", "dr", "st", "vs", "etc", "jan", "feb", "mar", "apr",
                 "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec", "fig", "sec", "art", "para", "p.m", "a.m",
                 "par", "pty", "s.r.l", "gmbh", "ag", "k.k", "a.g", "bros", "assn", "ave", "dept", "est", "govt",
                 "intl", "jr", "sr", "mfg", "natl", "u.s.a"}
MERGE_CELLS = {"$", "%", "€", "£", "¥", ")", "(", "%)"}


@dataclass
class Table:
    id: str
    section: str | None
    rows: list[list[str]]
    caption: str | None = None     # the nearest preceding heading or sentence, for orientation


@dataclass
class Document:
    key: str
    title: str | None = None
    headings: list[dict] = field(default_factory=list)    # {"id", "text", "order"}
    sentences: list[dict] = field(default_factory=list)   # {"id", "section", "text", "order"}
    tables: list[Table] = field(default_factory=list)

    def to_json(self) -> dict:
        return {"key": self.key, "title": self.title, "headings": self.headings, "sentences": self.sentences,
                "tables": [asdict(t) for t in self.tables]}

    @classmethod
    def from_json(cls, d: dict) -> "Document":
        return cls(d["key"], d.get("title"), d["headings"], d["sentences"], [Table(**t) for t in d["tables"]])


# ------------------------------------------------------------------------------------ sentences
_SPLIT = re.compile(r"(?<=[.!?])[\"'”’)\]]*\s+(?=[\"“'(\[]?[A-Z0-9•●])")


def split_sentences(text: str) -> list[str]:
    """Split on sentence-final punctuation followed by a capital, unless the word before the full
    stop is an abbreviation, an initial, or a number's decimal point."""
    text = " ".join(text.split())
    if not text:
        return []
    out, start = [], 0
    for m in _SPLIT.finditer(text):
        before = text[start:m.start()].rstrip("\"'”’)]")
        last = before.rsplit(" ", 1)[-1].lower().rstrip(".")
        if before.endswith("."):
            if last in ABBREVIATIONS or re.fullmatch(r"[a-z]", last) or re.fullmatch(r"([a-z]\.)+[a-z]", last):
                continue
        piece = text[start:m.start()].strip()
        if piece:
            out.append(piece)
        start = m.end()
    tail = text[start:].strip()
    if tail:
        out.append(tail)
    return out


def looks_like_heading(text: str, emphasised: bool) -> bool:
    words = text.split()
    if not words or len(words) > 14 or len(text) > 120:
        return False
    if re.match(r"^item\s+\d{1,2}\.\d{2}\b", text, re.I):
        return True
    if text.rstrip().endswith((".", ",", ";")) and not re.match(r"^\(?[a-z0-9]{1,3}[.)]\s", text, re.I):
        return False
    letters = [c for c in text if c.isalpha()]
    upper = letters and sum(c.isupper() for c in letters) / len(letters) > 0.8 and len(letters) > 3
    return bool(emphasised or upper)


# ------------------------------------------------------------------------------------ the parser
class _Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks: list[tuple] = []          # ("para", text, emphasised) | ("table", rows)
        self._buf: list[str] = []
        self._emph_chars = 0
        self._skip = 0
        self._stack: list[tuple[str, bool, bool]] = []   # (tag, skipping, emphasised)
        self._tables: list[dict] = []          # nested table stack: {"rows": [], "row": None, "cell": None}
        self.title = None
        self._in_title = False

    # -- helpers
    def _emph(self) -> bool:
        return any(e for _, _, e in self._stack)

    def _flush(self):
        text = " ".join("".join(self._buf).split())
        if text:
            emphasised = self._emph_chars >= 0.8 * len(text.replace(" ", ""))
            self.blocks.append(("para", text, emphasised))
        self._buf, self._emph_chars = [], 0

    # -- events
    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        a = {k.lower(): (v or "") for k, v in attrs}
        style = a.get("style", "").replace(" ", "").lower()
        hidden = "display:none" in style
        emph = tag in ("b", "strong", "u") or "font-weight:bold" in style or "font-weight:700" in style \
            or "text-decoration:underline" in style
        if tag == "title":
            self._in_title = True
        skipping = tag in SKIP_TAGS or hidden
        if tag not in VOID_TAGS:
            self._stack.append((tag, skipping, emph))
        if skipping:
            self._skip += 1
            return
        if self._skip:
            return
        if tag == "table":
            if not self._tables:
                self._flush()
            self._tables.append({"rows": [], "row": None, "cell": None})
        elif self._tables and tag == "tr":
            self._tables[-1]["row"] = []
        elif self._tables and tag in ("td", "th"):
            self._tables[-1]["cell"] = []
        elif tag in BLOCK_TAGS:
            if self._tables and self._tables[-1]["cell"] is not None:
                self._tables[-1]["cell"].append(" ")
            elif not self._tables:
                self._flush()

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        # pop to the matching open tag (HTML in filings is not always well nested)
        idx = next((i for i in range(len(self._stack) - 1, -1, -1) if self._stack[i][0] == tag), None)
        if idx is None:
            return
        popped = self._stack[idx:]
        del self._stack[idx:]
        self._skip -= sum(1 for _, s, _ in popped if s)
        if any(s for _, s, _ in popped):
            return
        if self._skip:
            return
        if self._tables:
            t = self._tables[-1]
            if tag in ("td", "th") and t["cell"] is not None:
                if t["row"] is None:
                    t["row"] = []
                t["row"].append(" ".join("".join(t["cell"]).split()))
                t["cell"] = None
            elif tag == "tr" and t["row"] is not None:
                t["rows"].append(t["row"])
                t["row"] = None
            elif tag == "table":
                done = self._tables.pop()
                if self._tables:   # a nested table becomes text in the outer cell
                    outer = self._tables[-1]
                    flat = " ".join(" ".join(r) for r in done["rows"])
                    if outer["cell"] is not None:
                        outer["cell"].append(" " + flat + " ")
                else:
                    self.blocks.append(("table", done["rows"]))
            elif tag in BLOCK_TAGS and t["cell"] is not None:
                t["cell"].append(" ")
        elif tag in BLOCK_TAGS:
            self._flush()

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_data(self, data):
        if self._in_title and self.title is None and data.strip():
            self.title = " ".join(data.split())
        if self._skip:
            return
        data = data.replace("\xa0", " ").replace("​", "")
        if self._tables:
            t = self._tables[-1]
            if t["cell"] is not None:
                t["cell"].append(data)
            return
        self._buf.append(data)
        if self._emph():
            self._emph_chars += len(data.replace(" ", "").replace("\n", ""))

    def close(self):
        super().close()
        while self._tables:
            done = self._tables.pop()
            if not self._tables:
                self.blocks.append(("table", done["rows"]))
        self._flush()


def clean_rows(rows: list[list[str]]) -> list[list[str]]:
    """Drop empty cells and rows; glue '$' / '%' / ')' cells to the number they belong to."""
    out = []
    for row in rows:
        cells = [c.strip() for c in row if c and c.strip() and c.strip() != "​"]
        merged: list[str] = []
        for c in cells:
            if c in ("$", "€", "£", "¥", "(") and merged is not None:
                merged.append(c)
                continue
            if merged and merged[-1] in ("$", "€", "£", "¥", "("):
                merged[-1] = merged[-1] + c
                continue
            if c in ("%", ")", "%)") and merged:
                merged[-1] = merged[-1] + c
                continue
            merged.append(c)
        if merged:
            out.append(merged)
    return out


def parse_html(raw: str | bytes, key: str) -> Document:
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", "ignore")
    p = _Parser()
    p.feed(raw)
    p.close()
    doc = Document(key=key, title=p.title)
    section, order, last_text = None, 0, None
    for block in p.blocks:
        if block[0] == "para":
            _, text, emphasised = block
            text = html.unescape(text)
            if looks_like_heading(text, emphasised):
                section = f"h{len(doc.headings)}"
                doc.headings.append({"id": section, "text": text, "order": order})
                order += 1
                last_text = text
                continue
            for s in split_sentences(text):
                doc.sentences.append({"id": f"s{len(doc.sentences)}", "section": section, "text": s, "order": order})
                order += 1
                last_text = s
        else:
            rows = clean_rows(block[1])
            if not rows:
                continue
            doc.tables.append(Table(id=f"t{len(doc.tables)}", section=section, rows=rows,
                                    caption=(last_text or "")[:160] or None))
            order += 1
    return doc
