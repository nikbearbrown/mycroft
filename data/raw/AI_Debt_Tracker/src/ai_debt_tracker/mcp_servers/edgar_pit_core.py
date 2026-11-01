"""Point-in-time EDGAR: the agent's only window onto SEC filings, and the place look-ahead is refused.

DESIGN.md P11: the agent must never see the report it is graded on, or anything filed after it.
This module is that rule as code, kept apart from the MCP binding (`edgar_pit.py`) so it can be
tested without a server:

* Started with an `as_of` cut-off (EDGAR acceptance time, **exclusive**) and an optional set of
  excluded accessions (the episode's target report).
* `timeline` only lists filings accepted before the cut-off. It does not say how many it held
  back — a count of later filings would itself leak the future.
* `exhibits` and `fetch` **refuse** (raise `Refused`) any accession that is unknown for the
  company, accepted at or after the cut-off, or excluded. Fail closed: an accession we cannot
  date is treated as the future.
* Every call, allowed or refused, is appended to a JSONL access log, so a backtest can prove
  afterwards what the agent did and did not read.

Times (P29). EDGAR's `acceptanceDateTime` is not a stable clock: between 18 and 23 October 2026
the submissions index moved 43 of the 495 episode targets (9 filers) by 4–5 hours, consistent with
a switch from US Eastern time to UTC for some filers. Two rules make the cut-off immune to that:

* **Pin the cut-off to the target report, not to a timestamp.** `for_episode(cik, target)` reads
  the target's acceptance time from the live index when the server starts, so the cut-off and the
  filings it is compared with always come from the same snapshot of the same clock. A timestamp
  written in a manifest is kept for people to read, never used to enforce.
* **A safety margin on the cut-off day.** A filing from an earlier filing date is visible; a
  filing dated the same day as the cut-off is visible only if accepted at least `margin_hours`
  (default 5, the largest shift seen) before it. If one filer's filings mix two clocks, nothing
  accepted after the target can slip in; the cost is hiding a same-day filing now and then.
"""

from __future__ import annotations

import html
import json
import re
import threading
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .. import config
from ..edgar import ARCHIVE, FilingRef, load_filings, normalise_time  # noqa: F401 (re-exported)
from ..sec import SecClient

ACCESSION = re.compile(r"^\d{10}-\d{2}-\d{6}$")
DOC_NAME = re.compile(r"^[\w.-]+$")
DEFAULT_MAX_CHARS = 20_000


class Refused(PermissionError):
    """A request the point-in-time rule does not allow. The message says why, never what."""


def html_to_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|li|h\d|table)>", "\n", raw)
    raw = re.sub(r"(?i)</t[dh]>", " | ", raw)
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw)).replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()


class PointInTimeEdgar:
    def __init__(self, as_of: str, exclude: set[str] | None = None, client: SecClient | None = None,
                 log_path: Path | None = None, cutoff_date: str | None = None, margin_hours: float = 5.0):
        self.as_of = normalise_time(as_of)
        self.cutoff_date = cutoff_date or self.as_of[:10]
        self.margin_hours = margin_hours
        self._same_day_limit = (datetime.fromisoformat(self.as_of) - timedelta(hours=margin_hours)).isoformat()
        self.exclude = set(exclude or ())
        self.client = client or SecClient()
        self.log_path = log_path or config.data_dir() / "logs" / "edgar_pit_access.jsonl"
        self._index: dict[int, dict[str, FilingRef]] = {}
        self._lock = threading.Lock()

    @classmethod
    def for_episode(cls, cik: int, target_accession: str, client: SecClient | None = None,
                    log_path: Path | None = None, margin_hours: float = 5.0) -> "PointInTimeEdgar":
        """The cut-off of an episode: the target report's acceptance time in the live index."""
        client = client or SecClient()
        refs = load_filings(client, cik)
        if target_accession not in refs:
            raise Refused("target report is not in this company's EDGAR index")
        t = refs[target_accession]
        pit = cls(t.accepted, {target_accession}, client, log_path, cutoff_date=t.filing_date, margin_hours=margin_hours)
        pit._index[int(cik)] = refs
        return pit

    # ---- the rule ---------------------------------------------------------------------------
    def visible(self, ref: FilingRef) -> bool:
        if ref.accession in self.exclude or ref.accepted >= self.as_of:
            return False
        if ref.filing_date < self.cutoff_date:
            return True
        return ref.filing_date == self.cutoff_date and ref.accepted < self._same_day_limit

    def _check(self, cik: int, accession: str) -> FilingRef:
        if not ACCESSION.match(accession or ""):
            raise Refused("malformed accession number")
        ref = self.index(cik).get(accession)
        if ref is None:
            raise Refused("accession is not a filing of this company (or cannot be dated)")
        if accession in self.exclude:
            raise Refused("this filing is withheld for this episode")
        if ref.accepted >= self.as_of or ref.filing_date > self.cutoff_date:
            raise Refused("filing accepted at or after the cut-off")
        if not self.visible(ref):
            raise Refused("filed on the cut-off day too close to the cut-off to be sure it came first")
        return ref

    # ---- index of a company's filings -------------------------------------------------------
    def index(self, cik: int) -> dict[str, FilingRef]:
        cik = int(cik)
        if cik not in self._index:
            self._index[cik] = load_filings(self.client, cik)
        return self._index[cik]

    # ---- tools ------------------------------------------------------------------------------
    def timeline(self, cik: int, start: str, end: str, forms: list[str] | None = None) -> list[dict]:
        """Filings with filing date in [start, end] that were accepted before the cut-off."""
        try:
            rows = [asdict(r) for r in sorted(self.index(cik).values(), key=lambda r: r.accepted)
                    if self.visible(r) and start <= r.filing_date <= end and (not forms or r.form in forms)]
        except Exception as ex:
            self._log("timeline", {"cik": cik, "start": start, "end": end, "forms": forms}, "error", str(ex))
            raise
        self._log("timeline", {"cik": cik, "start": start, "end": end, "forms": forms}, "ok", n=len(rows))
        return rows

    def exhibits(self, cik: int, accession: str) -> list[dict]:
        """The documents in a filing: sequence, description, file name, type (e.g. EX-99.1), size."""
        args = {"cik": cik, "accession": accession}
        try:
            self._check(cik, accession)
        except Refused as ex:
            self._log("exhibits", args, "refused", str(ex))
            raise
        url = ARCHIVE.format(cik=int(cik), acc_nodash=accession.replace("-", "")) + f"{accession}-index.htm"
        page = self.client.get(url).decode("utf-8", "ignore")
        docs = []
        for row in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", page):
            cells = [html_to_text(c) for c in re.findall(r"(?is)<td[^>]*>(.*?)</td>", row)]
            link = re.search(r'href="[^"]*/([^/"]+)"', row)
            if len(cells) >= 5 and link:
                docs.append({"seq": cells[0], "description": cells[1], "document": link.group(1).split("?")[0],
                             "type": cells[3], "size": cells[4]})
        self._log("exhibits", args, "ok", n=len(docs))
        return docs

    def raw(self, cik: int, accession: str, doc: str) -> bytes:
        """One document's original bytes, under the same rule and log as `fetch`. For the `docs`
        server, which needs the HTML itself to keep tables as tables (Week 3)."""
        args = {"cik": cik, "accession": accession, "doc": doc}
        try:
            self._check(cik, accession)
            if not DOC_NAME.match(doc or ""):
                raise Refused("document name must be a plain file name from exhibits()")
        except Refused as ex:
            self._log("raw", args, "refused", str(ex))
            raise
        body = self.client.get(ARCHIVE.format(cik=int(cik), acc_nodash=accession.replace("-", "")) + doc)
        self._log("raw", args, "ok", n=len(body))
        return body

    def fetch(self, cik: int, accession: str, doc: str, offset: int = 0, max_chars: int = DEFAULT_MAX_CHARS) -> dict:
        """One document as plain text, paged: `text` holds chars [offset, offset+max_chars)."""
        args = {"cik": cik, "accession": accession, "doc": doc, "offset": offset}
        try:
            self._check(cik, accession)
            if not DOC_NAME.match(doc or ""):
                raise Refused("document name must be a plain file name from exhibits()")
        except Refused as ex:
            self._log("fetch", args, "refused", str(ex))
            raise
        raw = self.client.get(ARCHIVE.format(cik=int(cik), acc_nodash=accession.replace("-", "")) + doc)
        text = raw.decode("utf-8", "ignore")
        if doc.lower().endswith((".htm", ".html", ".xml")) or "<html" in text[:2000].lower():
            text = html_to_text(text)
        offset = max(0, int(offset))
        chunk = text[offset: offset + max_chars]
        self._log("fetch", args, "ok", n=len(chunk))
        return {"accession": accession, "document": doc, "offset": offset, "total_chars": len(text),
                "next_offset": offset + len(chunk) if offset + len(chunk) < len(text) else None, "text": chunk}

    # ---- audit trail ------------------------------------------------------------------------
    def _log(self, tool: str, args: dict, outcome: str, reason: str = "", n: int | None = None) -> None:
        rec = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "as_of": self.as_of, "tool": tool,
               "args": args, "outcome": outcome}
        if reason:
            rec["reason"] = reason
        if n is not None:
            rec["n"] = n
        with self._lock:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec) + "\n")
