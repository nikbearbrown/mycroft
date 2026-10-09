"""The Reg S-X 12-12 restricted-securities footnote, out of N-CSR and N-CSRS.

`plan.md` week 9: "N-CSR / N-CSRS restricted-securities footnote (Reg S-X
12-12), which requires acquisition date and cost per restricted position --
entry price and round timing that N-PORT lacks entirely."

That is the whole reason this lane exists. N-PORT says what a position is worth
on a period end. It never says when the fund bought it or what it paid. The
footnote says both, and it is the only routinely filed place that does.

--------------------------------------------------------------------------
Four filers, four layouts, one parser
--------------------------------------------------------------------------
There is no prescribed format -- Reg S-X names the required contents, not the
columns -- and the four large holders in this universe each write it
differently:

    Baron        Name of Issuer | Acquisition Date(s) | Value
                 cost given once per fund, not per position
    Fidelity     Security | Acquisition Date | Acquisition Cost ($)
                 per position, security name carries the series
    Neuberger    Restricted Security | Acquisition Date(s) | Acquisition Cost
                 | Value | Percentage of Net Assets
    Lincoln      Investment | Date of Acquisition | Cost | Value

Writing four parsers would mean a fifth filer silently returns nothing. So the
parser reads the **header row** and maps columns by what they are called. A
layout it has never seen works if its header is labelled; a layout whose header
it cannot read is recorded as a parse failure in `ncsr_filings`, never as zero
rows.

--------------------------------------------------------------------------
Why no HTML library
--------------------------------------------------------------------------
These documents run to 95 MB. Building a DOM for one costs about a gigabyte,
and the footnote is a few kilobytes of it. So the document is sliced to the
footnote region by a cheap text scan first, and only that slice is parsed. The
regex table reader below is adequate *because* it only ever sees filing-agent
HTML that has already been narrowed to one table -- it is not a general HTML
parser and should not be used as one.

--------------------------------------------------------------------------
Two things the format forces into the schema
--------------------------------------------------------------------------
1. **Dates are often ranges.** "11/15/2017-8/4/2020" means the position was
   built across that span. Both ends are stored. Collapsing to one would
   invent a precision the filing does not have.
2. **Cost is not always per position.** Baron reports one cost for all
   restricted securities in a fund and says so: "See Portfolios of Investments
   for cost of individual securities." `cost_basis_scope` records which kind
   of number this is, so a fund total is never read as an entry price.
"""

from __future__ import annotations

import html as html_mod
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.ingest.universe import UNIVERSE_PATTERNS, WATCHLIST_PATTERNS  # noqa: E402

FORMS = ("N-CSR", "N-CSRS")

_PATTERNS = [
    (canonical, pattern.strip("%"))
    for group in (UNIVERSE_PATTERNS, WATCHLIST_PATTERNS)
    for canonical, patterns in group.items()
    for pattern in patterns
]

# What a header cell has to say for the parser to know what the column holds.
# Order matters within COST/VALUE: "Acquisition Cost" must not be read as a
# value column, and "Value as of 2/28/2026" must not be read as a cost.
_H_NAME = re.compile(r"(securit|issuer|investment|name|description)", re.I)
_H_DATE = re.compile(r"(acquisition\s*date|date\s*(of\s*)?acquisition|"
                     r"acquisition\s*date\(s\))", re.I)
_H_COST = re.compile(r"cost", re.I)
_H_PCT = re.compile(r"(percentage|%\s*of\s*net|of\s*net\s*assets)", re.I)
_H_VALUE = re.compile(r"value", re.I)

_TABLE = re.compile(r"<table\b.*?</table>", re.I | re.S)
_ROW = re.compile(r"<tr\b.*?</tr>", re.I | re.S)
_CELL = re.compile(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", re.I | re.S)
_TAG = re.compile(r"<[^>]+>")

_DATE = r"\d{1,2}/\d{1,2}/\d{2,4}"
_DATE_RANGE = re.compile(rf"({_DATE})\s*(?:[-‐-―]\s*({_DATE}))?\s*$")
_MONEY = re.compile(r"^\(?\$?\s*-?[\d,]+(?:\.\d+)?\s*\)?$")

# The footnote can be titled several ways. The scan looks for any of these and
# keeps the widest window around the hits, because a registrant with twelve
# series writes the note twelve times.
_ANCHORS = re.compile(
    r"(restricted\s+securit|acquisition\s*date|date\s*of\s*acquisition)", re.I)


def clean(fragment: str) -> str:
    """One HTML cell reduced to its text."""
    text = _TAG.sub(" ", fragment)
    text = html_mod.unescape(text)
    # Zero-width characters are used as row separators by at least one filing
    # agent; left in, they weld a value onto the next security's name.
    for ch in (" ", " ", " ", "​", "‌", "‍",
               "﻿", " ", " "):
        text = text.replace(ch, " ")
    return re.sub(r"\s+", " ", text).strip()


def company_for(name: str) -> str | None:
    upper = (name or "").upper()
    for canonical, pattern in _PATTERNS:
        if pattern in upper:
            return canonical
    return None


def _money(text: str):
    if not text or not _MONEY.match(text.strip()):
        return None
    negative = text.strip().startswith("(") or text.strip().startswith("-")
    digits = re.sub(r"[^\d.]", "", text)
    if not digits:
        return None
    try:
        value = float(digits)
    except ValueError:
        return None
    return -value if negative else value


def _pct(text: str):
    if not text:
        return None
    match = re.search(r"(-?[\d.]+)\s*%?", text)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _date(text: str):
    for fmt in ("%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue
    return None


def slice_regions(document: str, window: int = 60_000) -> list[str]:
    """Windows of the document that might contain the footnote.

    A 95 MB filing is narrowed to a few hundred kilobytes before any table is
    read. Overlapping hits are merged so a table is never cut in half.
    """
    spans: list[list[int]] = []
    for match in _ANCHORS.finditer(document):
        start = max(0, match.start() - window // 3)
        end = min(len(document), match.end() + window)
        if spans and start <= spans[-1][1]:
            spans[-1][1] = max(spans[-1][1], end)
        else:
            spans.append([start, end])
    return [document[a:b] for a, b in spans]


def read_table(table_html: str) -> tuple[list[str], list[list[str]], list[list[str]]]:
    """Header cells, body rows, and whatever sat above the header.

    The rows above the header are not noise. Baron and Fidelity both put the
    series name there -- "Baron Partners Fund", "Fidelity Growth Company Fund"
    -- and without it a lot says which company was bought but not which fund
    bought it, which is half the fact.
    """
    rows = []
    for row_html in _ROW.findall(table_html):
        cells = [clean(c) for c in _CELL.findall(row_html)]
        if any(cells):
            rows.append(cells)
    if not rows:
        return [], [], []
    # The header is the first row that names a date column. Filing agents put
    # spacer rows and fund titles above it.
    for index, row in enumerate(rows):
        if any(_H_DATE.search(c or "") for c in row):
            return row, rows[index + 1:], rows[:index]
    return rows[0], rows[1:], []


# "(Cost $253,013,093)" -- Baron gives one cost for all restricted securities
# in a fund and points at the Schedule of Investments for per-position cost.
_FUND_COST = re.compile(r"\(\s*Cost\s*\$?\s*([\d,]+)", re.I)

# A fund title: a capitalised phrase ending in a fund word. Deliberately
# narrow -- a wrong fund name is worse than none, because it would attribute
# one series' entry price to another.
_FUND_TITLE = re.compile(
    r"\b((?:[A-Z][A-Za-z0-9&.'’\-]*\s+){1,7}"
    r"(?:Fund|Portfolio|Trust)\b)")

# Phrases that end in a fund word and name no fund.
_NOT_A_FUND = re.compile(
    r"^(the|each|a|an|this|other|such|central|underlying|acquired|affiliated|"
    r"total|net|see|notes to|statement of|schedule of)\b", re.I)


def fund_title(above: list[list[str]]) -> str | None:
    """The series name, taken only from the table's own heading rows.

    An earlier version also searched the running text before the table, and
    it produced a wrong answer rather than no answer. Fidelity's note is
    preceded by the sentence "each Fidelity Central Fund's financial
    statements ... are available on the SEC's website"; the last fund-shaped
    phrase before the table is therefore "Fidelity Central Fund", which is a
    real but entirely different vehicle. Every Anduril and Anthropic lot in
    that filing would have been filed under the wrong series.

    So prose is not a source. A title is read only where a filer puts one in
    the table structure, which Baron does and Fidelity, Lincoln and Neuberger
    do not. `restricted_lots.registrant` still says who filed; only the series
    within the registrant is unknown, and unknown is NULL.
    """
    for row in reversed(above):
        for cell in reversed([c for c in row if c]):
            for match in _FUND_TITLE.finditer(cell):
                candidate = match.group(1).strip()
                if _NOT_A_FUND.match(candidate) or len(candidate) < 8:
                    continue
                return candidate
    return None


def map_columns(header: list[str]) -> dict | None:
    """Which column is which, from what the header calls them."""
    columns: dict[str, int] = {}
    for index, cell in enumerate(header):
        text = cell or ""
        if not text:
            continue
        if "date" not in columns and _H_DATE.search(text):
            columns["date"] = index
        elif "cost" not in columns and _H_COST.search(text):
            columns["cost"] = index
        elif "pct" not in columns and _H_PCT.search(text):
            columns["pct"] = index
        elif "value" not in columns and _H_VALUE.search(text):
            columns["value"] = index
        elif "name" not in columns and _H_NAME.search(text):
            columns["name"] = index
    if "date" not in columns:
        return None
    columns.setdefault("name", 0)
    return columns


def parse_rows(rows: list[list[str]]) -> list[dict]:
    """Body rows of a restricted-securities table.

    Cells are frequently split across several `<td>`s -- a currency symbol in
    one, the digits in the next -- so a row is read by scanning for the date
    first and then taking the numbers to its right in header order, rather
    than trusting the column index against a ragged row.
    """
    out = []
    for cells in rows:
        joined = [c for c in cells if c]
        if not joined:
            continue
        name = joined[0]
        if not name or _DATE_RANGE.search(name):
            continue
        if re.match(r"^(total|subtotal)\b", name, re.I):
            continue

        date_index, dates = None, None
        for index, cell in enumerate(joined[1:], start=1):
            match = _DATE_RANGE.search(cell)
            if match:
                date_index, dates = index, match
                break
        if dates is None:
            continue

        numbers = [_money(c) for c in joined[date_index + 1:]]
        numbers = [n for n in numbers if n is not None]
        percents = [_pct(c) for c in joined[date_index + 1:] if "%" in c]

        first, last = dates.group(1), dates.group(2)
        out.append({
            "issuer_name_raw": name,
            "acquisition_date_raw": dates.group(0).strip(),
            "acquisition_date_first": _date(first),
            "acquisition_date_last": _date(last or first),
            "acquisition_date_is_range": bool(last),
            "_numbers": numbers,
            "_percents": percents,
        })
    return out


def assign_amounts(parsed: list[dict], columns: dict) -> list[dict]:
    """Attach cost and value using the order the header declared them in.

    Which number is the cost is a header question, not a magnitude question.
    An earlier version guessed "the larger number is the value", which is
    false for every position a fund is underwater on -- Lincoln's entire
    Russian book is carried at 0 against a cost of $16.3m.
    """
    order = sorted(
        (index, key) for key, index in columns.items() if key in ("cost", "value"))
    keys = [key for _, key in order]
    for row in parsed:
        numbers = row.pop("_numbers")
        percents = row.pop("_percents")
        for position, key in enumerate(keys):
            row[f"{key}_usd"] = numbers[position] if position < len(numbers) else None
        row.setdefault("cost_usd", None)
        row.setdefault("value_usd", None)
        row["pct_net_assets"] = percents[0] if percents else None
        row["cost_basis_scope"] = "position" if row["cost_usd"] is not None else "absent"
    return parsed


def parse_document(document: str, universe_only: bool = True) -> list[dict]:
    """Every restricted-securities lot in one filing."""
    lots, seen = [], set()
    for region in slice_regions(document):
        for match in _TABLE.finditer(region):
            table_html = match.group(0)
            header, rows, above = read_table(table_html)
            columns = map_columns(header)
            if not columns:
                continue
            parsed = assign_amounts(parse_rows(rows), columns)
            if not parsed:
                continue

            title = fund_title(above)
            # A fund-level cost total sits just after the table it belongs to.
            tail = clean(region[match.end():match.end() + 600])
            fund_cost = _FUND_COST.search(clean(table_html)) or _FUND_COST.search(tail)

            for row in parsed:
                company = company_for(row["issuer_name_raw"])
                if universe_only and company is None:
                    continue
                key = (row["issuer_name_raw"], row["acquisition_date_raw"],
                       row.get("cost_usd"), row.get("value_usd"), title)
                if key in seen:
                    continue
                seen.add(key)
                row["company_provisional"] = company
                row["fund_name"] = title
                if row["cost_usd"] is None and fund_cost:
                    # The filer DID disclose cost, just not at this
                    # granularity. Saying 'absent' would be false, and putting
                    # the fund total in cost_usd would be worse -- it would
                    # read as this position's entry price. So the scope says
                    # what happened and the amount stays NULL.
                    row["cost_basis_scope"] = "fund_total"
                lots.append(row)

    # The fifth layout carries no table, so it is parsed separately and
    # merged. Keyed the same way, so a filer that discloses both ways -- a
    # footnote table and an inline parenthetical for the same position --
    # contributes one lot, not two.
    for row in parse_inline(document, universe_only):
        key = (row["issuer_name_raw"], row["acquisition_date_raw"],
               row.get("cost_usd"), row.get("value_usd"), row.get("fund_name"))
        if key in seen:
            continue
        seen.add(key)
        lots.append(row)
    return lots


# --------------------------------------------------------------------------
# The fifth layout: no table at all
# --------------------------------------------------------------------------
# BlackRock satisfies Reg S-X 12-12 inside the Schedule of Investments line
# item rather than in a separate note:
#
#   Databricks, Inc., Series F, (Acquired 10/22/19, cost $3,030,010) (d)(g)(j)
#
# The first version of this module returned zero lots for every BlackRock
# filing and recorded "footnote text present but no universe lot parsed",
# which was true and useless -- there was no table to find because the
# disclosure is a parenthetical. BlackRock is one of the largest holders in
# this universe, so a lane that silently skips it is not a lane.
#
# Two-digit years here, and occasionally a range or a list of dates.
_ACQUIRED = re.compile(
    r"\(\s*Acquired\s+(?P<dates>\d{1,2}/\d{1,2}/\d{2,4}"
    r"(?:\s*(?:[-‐-―]|,|and)\s*\d{1,2}/\d{1,2}/\d{2,4})*)"
    r"\s*(?:,\s*cost\s*\$?\s*(?P<cost>[\d,]+(?:\.\d+)?))?\s*\)", re.I)

# Where the previous line item ended: its share count and value, run together.
# Splitting on this is what isolates one security's name, because the
# alternative -- stopping at the previous full stop -- cuts "Databricks, Inc.,
# Series F" down to "Series F". Every name in this universe contains a period.
_PREV_ITEM = re.compile(r"\d[\d,]*(?:\.\d+)?\s+[\d,]+(?:\.\d+)?\s")

# A Schedule of Investments restarts its column headings and its country or
# sector heading at every page break, and those land immediately before the
# first line item on the page. Left in, `issuer_name_raw` reads
# "Security Shares Shares Value United States (continued) Fanatics Holdings".
_SECTION_NOISE = re.compile(
    r"^.*(?:\(continued\)|Shares\s+Value|Value\s*\(?[a-z]?\)?|"
    r"—\s*[\d.]+\s*%|–\s*[\d.]+\s*%)\s*", re.I | re.S)


def _trim_section_header(name: str) -> str:
    """Drop a repeated page heading that precedes a line item."""
    trimmed = _SECTION_NOISE.sub("", name)
    if not re.search(r"[A-Za-z]{3}", trimmed):
        trimmed = name
    # A bare leading number is the tail of the previous line item's value,
    # left behind when the split lands mid-figure.
    return re.sub(r"^[\d,.]+\s+", "", trimmed).strip()


def parse_inline(document: str, universe_only: bool = True) -> list[dict]:
    """Lots disclosed as an "(Acquired ..., cost $...)" parenthetical."""
    flat = clean(document)
    lots, seen = [], set()
    for match in _ACQUIRED.finditer(flat):
        before = flat[max(0, match.start() - 200):match.start()]
        before = re.sub(r"[.…]{2,}", " ", before)          # dot leaders
        name = _PREV_ITEM.split(before)[-1]
        # Footnote markers "(d)(g)" belong to the previous item, not this name.
        name = re.sub(r"^(?:\s*\([a-z]{1,3}\))+", " ", name)
        name = _trim_section_header(name)
        name = name.strip(" ,.;")
        if len(name) < 3 or not re.search(r"[A-Za-z]{3}", name):
            continue
        company = company_for(name)
        if universe_only and company is None:
            continue

        dates = re.findall(_DATE, match.group("dates"))
        first, last = dates[0], dates[-1]
        cost = _money(match.group("cost") or "")
        key = (name, match.group("dates"), cost)
        if key in seen:
            continue
        seen.add(key)
        lots.append({
            "issuer_name_raw": name,
            "acquisition_date_raw": match.group("dates").strip(),
            "acquisition_date_first": _date(first),
            "acquisition_date_last": _date(last),
            "acquisition_date_is_range": len(dates) > 1,
            "cost_usd": cost,
            "value_usd": None,
            "pct_net_assets": None,
            "cost_basis_scope": "position" if cost is not None else "absent",
            "company_provisional": company,
            "fund_name": None,
        })
    return lots


def footnote_present(document: str) -> bool:
    """Does this filing disclose restricted securities in either shape?

    Tested against the *flattened* text, not the raw HTML. The inline form is
    split across tags in the source -- "(Acquired&#160;10/22/19,<span> cost
    $3,030,010)" -- so a raw-HTML search finds nothing, reports
    `footnote_found = False`, and in `load` that short-circuits the parse
    before the inline path runs. Every BlackRock filing was recorded as
    having no footnote for exactly that reason.
    """
    flat = clean(document)
    return bool(re.search(r"restricted\s+securit", flat, re.I)
                or _ACQUIRED.search(flat)
                or re.search(r"acquisition\s*date", flat, re.I))


# --------------------------------------------------------------------------
# Fetching. There is no bulk data set for N-CSR -- it is narrative HTML -- so
# this is the one lane in the project that reads EDGAR document by document.
# --------------------------------------------------------------------------

# plan.md: "Scope this to the top three companies by coverage; treat wider
# coverage as a stretch." Ninety-eight registrants hold one of those three, at
# 15-95 MB per filing, so fetching all of them is several gigabytes for a
# long tail that adds a lot or two each. Registrants are ranked by how many
# marks they account for and the ranking is stored with the result, so the
# cut-off is a visible parameter rather than a silent sample.
TOP_THREE = ("Databricks, Inc.",
             "Space Exploration Technologies Corp.",
             "Anduril Industries, Inc.")


def registrants(conn, companies=TOP_THREE, limit: int | None = None) -> list[dict]:
    """Registrant CIKs holding the named companies, heaviest first."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT f.cik,
                   min(f.family)                   AS family,
                   count(*)                        AS marks,
                   count(DISTINCT co.canonical_name) AS companies
              FROM marks m
              JOIN funds f      ON f.fund_id = m.fund_id
              JOIN companies co ON co.company_id = m.company_id
             WHERE co.canonical_name = ANY(%s)
             GROUP BY f.cik
             ORDER BY count(*) DESC
        """, (list(companies),))
        rows = [dict(zip([c[0] for c in cur.description], r)) for r in cur.fetchall()]
    return rows[:limit] if limit else rows


def list_filings(cik: str, session=None) -> list[dict]:
    """Every N-CSR / N-CSRS this registrant has on EDGAR, newest first."""
    import requests

    from src.ingest.download_bulk import throttle, user_agent

    throttle()
    get = (session or requests).get
    response = get(f"https://data.sec.gov/submissions/CIK{cik}.json",
                   headers={"User-Agent": user_agent()}, timeout=60)
    response.raise_for_status()
    payload = response.json()
    recent = payload.get("filings", {}).get("recent", {})
    out = []
    for form, filed, accession, document, report in zip(
            recent.get("form", []), recent.get("filingDate", []),
            recent.get("accessionNumber", []), recent.get("primaryDocument", []),
            recent.get("reportDate", [])):
        if form not in FORMS or not document:
            continue
        out.append({
            "cik": cik,
            "registrant": payload.get("name"),
            "form_type": form,
            "filed_date": filed or None,
            "accession": accession,
            "primary_document": document,
            "report_date": report or None,
            "source_url": (f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
                           f"{accession.replace('-', '')}/{document}"),
        })
    return out


def newest_per_form(filings: list[dict]) -> list[dict]:
    """The latest annual and the latest semi-annual.

    Two filings cover a whole year of the footnote. A registrant's older
    reports repeat most of the same lots with a stale value, so depth here
    buys far less than breadth across registrants.
    """
    chosen: dict[str, dict] = {}
    for filing in sorted(filings, key=lambda f: f["filed_date"] or "", reverse=True):
        chosen.setdefault(filing["form_type"], filing)
    return list(chosen.values())


def fetch_document(url: str, session=None) -> bytes:
    import requests

    from src.ingest.download_bulk import throttle, user_agent

    throttle()
    get = (session or requests).get
    response = get(url, headers={"User-Agent": user_agent()}, timeout=600)
    response.raise_for_status()
    return response.content


RECORD_FILING = """
INSERT INTO ncsr_filings (accession, cik, registrant, form_type, filed_date,
                          report_date, primary_document, source_url,
                          bytes_fetched, footnote_found, lots_parsed, parse_note)
VALUES (%(accession)s, %(cik)s, %(registrant)s, %(form_type)s, %(filed_date)s,
        %(report_date)s, %(primary_document)s, %(source_url)s,
        %(bytes_fetched)s, %(footnote_found)s, %(lots_parsed)s, %(parse_note)s)
ON CONFLICT (accession) DO UPDATE SET
    bytes_fetched  = EXCLUDED.bytes_fetched,
    footnote_found = EXCLUDED.footnote_found,
    lots_parsed    = EXCLUDED.lots_parsed,
    parse_note     = EXCLUDED.parse_note,
    fetched_at     = now()
"""

RECORD_LOT = """
INSERT INTO restricted_lots
    (cik, accession, form_type, filed_date, report_date, registrant, fund_name,
     issuer_name_raw, security_class_raw, acquisition_date_first,
     acquisition_date_last, acquisition_date_raw, acquisition_date_is_range,
     value_usd, cost_usd, cost_basis_scope, pct_net_assets, company_provisional,
     source_url)
VALUES (%(cik)s, %(accession)s, %(form_type)s, %(filed_date)s, %(report_date)s,
        %(registrant)s, %(fund_name)s, %(issuer_name_raw)s, %(security_class_raw)s,
        %(acquisition_date_first)s, %(acquisition_date_last)s,
        %(acquisition_date_raw)s, %(acquisition_date_is_range)s, %(value_usd)s,
        %(cost_usd)s, %(cost_basis_scope)s, %(pct_net_assets)s,
        %(company_provisional)s, %(source_url)s)
ON CONFLICT (accession, fund_name, issuer_name_raw, security_class_raw,
             acquisition_date_raw) DO UPDATE SET
    value_usd        = EXCLUDED.value_usd,
    cost_usd         = EXCLUDED.cost_usd,
    cost_basis_scope = EXCLUDED.cost_basis_scope,
    pct_net_assets   = EXCLUDED.pct_net_assets
"""


def load(conn, companies=TOP_THREE, max_registrants: int = 25,
         session=None, verbose: bool = True) -> dict:
    """Fetch, parse and store the footnote for the heaviest registrants.

    Every filing touched gets a row in `ncsr_filings` whether or not it
    yielded a lot, because "the parser found nothing here" and "nobody looked
    here" are different facts and a table of lots alone cannot tell them
    apart.
    """
    targets = registrants(conn, companies, max_registrants)
    stats = {"registrants": len(targets), "filings": 0, "lots": 0,
             "bytes": 0, "no_footnote": 0, "parsed_zero": 0, "errors": []}

    for rank, target in enumerate(targets, start=1):
        try:
            filings = newest_per_form(list_filings(target["cik"], session))
        except Exception as exc:                        # noqa: BLE001
            stats["errors"].append(f"{target['cik']} list: {exc}")
            continue

        for filing in filings:
            try:
                body = fetch_document(filing["source_url"], session)
            except Exception as exc:                    # noqa: BLE001
                stats["errors"].append(f"{filing['accession']} fetch: {exc}")
                continue
            document = body.decode("utf-8", "replace")
            # Parse unconditionally. Gating the parse on the text probe made
            # the probe's blind spots into missing data rather than into a
            # visibly empty result, and the probe had one.
            lots = parse_document(document)
            found = footnote_present(document) or bool(lots)

            note = None
            if not found:
                note = "no 'restricted securit...' anywhere in the document"
                stats["no_footnote"] += 1
            elif not lots:
                note = ("footnote text present but no universe lot parsed -- "
                        "either this registrant holds none of the named "
                        "companies in a restricted position, or its table "
                        "header names no acquisition-date column")
                stats["parsed_zero"] += 1

            with conn.cursor() as cur:
                # Replace this filing's lots rather than upserting them.
                # The unique key contains parsed fields -- fund_name, the raw
                # date string, the issuer name -- so improving the parser
                # changes the key and ON CONFLICT silently appends a second
                # version of the same lot instead of correcting the first.
                # Re-running the ingest three times left 715 rows where 252
                # were parsed. The filing is immutable; its parse is not, and
                # only the parse is deleted here.
                cur.execute("DELETE FROM restricted_lots WHERE accession = %s",
                            (filing["accession"],))
                cur.execute(RECORD_FILING, {
                    **filing, "bytes_fetched": len(body),
                    "footnote_found": found, "lots_parsed": len(lots),
                    "parse_note": note,
                })
                for lot in lots:
                    cur.execute(RECORD_LOT, {
                        "cik": filing["cik"], "accession": filing["accession"],
                        "form_type": filing["form_type"],
                        "filed_date": filing["filed_date"],
                        "report_date": filing["report_date"],
                        "registrant": filing["registrant"],
                        "fund_name": lot.get("fund_name") or "",
                        "security_class_raw": "",
                        "source_url": filing["source_url"], **lot,
                    })
            conn.commit()

            stats["filings"] += 1
            stats["lots"] += len(lots)
            stats["bytes"] += len(body)
            if verbose:
                print(f"[{rank:3}/{len(targets)}] {target['family']:22.22} "
                      f"{filing['form_type']:7} {len(body)/1e6:6.1f} MB "
                      f"-> {len(lots):3} lots", flush=True)
    return stats


def coverage(conn) -> dict:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT count(*) AS filings,
                   count(*) FILTER (WHERE footnote_found)      AS with_footnote,
                   count(*) FILTER (WHERE lots_parsed > 0)     AS with_lots,
                   count(DISTINCT cik)                         AS registrants,
                   coalesce(sum(bytes_fetched), 0)             AS bytes_fetched
              FROM ncsr_filings
        """)
        filings = dict(zip([c[0] for c in cur.description], cur.fetchone()))
        cur.execute("""
            SELECT company_provisional AS company,
                   count(*)                                           AS lots,
                   count(DISTINCT registrant)                         AS registrants,
                   count(*) FILTER (WHERE cost_basis_scope = 'position') AS with_position_cost,
                   count(*) FILTER (WHERE acquisition_date_is_range)  AS date_ranges,
                   min(acquisition_date_first)                        AS earliest_entry,
                   max(acquisition_date_last)                         AS latest_entry
              FROM restricted_lots
             WHERE company_provisional IS NOT NULL
             GROUP BY 1 ORDER BY 2 DESC
        """)
        by_company = [dict(zip([c[0] for c in cur.description], r))
                      for r in cur.fetchall()]
    return {"filings": filings, "by_company": by_company}


def main() -> None:
    import argparse
    import json

    from src.db.connect import apply_schema, connect

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max-registrants", type=int, default=25)
    ap.add_argument("--coverage", action="store_true", help="report, do not fetch")
    args = ap.parse_args()

    conn = connect()
    apply_schema(conn)
    try:
        if args.coverage:
            print(json.dumps(coverage(conn), indent=2, default=str))
        else:
            print(json.dumps(load(conn, max_registrants=args.max_registrants),
                             indent=2, default=str))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
