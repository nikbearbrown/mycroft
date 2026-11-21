"""Investigators (DESIGN.md §7.3, week 6): one per open question the ledger engine raised, run in parallel, at most
two rounds per episode.

The engine refuses to guess. When an event cannot be placed it becomes a question; an investigator looks for the
missing fact, cites where it found it, and hands the engine an **amendment** (`ledger/engine.py: amend`): drop the
event, or set the field it lacked — with the passage or ledger row that states it. The engine then re-runs merge →
ledger → checks. Whatever an investigator cannot settle stays an open question in the record. Rule 1 still holds:
the model points at a passage, code reads the value.

  new_without_amount   (P56) a new bond with no amount. First, code: does the opening ledger already hold a bond
                       with this coupon and year, in any currency (a euro note printed in dollars)? Then it is not
                       new — dropped. Otherwise the model is shown the filing's passages that name the coupon or the
                       year and asked whether the filing *offers* these notes, and which passage states their amount;
                       code parses the amount. Not offered → dropped as existing debt described in the filing.
  new_without_maturity a new bond with no maturity year: the model points at the passage stating its due date among
                       the filing's passages that name its amount or coupon; code parses the year.
  exit_of_unknown      a repayment or redemption that matched nothing. Code tries the ledger with a relaxed key:
                       the same coupon and year in another currency; the same year and principal with no coupon; the
                       only bond with that coupon when the event names no year. A match rewrites the event's identity
                       to the held bond's (citing the ledger row). Otherwise it stays open: the bond was issued
                       before the opening report and is not in the opening ledger, or the event is misread.
  launch_not_priced    (P57) a proposed offering with no priced bond after it in the window: nothing to read (the
                       window's filings were all triaged and read); stays open, not applied.

What an investigator decides — whether a filing offers the notes it names, which passage states a value — is a
model judgment (P8) and is flagged; every value it supplies was parsed by code from a cited passage or comes from
the opening ledger row it matched.
"""

from __future__ import annotations

import json
import re
import time

from ...ledger import engine
from ...ledger import values as V
from . import reader as rd

RATE_TOL = 0.005
MAX_ROUNDS = 2
MAX_PASSAGES = 25

SCHEMA = {"type": "object", "properties": {
    "offered_in_this_filing": {"type": "boolean"},
    "passage": {"type": ["string", "null"]}}, "required": ["offered_in_this_filing", "passage"]}

PROMPT_AMOUNT = (
    "A {form} filing names the {what}. Below are passages from it, each with an id.\n"
    "1. Does this filing OFFER or ISSUE these notes (a new sale), or does it only describe notes the company already "
    "has outstanding (for example in a description of existing debt or a capitalization table)?\n"
    "2. If it offers them, give the id of the passage that states the principal amount being offered; else null.\n"
    "Point only; never type a number.\n\nPASSAGES:\n{passages}")
PROMPT_YEAR = (
    "A {form} filing announces {what}. Below are passages from it, each with an id. Give the id of the passage that "
    "states when it matures (its due date or maturity), or null if none does. Set offered_in_this_filing to true if "
    "the filing announces it as new. Point only; never type a number.\n\nPASSAGES:\n{passages}")


def describe(e: dict) -> str:
    c = f"{e['coupon_pct']}%" if e.get("coupon_pct") is not None else "(coupon not stated)"
    y = f"due {e['maturity_year']}" if e.get("maturity_year") else "(maturity not stated)"
    a = f"{e.get('currency') or 'USD'} {e['principal']:,.0f}" if e.get("principal") else ""
    return " ".join(x for x in (a, c, (e.get("kind") or "notes").replace("_", " "), y) if x)


def _passages_about(docs: list, e: dict) -> list[tuple[str, str]]:
    """The filing's debt passages that name this event's coupon, year or amount."""
    keys = []
    if e.get("coupon_pct") is not None:
        c = e["coupon_pct"]
        keys += [f"{c:.3f}%", f"{c:.2f}%", f"{c:g}%", f"{c:.3f} %", f"{c:g} %"]
    if e.get("maturity_year"):
        keys.append(str(e["maturity_year"]))
    if e.get("principal"):
        p = e["principal"]
        keys += [f"{p:,.0f}", f"{p / 1e6:,.0f} million", f"{p / 1e9:g} billion"]
    found = [(pid, t) for pid, t in rd.select_passages(docs) if any(k in t for k in keys)]
    return found[:MAX_PASSAGES]


def _ask(prompt: str, model: str, host: str | None) -> dict:
    content, _ = rd.call_model(prompt, SCHEMA, model, host, num_predict=256)
    return json.loads(content)


def _held_relaxed(e: dict, ledger: list[dict]) -> dict | None:
    """A held bond the event names under a looser key (see the module notes)."""
    bonds = [i for i in ledger if i.get("kind") == "bond" and i.get("status", "outstanding") == "outstanding"]
    c, y, p = e.get("coupon_pct"), e.get("maturity_year"), e.get("principal")
    if c is not None and y:
        hits = [i for i in bonds if i.get("maturity_year") == y and i.get("coupon_pct") is not None
                and abs(i["coupon_pct"] - c) <= RATE_TOL]
        if len(hits) == 1:
            return hits[0]
    if c is None and y and p:
        hits = [i for i in bonds if i.get("maturity_year") == y and i.get("principal")
                and abs(i["principal"] - p) <= 0.01 * max(i["principal"], p)]
        if len(hits) == 1:
            return hits[0]
    if c is not None and not y:
        hits = [i for i in bonds if i.get("coupon_pct") is not None and abs(i["coupon_pct"] - c) <= RATE_TOL]
        if len(hits) == 1:
            return hits[0]
    return None


def _ledger_cite(i: dict) -> dict:
    return {"accession": (i.get("source") or {}).get("adsh") or (i.get("source") or {}).get("accession") or "opening",
            "accepted": None, "form": "opening ledger",
            "cites": {"identity": {"id": json.dumps(i.get("source") or {"id": i.get("id")})[:200],
                                   "text": f"{i.get('coupon_pct')}% {i.get('maturity_year')} {i.get('currency')}",
                                   "found": "ledger"}}}


def investigate(q: dict, opening: list[dict], docs_for, model: str = "qwen3:4b", host: str | None = None,
                gpu=None) -> dict:
    """One open question → {"question", "resolution", "amendment" | None, "model_judgment", "seconds"}.
    `docs_for(accession)` returns the filing's parsed documents (main document first)."""
    t0 = time.time()
    e = q["event"]
    fp = engine.fingerprint(e)
    out = {"type": q["type"], "event": describe(e), "accession": e.get("accession"), "fingerprint": fp,
           "amendment": None, "model_judgment": False}

    def done(resolution: str, amendment: dict | None = None, judged: bool = False):
        out.update({"resolution": resolution, "amendment": amendment, "model_judgment": judged,
                    "seconds": round(time.time() - t0, 2)})
        return out

    if q["type"] == "launch_not_priced":
        return done("open: no priced bond in the window's filings")

    if q["type"] == "exit_of_unknown":
        held = _held_relaxed(e, opening)
        if held is None:
            return done("open: matches no bond in the opening ledger, even on a looser key")
        return done(f"matched held bond {held.get('coupon_pct')}% {held.get('maturity_year')} {held.get('currency')} "
                    "on a looser key",
                    {"fingerprint": fp, "resolution": "exit matched on a looser key",
                     "set": {"currency": held.get("currency"), "coupon_pct": held.get("coupon_pct"),
                             "maturity_year": held.get("maturity_year")},
                     "sources": [_ledger_cite(held)]})

    if q["type"] == "new_without_amount":
        held = _held_relaxed(e, opening)
        if held is not None:
            return done(f"already held: {held.get('coupon_pct')}% {held.get('maturity_year')} {held.get('currency')}",
                        {"fingerprint": fp, "drop": True, "resolution": "already held (opening ledger)"})

    if q["type"] not in ("new_without_amount", "new_without_maturity"):
        return done("open: no investigator for this question")
    try:
        docs = docs_for(e.get("accession"))
    except Exception as ex:  # noqa: BLE001 — a filing that cannot be opened leaves the question open
        return done(f"open: filing could not be opened ({ex!s:.60})")
    passages = _passages_about(docs, e)
    if not passages:
        return done("open: no passage in the filing names this bond")
    text = "\n".join(f"[{pid}] {t[:700]}" for pid, t in passages)
    prompt = (PROMPT_AMOUNT if q["type"] == "new_without_amount" else PROMPT_YEAR).format(
        form=e.get("form") or "SEC", what=describe(e), passages=text)
    try:
        if gpu is not None:
            with gpu:
                ans = _ask(prompt, model, host)
        else:
            ans = _ask(prompt, model, host)
    except (json.JSONDecodeError, OSError) as ex:
        return done(f"open: model answer failed ({ex!s:.60})")
    by_id = dict(passages)
    if q["type"] == "new_without_amount" and not ans.get("offered_in_this_filing"):
        return done("not offered in this filing: existing notes it describes",
                    {"fingerprint": fp, "drop": True, "resolution": "existing notes described in the filing (model)"},
                    judged=True)
    pid = ans.get("passage")
    if pid not in by_id:
        return done("open: the model named no passage (or one not shown)", judged=True)
    passage = by_id[pid]
    if q["type"] == "new_without_amount":
        amt = _amount_near(passage, e)
        if amt is None:
            return done("open: no amount in the passage named", judged=True)
        cite = {"principal": {"id": pid, "text": amt[2], "found": "investigator"}}
        return done(f"amount read: {amt[1] or e.get('currency') or 'USD'} {amt[0]:,.0f}",
                    {"fingerprint": fp, "resolution": "amount read by an investigator",
                     "set": {"principal": amt[0]} | ({"currency": amt[1]} if amt[1] else {}),
                     "sources": [{"accession": e.get("accession"), "accepted": e.get("accepted"), "form": e.get("form"),
                                  "cites": cite}]}, judged=True)
    m = V.DUE_YEAR.search(passage)
    year = int(m.group(1)) if m else None
    if not year:
        return done("open: no due date in the passage named", judged=True)
    if year < int((e.get("accepted") or "0000")[:4]):
        # a new bond cannot mature before the year it is announced: the passage is about something else
        return done(f"open: the passage named gives {year}, before the filing's own year", judged=True)
    cite = {"maturity": {"id": pid, "text": str(year), "found": "investigator"}}
    return done(f"maturity read: {year}",
                {"fingerprint": fp, "resolution": "maturity read by an investigator", "set": {"maturity_year": year},
                 "sources": [{"accession": e.get("accession"), "accepted": e.get("accepted"), "form": e.get("form"),
                              "cites": cite}]}, judged=True)


AMOUNT_TEXT = re.compile(r"(?:US\$|U\.S\.\$|\$|€|£|CHF|EUR|USD)\s?\d[\d,.]*(?:\s*(?:million|billion))?", re.I)


def _amount_near(passage: str, e: dict) -> tuple[float, str | None, str] | None:
    """The amount closest to the bond's coupon (or year) in the passage: (value, currency, the words)."""
    anchors = []
    if e.get("coupon_pct") is not None:
        for f in (f"{e['coupon_pct']:.3f}%", f"{e['coupon_pct']:.2f}%", f"{e['coupon_pct']:g}%"):
            i = passage.find(f)
            if i >= 0:
                anchors.append(i)
    if e.get("maturity_year"):
        i = passage.find(str(e["maturity_year"]))
        if i >= 0:
            anchors.append(i)
    best = None
    for m in AMOUNT_TEXT.finditer(passage):
        parsed = V.parse_amount(m.group(0))
        if not parsed or parsed[0] < 1e6:
            continue
        d = min((abs(m.start() - a) for a in anchors), default=0)
        if best is None or d < best[0]:
            best = (d, parsed[0], parsed[1], m.group(0))
    return (best[1], best[2], best[3]) if best else None
