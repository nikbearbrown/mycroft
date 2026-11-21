"""The opening-ledger reader (DESIGN.md §7.3, agent-start mode; week 6): the debt the company owed at the start of
the episode, read from the debt table of its last report — not borrowed from the answer key.

DESIGN.md §7.1 rule 1 holds here as in the event reader: the model points, code reads.

1. **Tables (code).** The report's main document is opened through the `docs` store (so the point-in-time rule
   holds). Every table is scored as a debt table: rows whose label names a coupon, a maturity year or a debt word
   *and* carry an amount; a caption about debt or borrowings scores more, fair-value and lease tables less; the
   cover page's list of registered notes and the exhibit index carry no amounts and drop out. The best few are kept.
2. **Pointing (model).** `qwen3:4b` sees the candidate tables, every row with its id and every cell with its
   column number, and the report's period end. It names the rows that are one debt instrument outstanding at the
   period end, the column that holds the period-end amount, each instrument's kind, and the row that states total
   debt. It types no number. Output is forced to a JSON schema. Which rows are instruments, and their kinds, are
   **model judgments** (P8), flagged.
3. **Reading (code).** Each named row is parsed with the answer key's own label parser (`ledger/parsers.py`):
   coupon, maturity year, currency, offering ranges ("2015 issuance of $23.8 billion, 2025–2055"). The amount is
   the named cell, parsed and scaled by the units the table states ("In millions"); a dash is zero, and a row at
   zero is a bond repaid before the period end, so it is left out. A foreign-currency bond printed in dollars keeps
   its dollar amount as `amount_usd` and no own-currency principal, unless the label states one ("€500 million").

`rules` is the same reader without the model: the best-scoring table, every row whose label has a coupon or a
maturity, and the first amount cell. It is the comparison that says what the model's pointing adds.

The result is a ledger in the grader's format, with `source` citing the table row and cell of every instrument.
"""

from __future__ import annotations

import json
import re
import time

from ...ledger import parsers as P
from ...ledger import values as V
from . import reader as rd

DEBT_LABEL = re.compile(r"\bnotes?\b|debentures?|\bbonds?\b|term loan|credit (?:facility|agreement)|revolv|"
                        r"commercial paper|convertible|\bloans?\b|borrowings?|issuance of|senior|facility", re.I)
TOTAL_LABEL = re.compile(r"^\s*total|\bnet\b.*\bdebt\b|less:|unamortiz|discount|premium|issuance costs|"
                         r"fair value|hedg|current portion|current maturities|long-term debt$|^long-term debt, net", re.I)
CAPTION_DEBT = re.compile(r"\bdebt\b|borrowings|\bnotes\b|indebtedness|credit facilit", re.I)
CAPTION_OFF = re.compile(r"fair value|lease|interest expense|amortization|derivative|swap|hedg|maturit(?:y|ies) of|"
                         r"future principal|schedule|available borrowings|unused|availability", re.I)
RATE_HEAD = re.compile(r"\brate\b|%|interest terms", re.I)
TOTAL_ROW = re.compile(r"^\s*(?:total|net)\b(?!.*(?:principal|face|long-term debt, less|lease)).*\b(?:debt|borrowings|"
                       r"carrying amount|notes)\b", re.I)
UNITS = re.compile(r"in\s+(thousands|millions|billions)", re.I)
SCALE = {"thousands": 1e3, "millions": 1e6, "billions": 1e9}
NUMBER = re.compile(r"^\(?\s*[$€£]?\s*\(?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)\s*\)?$")
DASH = re.compile(r"^\s*[$€£]?\s*[—–-]+\s*$")
DATE_HEAD = re.compile(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2},?\s+(20\d\d)", re.I)
MONTHS = {m: i for i, m in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov",
                                      "dec"), 1)}
MAX_TABLES, MAX_ROWS = 4, 120
KINDS = ["notes", "convertible_notes", "term_loan", "revolving_facility", "commercial_paper", "finance_lease", "other"]


def cell_amount(cell: str) -> float | None:
    """A table cell as a number in the table's units: '1,750' -> 1750, '$—' -> 0, '(31)' -> None (an adjustment)."""
    c = cell.strip()
    if DASH.match(c):
        return 0.0
    if c.startswith("(") or c.endswith(")"):
        return None
    m = NUMBER.match(c.replace(" ", ""))
    if not m or "%" in c:
        return None
    return float(m.group(1).replace(",", ""))


def _is_year(cell: str) -> bool:
    return bool(re.fullmatch(r"\s*(19|20)\d\d\s*", cell))


def amount_cells(row: list[str]) -> list[int]:
    """Indices of the cells that hold an amount (not a rate, not a bare year, not the label)."""
    return [k for k, c in enumerate(row) if k > 0 and not _is_year(c) and cell_amount(c) is not None]


def table_units(table, doc) -> float:
    for text in [table.caption or ""] + [" ".join(r) for r in table.rows[:3]]:
        m = UNITS.search(text)
        if m:
            return SCALE[m.group(1).lower()]
    # the parser keeps 160 characters of a caption, so "(in thousands)" can be cut off: the document votes, captions
    # included (P61; Super Micro's loan table)
    votes = {}
    for t in doc.tables:
        for text in [t.caption or ""] + [" ".join(r) for r in t.rows[:3]]:
            m = UNITS.search(text)
            if m:
                votes[m.group(1).lower()] = votes.get(m.group(1).lower(), 0) + 1
    return SCALE[max(votes, key=votes.get)] if votes else 1e6


def instrument_row(row: list[str]) -> bool:
    label = row[0] if row else ""
    return bool(amount_cells(row)) and not TOTAL_LABEL.search(label) and bool(
        DEBT_LABEL.search(label) or V.RATE.search(label) or P.DUE_YEAR.search(label))


def score_table(table) -> int:
    rows = table.rows[:MAX_ROWS]
    n = sum(instrument_row(r) for r in rows)
    keyed = sum(instrument_row(r) and bool(V.RATE.search(" ".join(r[:3]))) for r in rows)
    if n < 1:
        return 0
    cap = " ".join([table.caption or ""] + [" ".join(r) for r in rows[:2]])
    return n + keyed + 4 * bool(CAPTION_DEBT.search(cap)) - 6 * bool(CAPTION_OFF.search(table.caption or ""))


def candidate_tables(doc, k: int = MAX_TABLES) -> list:
    scored = sorted(((score_table(t), i, t) for i, t in enumerate(doc.tables)), key=lambda x: (-x[0], x[1]))
    return [t for s, _, t in scored[:k] if s >= 2]


def period_columns(table, period_end: str) -> tuple[int, int] | None:
    """(position of the period-end date among the header's dates, number of dates), when the header names dates
    ("Apr 27, 2025 | Jan 26, 2025") or, in a 10-K, bare years ("2025 | 2024"). The amount for the period end is then
    that position among the row's last n amount cells — columns before them (a remaining term, a rate) do not
    shift it."""
    y, mo = int(period_end[:4]), int(period_end[5:7])
    for r in table.rows[:4]:
        dates = [(int(m.group(2)), MONTHS[m.group(1).lower()[:3]]) for c in r for m in DATE_HEAD.finditer(c)]
        if not dates:
            years = [int(c.strip()) for c in r if _is_year(c)]
            dates = [(yy, mo) for yy in years] if len(years) >= 2 else []
        if dates:
            for i, (dy, dm) in enumerate(dates):
                if (dy == y and abs(dm - mo) <= 1) or (dy == y + 1 and mo == 12 and dm == 1):
                    return i, len(dates)
            return None
    return None


def _dated(cell: str, period_end: str) -> bool:
    """A header cell that names the period end ('Principal Outstanding as of January 31, 2025')."""
    y, mo = int(period_end[:4]), int(period_end[5:7])
    return any((int(m.group(2)) == y and abs(MONTHS[m.group(1).lower()[:3]] - mo) <= 1)
               for m in DATE_HEAD.finditer(cell))


def parse_row(row: list[str], amount_cell: int, units: float, period_end: str) -> dict | None:
    """One instrument from one table row: code reads every value from the row's own words."""
    if amount_cell is None or amount_cell >= len(row) or amount_cell < 1:
        return None
    amt = cell_amount(row[amount_cell])
    if amt is None or amt == 0:
        return None                       # an adjustment, or a bond repaid before the period end
    # the label, then the columns before the amount that name a maturity year or — when the label states no coupon —
    # the first rate (a "Stated Interest Rate" column precedes an "Effective Interest Rate" one)
    extra = [c for c in row[1:amount_cell] if _is_year(c) or re.search(r"(19|20)\d\d\s*[–-]\s*(19|20)\d\d", c)]
    if not V.RATE.search(row[0]):
        extra += [c for c in row[1:amount_cell] if V.RATE.search(c)][:1]
    text = " ".join([row[0]] + extra)
    year, month = int(period_end[:4]), int(period_end[:4] + period_end[5:7])
    pm = P._parse_text(text, year, month)
    usd = amt * units
    cur = pm.currency or "USD"
    principal = usd if cur == "USD" else None
    if cur != "USD":
        own = V.parse_amount(row[0], cur)          # "€500 million 3.25% notes due 2029": the label states it
        principal = own[0] if own and own[1] == cur else None
    kind = "offering" if pm.offering else "bond" if (pm.maturity_year and pm.kind in (None, "notes", "convertible")) \
        else "facility" if pm.kind in ("revolver", "term_loan", "delayed_draw", "credit_facility", "commercial_paper") \
        else "other"
    return {"kind": kind, "currency": cur, "principal": principal, "coupon_pct": pm.rate,
            "maturity_year": pm.maturity_year, "floating": pm.floating, "issued": None, "amount_usd": usd,
            "label": row[0], "parsed_kind": pm.kind}


def _kind(parsed: dict, said: str | None) -> str:
    if parsed["kind"] == "offering":
        return "offering"
    if said in ("term_loan", "revolving_facility", "commercial_paper") or parsed["kind"] == "facility":
        return "facility"
    if said == "finance_lease":
        return "other"
    if parsed["maturity_year"] and (said in (None, "notes", "convertible_notes") or parsed["coupon_pct"] is not None):
        return "bond"
    return "other"


def render(tables: list) -> str:
    out = []
    for t in tables:
        out.append(f"TABLE {t.id} — {(t.caption or '')[:160]}")
        for i, r in enumerate(t.rows[:MAX_ROWS]):
            cells = " | ".join(f"c{k}: {c[:90]}" for k, c in enumerate(r))
            out.append(f"[{t.id}.r{i}] {cells}")
        out.append("")
    return "\n".join(out)


SCHEMA = {"type": "object", "properties": {
    "instruments": {"type": "array", "items": {"type": "object", "properties": {
        "row": {"type": "string"}, "amount_column": {"type": "integer"},
        "kind": {"type": "string", "enum": KINDS}}, "required": ["row", "amount_column", "kind"]}},
    "total_debt": {"type": "object", "properties": {"row": {"type": ["string", "null"]},
                                                    "amount_column": {"type": ["integer", "null"]}},
                   "required": ["row", "amount_column"]}},
    "required": ["instruments", "total_debt"]}

PROMPT = (
    "You are reading the debt note of a company's {form} for the period ended {period}. Below are tables from it; "
    "each row has an id in brackets and each cell a column number (c0 is the row label).\n\n"
    "List every row that is ONE debt instrument the company owed at {period}: a bond or note, a convertible note, a "
    "term loan, a drawn revolving facility, commercial paper. For each give the row id, the column number holding its "
    "amount at {period} (not the earlier date, not a rate, not a year), and its kind. Header rows have fewer cells than "
    "data rows, so count a data row's own cells. If the table splits each date into Current, Long-Term and Total, use "
    "the Total column for {period}. A row whose amount at {period} is a dash was repaid: leave it out. Do NOT list totals, subtotals, "
    "discounts, issuance costs, premiums, hedge adjustments, current-portion lines, rows from fair-value tables, or the "
    "same instrument twice. A table may continue on the next page as another table: list the rows of every table. Also give the row and column stating TOTAL debt at {period} (prefer the "
    "row for total debt including the current portion, net of discounts), or null.\n"
    "Point only; never type a number.\n\nTABLES:\n{tables}")


def ask_model(tables: list, form: str, period_end: str, model: str = "qwen3:4b", host: str | None = None) -> str:
    content, _ = rd.call_model(PROMPT.format(form=form, period=period_end, tables=render(tables)), SCHEMA, model,
                               host, num_predict=3_072, num_ctx=16_384)
    return content


def _rows(tables: list) -> dict:
    return {f"{t.id}.r{i}": (t, r) for t in tables for i, r in enumerate(t.rows[:MAX_ROWS])}


def _dedupe(insts: list[dict]) -> list[dict]:
    """The same bond read from two tables (a debt table and a maturity table) is one bond."""
    out, seen = [], set()
    for i in insts:
        k = (i["kind"], i["currency"], i["coupon_pct"], i["maturity_year"], round(i["amount_usd"] or 0, -5)) \
            if i["coupon_pct"] is not None or i["maturity_year"] else None
        if k and k in seen:
            continue
        if k:
            seen.add(k)
        out.append(i)
    return out


def _total(t, r, col, units) -> float | None:
    if col is None or col >= len(r) or col < 1:
        return None
    a = cell_amount(r[col])
    return a * units if a else None


def code_column(table, row: list[str], period_end: str) -> int | None:
    """The period-end amount's cell in a data row, when the header settles it (code, not the model): a header row
    one cell shorter than the row that names Total columns (Micron: Current | Long-Term | Total per date) gives the
    Total column of the period-end date; otherwise header dates give the position among the row's last amounts.
    None when the header says neither."""
    cells = sorted(set(amount_cells(row) + [k for k, c in enumerate(row) if k > 0 and c.strip().startswith("(")]))
    pc = period_columns(table, period_end)
    for h in table.rows[:5]:
        tot = [k + 1 for k, c in enumerate(h) if c.strip().lower() == "total"]
        if len(h) == len(row) - 1 and tot:
            return tot[pc[0] if pc and pc[0] < len(tot) else 0]
    # a header with one cell per data cell (P61; Salesforce: Instrument | Maturity Date | Principal Outstanding as of
    # January 31, 2025 | Interest Terms | Contractual Interest Rate): the one column dated the period end is the
    # amount; columns headed as a rate never are
    for h in table.rows[:4]:
        if len(h) != len(row) or h is row:
            continue
        dated = [k for k, c in enumerate(h) if k > 0 and _dated(c, period_end)]
        if len(dated) == 1 and dated[0] in cells:
            return dated[0]
        rates = {k for k, c in enumerate(h) if k > 0 and RATE_HEAD.search(c)}
        if rates:
            cells = [k for k in cells if k not in rates]
    if pc and len(cells) >= pc[1]:
        return cells[len(cells) - pc[1] + pc[0]]
    return None


def read_rules(doc, period_end: str) -> dict:
    """The comparison: no model. Best table; rows with a coupon or a maturity; the period-end date column if the
    header names dates, else the first amount cell; total debt from the first row labelled 'total debt'."""
    cands = candidate_tables(doc, 1)
    if not cands:
        return {"instruments": [], "totals": {}, "tables": [], "error": "no debt table"}
    t = cands[0]
    units = table_units(t, doc)
    insts, totals = [], []
    for i, r in enumerate(t.rows[:MAX_ROWS]):
        cells = amount_cells(r) + [k for k, c in enumerate(r) if k > 0 and c.strip().startswith("(")]
        cells = sorted(set(cells))
        if not cells:
            continue
        col = code_column(t, r, period_end) or cells[0]
        if TOTAL_ROW.search(r[0]):
            v = _total(t, r, col, units)
            if v:
                totals.append((bool(re.search(r"\bnet\b|carrying", r[0], re.I)), r[0], v))
            continue
        if instrument_row(r) and (V.RATE.search(r[0]) or P.DUE_YEAR.search(r[0]) or P.YEAR.search(r[0])
                                  or any(_is_year(c) for c in r[1:col])):
            p = parse_row(r, col, units, period_end)
            if p:
                p["kind"] = _kind(p, None)
                p["source"] = {"table": t.id, "row": f"{t.id}.r{i}", "cell": col}
                insts.append(p)
    # total debt: a row labelled net or carrying first (the key's total is the balance sheet's), else the first
    total = next((v for net, _, v in totals if net), None) or (totals[0][2] if totals else None)
    return {"instruments": _dedupe(insts), "totals": {"total_debt": total} if total else {}, "tables": [t.id],
            "model_judgment": False}


def read_opening(doc, form: str, period_end: str, model: str = "qwen3:4b", host: str | None = None,
                 ask=ask_model) -> dict:
    """The opening ledger from one report's main document (agent start). Falls back to `read_rules` when no table
    qualifies or the model's answer does not parse; the result says which."""
    t0 = time.time()
    tables = candidate_tables(doc)
    if not tables:
        return read_rules(doc, period_end) | {"seconds": 0.0, "error": "no debt table"}
    raw = None
    try:
        raw = ask(tables, form, period_end, model, host)
        ans = json.loads(raw)
    except (json.JSONDecodeError, OSError) as ex:
        return read_rules(doc, period_end) | {"seconds": round(time.time() - t0, 2), "error": f"model: {ex!s:.80}",
                                              "fallback": "rules"}
    rows = _rows(tables)
    insts, refused = [], []
    for a in ans.get("instruments", []):
        hit = rows.get(a.get("row"))
        if hit is None:
            refused.append({"row": a.get("row"), "why": "no such row"})
            continue
        t, r = hit
        col = code_column(t, r, period_end) or a.get("amount_column")     # the header settles it when it can
        p = parse_row(r, col, table_units(t, doc), period_end)
        if p is None:
            refused.append({"row": a.get("row"), "why": "no amount in that column (or zero)"})
            continue
        p["kind"] = _kind(p, a.get("kind"))
        p["said_kind"] = a.get("kind")
        p["source"] = {"table": t.id, "row": a["row"], "cell": col, "model_column": a.get("amount_column")}
        p["model_judgment"] = True
        insts.append(p)
    totals = {}
    td = ans.get("total_debt") or {}
    if td.get("row") in rows:
        t, r = rows[td["row"]]
        v = _total(t, r, code_column(t, r, period_end) or td.get("amount_column"), table_units(t, doc))
        if v:
            totals = {"total_debt": v}
            totals_source = {"row": td["row"], "cell": td.get("amount_column")}
    out = {"instruments": _dedupe(insts), "totals": totals, "tables": [t.id for t in tables], "refused": refused,
           "model_judgment": True, "seconds": round(time.time() - t0, 2), "raw": (raw or "")[:40000]}
    if totals:
        out["totals_source"] = totals_source
    return out
