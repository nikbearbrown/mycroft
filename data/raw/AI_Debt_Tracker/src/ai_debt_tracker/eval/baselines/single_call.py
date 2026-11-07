"""Baseline B2 (DESIGN.md §9.3): one model call per document, no pointing, no merging, no checks.

The "just ask a model" approach, exactly as the Week 1 bake-off asked it (`scripts/bakeoff.py`): the
model gets the first 24,000 characters of one document and must list every instrument it announces,
typing each value itself as a number. Same model as the event reader (`qwen3:4b`, the Week 1 pick —
the design first named `qwen3:8b` for B2, but holding the model fixed makes the comparison about the
method, not the model). Instruments from a filing's documents are pooled, exact repeats removed.
"""

from __future__ import annotations

import json
import time

SCHEMA = {"type": "object", "properties": {"instruments": {"type": "array", "items": {"type": "object", "properties": {
    "action": {"type": "string", "enum": ["new_issue", "add_on", "new_facility", "draw", "redemption", "repayment",
                                          "tender_offer", "exchange", "amendment", "other"]},
    "kind": {"type": "string", "enum": ["notes", "convertible_notes", "term_loan", "revolving_facility",
                                        "delayed_draw_facility", "other"]},
    "currency": {"type": "string"},
    "principal": {"type": ["number", "null"]},
    "coupon_pct": {"type": ["number", "null"]},
    "maturity_year": {"type": ["integer", "null"]}},
    "required": ["action", "kind", "currency", "principal", "coupon_pct", "maturity_year"]}}},
    "required": ["instruments"]}
PROMPT = ("You read SEC filings about corporate debt. List every bond, note or loan facility that this document "
          "announces as being issued, priced, borrowed, entered into, redeemed, repaid, tendered for or exchanged. "
          "One entry per instrument (a deal with several tranches has one entry per tranche). For each: the action; "
          "the kind; the currency (ISO code); the principal amount of that instrument alone as a plain number in units "
          "of the currency (e.g. 1250000000 for $1.25 billion; for a facility, its total commitment); the annual "
          "interest rate in percent (null if floating or not stated); and the year it matures (null if not stated). "
          "Use only what the document says. Answer with JSON only.\n\nDOCUMENT:\n")
VISIBLE_CHARS, NUM_CTX, NUM_PREDICT = 24_000, 8192, 2048
CLASS = {"new_issue": "new", "add_on": "new", "new_facility": "new", "draw": "new", "amendment": "amend",
         "redemption": "exit", "repayment": "exit", "tender_offer": "exit", "exchange": "exit", "other": "other"}


def extract(texts: list[str], call, model: str = "qwen3:4b") -> tuple[list[dict], float, int]:
    """`call(prompt, schema, model, num_predict, num_ctx) -> content` is the model client (the reader's).
    Returns (instruments, seconds, answers that did not parse)."""
    out, seen, bad, t0 = [], set(), 0, time.time()
    for text in texts:
        content = call(PROMPT + text[:VISIBLE_CHARS], SCHEMA, model, NUM_PREDICT, NUM_CTX)
        try:
            ans = json.loads(content)
        except json.JSONDecodeError:
            bad += 1
            continue
        for a in ans.get("instruments") or []:
            key = (a.get("action"), a.get("principal"), a.get("coupon_pct"), a.get("maturity_year"))
            if key in seen:
                continue
            seen.add(key)
            out.append({"action_class": CLASS.get(a.get("action"), "other"), "kind": a.get("kind"),
                        "currency": (a.get("currency") or "USD").upper()[:3], "principal": a.get("principal"),
                        "coupon_pct": a.get("coupon_pct"), "maturity_year": a.get("maturity_year")})
    return out, round(time.time() - t0, 2), bad
