"""The `timeline` node (DESIGN.md §7.3): every filing in an episode's window that could carry debt news.

Plain code, no model. For one company (and its issuing subsidiaries, P12), it lists the filings of
the four document families the design names — 8-K current reports, 424B2/424B5 prospectus
supplements, FWP final term sheets, and the exhibits inside them — accepted before the cut-off, as
`edgar_pit` sees them. Deciding which are about debt is the next node's job (`triage`); the timeline
only refuses to miss anything.

Big issuers announce bonds without an 8-K (P1: Alphabet filed 0 item-2.03 8-Ks but 28 prospectus
supplements), and some debt is sold by a subsidiary under its own filer id (Equinix Europe 2
Financing Corporation, Vistra Operations, Digital Realty Trust L.P.), so both are in scope.

`pit` is anything with the `edgar_pit` tool surface — `timeline(cik, start, end, forms)` and
`exhibits(cik, accession)` — the in-process `PointInTimeEdgar` now, the MCP server in week 5.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
FAMILIES = {"8-K": "8-K", "8-K/A": "8-K", "424B2": "424B", "424B3": "424B", "424B5": "424B", "FWP": "FWP"}
# exhibits worth reading: press releases, indentures and note forms, credit agreements, underwriting
EXHIBIT_PREFIXES = ("EX-99", "EX-4", "EX-10", "EX-1.")


@dataclass
class Candidate:
    cik: int                       # the filer (the company or one of its issuing subsidiaries)
    company_cik: int               # the universe company the episode is about
    accession: str
    form: str
    family: str
    filing_date: str
    accepted: str
    items: list[str]
    primary_document: str
    documents: list[dict] = field(default_factory=list)   # {"document", "type", "description"}

    def keys(self) -> list[str]:
        """`docs` keys of the documents worth reading, main document first."""
        return [f"{self.cik}/{self.accession}/{d['document']}" for d in self.documents]


def issuing_subsidiaries(company_cik: int, universe_path: Path | None = None) -> list[int]:
    u = json.loads((universe_path or ROOT / "universe_v1.json").read_text(encoding="utf-8"))
    for c in u["companies"]:
        if c["cik"] == company_cik:
            return [s["cik"] for s in c.get("issuing_subsidiaries", [])]
    return []


def readable_documents(exhibits: list[dict], form: str, primary: str) -> list[dict]:
    """The main document plus the exhibits a reader could need; XBRL, images and the full
    submission text file are left out."""
    out = []
    for d in exhibits:
        name, t = d["document"], (d.get("type") or "").upper()
        if not name.lower().endswith((".htm", ".html", ".txt")) or name.endswith(".txt") and t == "":
            continue
        main = name == primary or t == form or (form.startswith("424B") and t.startswith("424B"))
        if main or t.startswith(EXHIBIT_PREFIXES):
            out.append({"document": name, "type": t or form, "description": d.get("description", "")})
    out.sort(key=lambda d: (d["document"] != primary, d["type"]))
    return out


def timeline(pit, company_cik: int, start: str, end: str, subsidiaries: list[int] | None = None,
             with_documents: bool = True) -> list[Candidate]:
    """Filings with filing date in [start, end] of the four families, oldest first."""
    ciks = [company_cik] + [c for c in (subsidiaries or []) if c != company_cik]
    seen, out = set(), []
    for cik in ciks:
        try:
            rows = pit.timeline(cik, start, end, sorted(FAMILIES))
        except Exception:  # noqa: BLE001 — a subsidiary with no EDGAR index is skipped, not fatal
            if cik == company_cik:
                raise
            continue
        for f in rows:
            if f["accession"] in seen:   # co-filed by parent and subsidiary: one candidate
                continue
            seen.add(f["accession"])
            c = Candidate(cik=cik, company_cik=company_cik, accession=f["accession"], form=f["form"],
                          family=FAMILIES[f["form"]], filing_date=f["filing_date"], accepted=f["accepted"],
                          items=[i for i in (f.get("items") or "").split(",") if i],
                          primary_document=f.get("primary_document", ""))
            if with_documents:
                c.documents = readable_documents(pit.exhibits(cik, f["accession"]), f["form"], c.primary_document)
            out.append(c)
    out.sort(key=lambda c: (c.accepted, c.accession))
    return out


def drop_duplicate_documents(rows: list[dict], text_of) -> list[dict]:
    """P45: one document filed under several accessions. Dell's October 2024 pricing term sheet was filed five
    times, once under each co-issuer's CIK, so de-duplicating by accession keeps every copy (Week 4 fresh triage
    set). Filings on the same day, of the same form, whose main document has the same file name *and* the
    same text are one document: the first is kept and lists the others in `also_filed_as`. The same file name
    alone is not enough — `form8-k.htm` is used by many filers for different news.

    `rows` are candidates as dicts (`to_json`), oldest first; `text_of(row)` returns the start of its main
    document's text, or "" when it cannot be read (then nothing is dropped)."""
    kept, first = [], {}
    for r in rows:
        key = (r["filing_date"], r["form"], r["primary_document"])
        f = first.get(key)
        if f is not None:
            a, b = " ".join(text_of(f).split()), " ".join(text_of(r).split())
            if a and a == b:
                f.setdefault("also_filed_as", []).append({"cik": r["cik"], "accession": r["accession"]})
                continue
        else:
            first[key] = r
        kept.append(r)
    return kept


def to_json(cands: list[Candidate]) -> list[dict]:
    return [asdict(c) for c in cands]
