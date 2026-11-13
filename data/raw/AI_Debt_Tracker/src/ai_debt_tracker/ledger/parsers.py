"""Read a debt member's name or label into a match key: coupon, maturity year, kind, currency.

XBRL debt members are free text squeezed into an identifier, and the feasibility spike found the
ways that breaks a naive regex (DESIGN.md §3.4):

* P3  — no standard naming: `Notes3.30Due2027`, `ConvertibleNotes2030`, `TermLoans`.
* P18 — some members are an *offering* (several bonds sold on one day), not a bond:
        `A2026USDollarNotes`, `March2026SeniorUnsecuredNotes`, `November2025Debt`.
* P20 — numbers spelled in words, with typos:
        `FourPointSixZeroZeroPercentSeniorNotesDueTwoThousandThirty`, `ThreePointTwoFieveZero…`.

`parse_member(name, label)` reads the human label first (from the notes data's `tag.tsv`, e.g.
"Senior Notes, 3.30% Due 2027") and falls back to the member name. Everything here is plain code
and deterministic; nothing is guessed by a model. A field that cannot be read is `None`, never a
default.
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field

UNITS = {"zero": 0, "oh": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
         "eight": 8, "nine": 9}
TEENS = {"ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
         "seventeen": 17, "eighteen": 18, "nineteen": 19}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fourty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
        "eighty": 80, "ninety": 90}
FRACTIONS = {"half": 0.5, "quarter": 0.25, "quarters": 0.25, "eighth": 0.125, "eighths": 0.125}
NUMBER_WORDS = {**UNITS, **TEENS, **TENS}
VOCAB = list(NUMBER_WORDS) + ["point", "percent", "thousand", "hundred"]
MONTHS = ("january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
          "november", "december", "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec")
CURRENCIES = [("EUR", r"euro|eur\b|€"), ("GBP", r"sterling|gbp|pound"), ("CHF", r"swiss ?franc|chf"),
              ("JPY", r"\byen\b|jpy"), ("CAD", r"canadian|cad\b"), ("AUD", r"australian|aud\b")]

KIND_RULES = [  # first match wins; order matters (a "convertible senior note" is convertible)
    ("commercial_paper", r"commercial ?paper"),
    ("convertible", r"convertible|exchangeable"),
    ("revolver", r"revolv|revolver|\brcf\b|line ?of ?credit|credit ?line|abl\b|asset[- ]based"),
    ("delayed_draw", r"delayed ?draw|\bddtl\b"),
    ("term_loan", r"term ?loan|\btla\b|\btlb\b|loan ?facility|facility ?loans?"),
    ("credit_facility", r"credit ?(facility|agreement)|facility"),
    ("finance_lease", r"finance ?lease|capital ?lease"),
    ("other_debt", r"other (long ?term )?(debt|borrowings?)"),
    # "nots": Broadcom's member for its 4.65% May 2027 notes is spelt `May2027SeniorNots`
    ("notes", r"notes?\b|\bnots\b|bonds?\b|debentures?|senior ?unsecured|senior ?secured|\bdebt\b"),
]


@dataclass
class ParsedMember:
    rate: float | None = None             # coupon in percent, e.g. 4.6
    rate_digits: int | None = None        # decimals as written (4.600 -> 3), for P17 tolerance
    maturity_year: int | None = None
    kind: str | None = None
    offering: bool = False                # P18: an issue-date group, not one bond
    floating: bool = False
    currency: str | None = None           # only when the text names a non-USD currency
    source: str = ""                      # "label" or "name" — where the fields came from
    notes: list[str] = field(default_factory=list)

    def key(self):
        """The match key of DESIGN.md P3, or None when coupon or maturity is missing."""
        if self.rate is None or self.maturity_year is None or self.offering:
            return None
        return (self.currency or "USD", round(self.rate, 3), self.maturity_year)


def split_camel(name: str) -> str:
    """`FourPointSixZeroPercentNotesDue2030Member` -> 'Four Point Six Zero Percent Notes Due 2030'."""
    name = re.sub(r"Member$", "", name)
    # a maturity year glued to a coupon: CoreWeave's `A20319.00SeniorNotes` is "2031 9.00% Senior Notes"
    name = re.sub(r"(?<!\d)(20[2-9]\d)(?=\d{1,2}\.\d)", r"\1 ", name)
    name = re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])", " ", name)
    return re.sub(r"\s+", " ", name.replace("_", " ")).strip()


def _fix_typos(words: list[str]) -> list[str]:
    """Correct misspelt number words, but only next to other number words (`Two Fieve Zero`,
    `Twele Point Zero`), so ordinary words like 'Note' are never 'corrected' into numbers."""
    out = list(words)
    for i, w in enumerate(words):
        lw = w.lower()
        if lw in NUMBER_WORDS or lw in ("point", "percent", "thousand") or len(lw) < 3 or not lw.isalpha():
            continue
        prev_num = i > 0 and words[i - 1].lower() in (*NUMBER_WORDS, "point")
        next_num = i + 1 < len(words) and words[i + 1].lower() in (*NUMBER_WORDS, "point", "percent")
        # inside a run of number words a loose match is safe ("Two Fieve Zero"); at the edge of one
        # ("Twele Point Zero") only a near-exact one is
        cutoff = 0.75 if prev_num and next_num else 0.85 if (prev_num or next_num) and len(lw) >= 4 else None
        if cutoff:
            close = difflib.get_close_matches(lw, VOCAB, n=1, cutoff=cutoff)
            if close:
                out[i] = close[0]
    return out


def _words_to_rate(words: list[str]) -> tuple[float, int] | None:
    """'Four Point Six Two Five Percent' -> (4.625, 3); 'Four And Three Quarters Percent' -> (4.75, 2)."""
    lw = [w.lower() for w in words]
    for i, w in enumerate(lw):
        if w != "point" or i == 0:
            continue
        j = i - 1
        whole = None
        if lw[j] in UNITS or lw[j] in TEENS:
            whole = NUMBER_WORDS[lw[j]]
            if j > 0 and lw[j - 1] in TENS and lw[j] in UNITS:
                whole += TENS[lw[j - 1]]
        elif lw[j] in TENS:
            whole = TENS[lw[j]]
        if whole is None:
            continue
        digits = []
        for w2 in lw[i + 1:]:
            if w2 in UNITS:
                digits.append(str(UNITS[w2]))
            else:
                break
        if digits:
            return float(f"{whole}.{''.join(digits)}"), len(digits)
    m = re.search(r"\b(" + "|".join(UNITS) + r") and (one|three|five|seven) (half|quarters?|eighths?)\b", " ".join(lw))
    if m:
        frac = UNITS[m.group(2)] * FRACTIONS[m.group(3)]
        return UNITS[m.group(1)] + frac, 3
    return None


def _words_to_years(words: list[str]) -> list[int]:
    """'Two Thousand Thirty' -> 2030, 'Two Thousand Twenty Seven' -> 2027, 'Twenty Thirty One' -> 2031."""
    lw = [w.lower() for w in words]
    years = []
    for i in range(len(lw)):
        if lw[i] == "two" and i + 1 < len(lw) and lw[i + 1] == "thousand":
            rest, k = 0, i + 2
            if k < len(lw) and lw[k] in TENS:
                rest = TENS[lw[k]]
                if k + 1 < len(lw) and lw[k + 1] in UNITS:
                    rest += UNITS[lw[k + 1]]
            elif k < len(lw) and (lw[k] in TEENS or lw[k] in UNITS):
                rest = NUMBER_WORDS[lw[k]]
            if rest:
                years.append(2000 + rest)
        elif lw[i] == "twenty" and i + 1 < len(lw) and lw[i + 1] in TENS and (i == 0 or lw[i - 1] not in ("thousand",)):
            rest = TENS[lw[i + 1]]
            if i + 2 < len(lw) and lw[i + 2] in UNITS:
                rest += UNITS[lw[i + 2]]
            years.append(2000 + rest)
    return [y for y in years if 2000 <= y <= 2099]


RATE_DIGITS = re.compile(r"(?<![\d.])(\d{1,2}\.\d{1,4})\s*(?:%|percent|pct\b)", re.I)
RATE_BARE = re.compile(r"(?<![\d.])(\d{1,2}\.\d{1,4})(?![\d.])")
DUE_YEAR = re.compile(r"\b(?:due|matur\w*|expir\w*)\b\D{0,25}?((?:19|20)\d\d)\b", re.I)
YEAR = re.compile(r"(?<!\d)(20[2-9]\d)(?!\d)")
YEAR_RANGE = re.compile(r"(?<!\d)(20\d\d)\s*(?:-|–|to|through)\s*(20\d\d)(?!\d)", re.I)
MONTH_YEAR = re.compile(r"\b(" + "|".join(MONTHS) + r")\.?\s*(?:\d{1,2},?\s*)?(20\d\d)\b", re.I)


def _parse_text(text: str, as_of_year: int | None = None, as_of_month: int | None = None) -> ParsedMember:
    p = ParsedMember()
    words = _fix_typos(text.split())
    norm = " ".join(words)
    low = norm.lower()

    m = RATE_DIGITS.search(norm)
    if m:
        p.rate, p.rate_digits = float(m.group(1)), len(m.group(1).split(".")[1])
    else:
        wr = _words_to_rate(words)
        if wr:
            p.rate, p.rate_digits = wr
        else:
            # a bare decimal is a rate only next to a bond word ("Notes 3.30 Due 2027"), never a year
            m = RATE_BARE.search(norm)
            if m and re.search(r"notes?|bonds?|debentures?", low) and 0 < float(m.group(1)) < 20:
                p.rate, p.rate_digits = float(m.group(1)), len(m.group(1).split(".")[1])
                p.notes.append("rate read from a bare decimal")

    for kind, pat in KIND_RULES:
        if re.search(pat, low):
            p.kind = kind
            break
    p.floating = bool(re.search(r"floating|variable|sofr|libor|euribor|\bfrn\b", low))
    for code, pat in CURRENCIES:
        if re.search(pat, low):
            p.currency = code
            break

    word_years = _words_to_years(words)
    m = DUE_YEAR.search(norm)
    rng = YEAR_RANGE.search(norm)
    if m and rng and rng.group(1) == m.group(1) and rng.group(1) != rng.group(2):
        # P43: "Oregon And Arizona Bonds Due 2035 To 2040" is a series of bonds on one line, not a 2035
        # bond (Intel, Week 4 fresh held-out check). No single maturity, so no match key.
        p.notes.append("due-year range — a series, not one maturity (P43)")
    elif m:
        p.maturity_year = int(m.group(1))
    elif word_years and re.search(r"\bdue\b|matur", low):
        p.maturity_year = word_years[-1]
    else:
        rng = YEAR_RANGE.search(norm)
        month_years = {int(y) for _, y in MONTH_YEAR.findall(norm)}
        years = [int(y) for y in YEAR.findall(norm)] + word_years
        dated = [int(y) * 100 + MONTH_NUM[mo.lower().rstrip(".")] for mo, y in MONTH_YEAR.findall(norm)
                 if mo.lower().rstrip(".") in MONTH_NUM]
        if rng:
            p.notes.append("year range — a series, not one maturity")
        elif dated and as_of_month and p.kind in ("notes", "convertible") and max(dated) >= as_of_month:
            # a month on or after the report's own period end cannot be an issue date: Broadcom's
            # assumed VMware notes are named by due date, `May2025SeniorNotes`, `November2025SeniorNotes`
            p.maturity_year = max(dated) // 100
            p.notes.append("month-year on or after the report: read as maturity")
        elif years and as_of_year and p.kind in ("notes", "convertible") and max(years) > as_of_year:
            # a bond cannot have been issued after the report it appears in, so a later year is
            # its maturity: "2029 Notes", "May 2029 Notes", "Two Thousand Thirty Three Senior Notes"
            p.maturity_year = max(years)
            p.notes.append("undated year after the report: read as maturity")
        elif years and not month_years and p.kind in ("notes", "convertible") and p.rate is not None:
            p.maturity_year = years[-1]      # "4.75% Notes 2031": with a coupon the year is the maturity
        elif years and not month_years and p.kind == "convertible":
            p.maturity_year = years[-1]      # "Convertible Notes, 2030"
        elif years:
            p.notes.append("year present but not marked as a maturity")
        # P18: an issue-date group — "March 2026 Senior Notes", "A2026 US Dollar Notes", "November 2025 Debt"
        if p.maturity_year is None and p.rate is None and p.kind == "notes" and (
                month_years or re.search(r"^\s*a\s*20\d\d\b|\b20\d\d\s*(us\s*dollar|euro|usd|eur|notes offering)|issued?\s+in|offering", low)):
            p.offering = True
    # Microsoft numbers its issuances instead of its bonds: `IssuanceOfLongTermDebtEight` is one
    # issuance date carrying several bonds ($19.8 bn), so it is an offering whatever else it says
    if p.maturity_year is None and re.search(r"\bissuances?\b", low) and p.kind in ("notes", None):
        p.offering = True
        p.kind = "notes"
    # One member naming two bonds is a deal, not a bond: AMD's "4.319% Senior Note Due 2028 And
    # 4.212% Senior Note Due 2026" is the $1.5 bn total of two bonds it also tags one by one.
    rates = {float(r) for r in RATE_BARE.findall(norm)}
    due_years = {int(y) for y in DUE_YEAR.findall(norm)}
    pair = re.search(r"(?<!\d)(20\d\d)\s*(?:and|&)\s*(20\d\d)(?!\d)", norm, re.I)   # "due 2027 and 2028"
    if pair and pair.group(1) != pair.group(2):
        due_years |= {int(pair.group(1)), int(pair.group(2))}
    if p.kind in ("notes", "convertible") and (len(rates) > 1 or len(due_years) > 1):
        p.offering, p.rate, p.rate_digits, p.maturity_year = True, None, None, None
        p.notes.append("combined member: names several bonds")
    return p


def parse_member(name: str, label: str | None = None, as_of_year: int | None = None,
                 as_of_month: int | None = None) -> ParsedMember:
    """Label first (it is the filer's own human text), name second; fields fill from either.

    `as_of_year` is the year of the report the member appears in, `as_of_month` its period end as
    YYYYMM. Without them an undated year ("2029 Notes") stays unread, because it could be an issue
    year (P18); with them, a year after the report — or a month on or after its period end — can
    only be a maturity."""
    from_name = _parse_text(split_camel(name), as_of_year, as_of_month)
    from_name.source = "name"
    if not label:
        return from_name
    from_label = _parse_text(re.sub(r"\[member\]|\bmember\b", " ", label, flags=re.I), as_of_year, as_of_month)
    from_label.source = "label"
    out = from_label
    for f in ("rate", "rate_digits", "maturity_year", "kind", "currency"):
        if getattr(out, f) is None and getattr(from_name, f) is not None:
            setattr(out, f, getattr(from_name, f))
            out.source = "label+name"
    out.floating = out.floating or from_name.floating
    if any("combined member" in n for n in from_name.notes + from_label.notes):
        out.rate = out.rate_digits = out.maturity_year = None
        out.offering = True
        out.notes = sorted(set(out.notes + ["combined member: names several bonds"]))
    out.offering = (out.offering or from_name.offering) and out.maturity_year is None
    if from_name.rate is not None and out.rate is not None and abs(from_name.rate - out.rate) > 0.0051:
        out.notes.append(f"label rate {out.rate} disagrees with name rate {from_name.rate}")
    return out


MONTH_NUM = {m: i for i, m in enumerate(("january", "february", "march", "april", "may", "june", "july", "august",
                                         "september", "october", "november", "december"), 1)}
MONTH_NUM.update({m[:3]: i for m, i in list(MONTH_NUM.items())} | {"sept": 9})


def issue_period(name: str, label: str | None = None) -> str | None:
    """When an offering member was issued, as 'YYYY-MM' or 'YYYY' (P18, for L2 grading).

    `November2025Debt` -> '2025-11'; `January2021SeniorNotesTranche` -> '2021-01';
    `A2026USDollarNotes` -> '2026'; `IssuanceOfLongTermDebtEight` -> None (no date in the name).
    Only meaningful for offerings: on a bond the year is usually the maturity."""
    for text in (label, split_camel(name)):
        if not text:
            continue
        low = " ".join(_fix_typos(text.split())).lower()
        m = MONTH_YEAR.search(low)
        if m:
            return f"{int(m.group(2)):04d}-{MONTH_NUM[m.group(1).rstrip('.')]:02d}"
        words = _words_to_years(low.split())
        month = next((MONTH_NUM[w] for w in low.split() if w in MONTH_NUM), None)
        if words and month:
            return f"{words[0]:04d}-{month:02d}"
        m = re.search(r"(?<!\d)(20\d\d)(?!\d)", low)
        if m:
            return m.group(1)
        if words:
            return str(words[0])
    return None


def rates_match(a: float | None, b: float | None, tol: float = 0.0051) -> bool:
    """P17: the bulk notes data rounds 6.125% to 6.13%, so two rates match within half a basis
    point of the rounding step."""
    return a is not None and b is not None and abs(a - b) <= tol
