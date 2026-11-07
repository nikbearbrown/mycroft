"""Baseline B1 (DESIGN.md §9.3): regex rules on the filing's text — how far plain pattern matching gets.

One family of patterns, the one the design names: "$X aggregate principal amount of Y% notes due Z",
with its common variants ("$X of Y% notes due Z", a term-sheet title "$X Y% Senior Notes due Z"). One
match is one instrument. The action is an exit when the sentence speaks of redeeming, repurchasing,
tendering or repaying, else new. Loans and facilities have no such pattern, so B1 does not find them —
that is part of what it measures.
"""

from __future__ import annotations

import re

from ...ledger import values as V

AMOUNT = r"(?P<amt>(?:US\$|U\.S\.\$|\$|€|£)\s?\d[\d,]*(?:\.\d+)?(?:\s*(?:million|billion))?)"
RATE = r"(?P<rate>\d{1,2}(?:\.\d{1,4})?)\s?%"
NOTES = r"(?P<words>(?:[A-Za-z][\w-]*\s+){0,5}?)(?:notes|debentures|bonds)"
DUE = r"\s+due\s+(?:(?:in\s+)?\w+\s+\d{1,2},\s+)?(?P<year>20\d\d)"
PATTERN = re.compile(AMOUNT + r"\s+(?:(?:in\s+)?aggregate principal amount\s+of\s+|of\s+)?(?:(?:its|our|the|their)\s+)?"
                     + RATE + r"\s+" + NOTES + DUE, re.I)
EXIT = re.compile(r"redeem|redemption|repurchas|tender|repa(?:y|id)", re.I)


def extract(texts: list[str]) -> list[dict]:
    """Instruments from the text of each document of one filing (sentences or table rows)."""
    out, seen = [], set()
    for text in texts:
        for m in PATTERN.finditer(text):
            got = V.parse_amount(m.group("amt"))
            if not got:
                continue
            principal, currency = got
            rate, year = float(m.group("rate")), int(m.group("year"))
            key = (principal, rate, year)
            if key in seen:
                continue
            seen.add(key)
            sentence = text[max(0, m.start() - 200): m.end() + 100]
            exit_ = bool(EXIT.search(sentence))
            out.append({"action_class": "exit" if exit_ else "new", "kind": "convertible_notes"
                        if "convertible" in m.group("words").lower() else "notes",
                        "currency": currency or "USD", "principal": principal, "coupon_pct": rate,
                        "maturity_year": year, "evidence": " ".join(m.group(0).split())[:200]})
    return out
