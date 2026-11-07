"""Code parsers for the values a debt announcement states: amounts, interest rates and maturity years.

DESIGN.md §7.1 rule 1: the AI never types a number. The event reader points at a sentence or a table
cell and copies the words that state a value ("$1,250,000,000", "4.750%", "June 1, 2031"); this
module turns those words into numbers. Nothing here is a model, and every parser returns None rather
than guess when the words do not state a value.

Forms seen in Week 1–3 documents (term sheets, prospectus covers, 8-K items):
  amounts   "$1,250,000,000"  "$1.25 billion"  "US$500 million"  "€750,000,000"  "€ 1.0 billion"
            "£400 million"  "CHF 300 million"  "$ 1,000,000,000"  "1,683.5 million"  "$1.6835 billion"
  rates     "4.750%"  "5.80 %"  "0%"  "1.75 % per annum"  "SOFR + 1.25%" (floating: no fixed rate)
  years     "2031"  "due 2031"  "June 1, 2031"  "March 15, 2030"  "2030 Notes"
"""

from __future__ import annotations

import re

CURRENCY_MARKS = [("EUR", r"€|\beuros?\b|\beur\b"), ("GBP", r"£|\bsterling\b|\bgbp\b|\bpounds?\b"),
                  ("CHF", r"\bchf\b|swiss francs?"), ("JPY", r"¥|\byen\b|\bjpy\b"), ("CAD", r"\bc\$|\bcad\b"),
                  ("AUD", r"\ba\$|\baud\b"), ("USD", r"\$|\busd\b|u\.s\. dollars?|\bdollars?\b")]
SCALE = {"thousand": 1e3, "million": 1e6, "mm": 1e6, "billion": 1e9, "bn": 1e9, "trillion": 1e12}
AMOUNT = re.compile(r"(?P<cur>US\$|U\.S\.\$|C\$|A\$|\$|€|£|¥|CHF|EUR|GBP|USD|JPY)?\s*"
                    r"(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
                    r"(?:\s*(?P<scale>thousand|million|billion|trillion|mm|bn)\b)?", re.I)
RATE = re.compile(r"(?<![\d.])(\d{1,2}(?:\.\d{1,5})?)\s*(?:%|percent\b|per cent\b)", re.I)
FLOATING = re.compile(r"\bsofr\b|\blibor\b|\beuribor\b|\bsonia\b|floating|base rate|prime rate|term rate|\bbsby\b", re.I)
YEAR = re.compile(r"(?<!\d)(20[2-9]\d|21\d\d)(?!\d)")
DUE_YEAR = re.compile(r"\b(?:due|matur\w*|expir\w*|until|through)\b\D{0,40}?(20[2-9]\d|21\d\d)(?!\d)", re.I)


def currency_of(text: str) -> str | None:
    low = text.lower()
    for code, pat in CURRENCY_MARKS:
        if re.search(pat, low):
            return code
    return None


def parse_amount(text: str, default_currency: str | None = None) -> tuple[float, str | None] | None:
    """The first money amount in `text`, as (value in units of the currency, ISO currency or None).
    A bare number with no currency mark and no scale word is not an amount ("2031", "4.750")."""
    for m in AMOUNT.finditer(text or ""):
        num, cur, scale = m.group("num"), m.group("cur"), (m.group("scale") or "").lower()
        if not cur and not scale and "," not in num:
            continue                     # a year, a coupon, a count — not money
        try:
            value = float(num.replace(",", ""))
        except ValueError:
            continue
        value *= SCALE.get(scale, 1.0)
        if value < 1_000:                # "$5" or "1.5 million" typo-level noise: not a debt amount
            continue
        code = currency_of(cur or "") if cur else None
        if code is None:
            around = (text or "")[max(0, m.start() - 12): m.end() + 25]
            code = currency_of(around) or default_currency
        return value, code
    return None


def parse_rate(text: str) -> float | None:
    """A fixed annual rate in percent; None for a floating rate ("SOFR + 1.25%") or no rate."""
    if not text or FLOATING.search(text):
        return None
    m = RATE.search(text)
    if not m:
        return None
    v = float(m.group(1))
    return v if 0 <= v < 30 else None


def is_floating(text: str) -> bool:
    return bool(text and FLOATING.search(text))


def parse_year(text: str) -> int | None:
    """A maturity year: the year after "due"/"matures" if there is one, else the only year in the text,
    else the last one ("issued in 2024, due June 1, 2031" → 2031)."""
    if not text:
        return None
    m = DUE_YEAR.search(text)
    if m:
        return int(m.group(1))
    years = YEAR.findall(text)
    return int(years[-1]) if years else None


def norm(text: str) -> str:
    """Whitespace- and quote-insensitive form, for checking that a copied value is in its span."""
    t = (text or "").replace(" ", " ").replace("’", "'").replace("“", '"').replace("”", '"')
    return " ".join(t.split()).lower()


def grounded(copied: str, span_text: str) -> bool:
    """Is the copied value really in the cited span? Spacing around '%' and '$' is forgiven
    ("4.750 %" in a table cell vs "4.750%" copied); nothing else is."""
    if not copied or not copied.strip():
        return False
    a, b = norm(copied), norm(span_text)
    if a in b:
        return True
    squeeze = lambda s: re.sub(r"\s*([%$€£])\s*", r"\1", s)  # noqa: E731
    return squeeze(a) in squeeze(b)
