"""The `event reader` node (DESIGN.md §7.3): one debt-relevant filing in, structured debt events out,
every value pointing at the words it came from.

DESIGN.md §7.1 rule 1 — the AI never types a number. The reader works in three steps:

1. **Passages (code).** The filing's documents are opened through the `docs` store (so the
   point-in-time rule holds) and cut into addressable sentences and table rows. Only the passages
   that look like they state a debt term are kept: a rate, a "due 20xx", a money amount, next to a
   debt word; term-sheet rows ("Coupon", "Maturity Date", "Principal Amount"); and each kept table's
   header row, so a column can be told from its neighbour. Each passage gets an id `d<k>:<span id>`.
2. **Pointing (model).** `qwen3:4b` lists the instruments the filing announces and, for each value,
   **copies the exact words** that state it and gives the id of the passage it copied from. Output
   is forced to a JSON schema (Ollama structured output).
3. **Reading (code).** Each copied value must really be in the passage it cites (`values.grounded`);
   if it is not, the other passages are searched and a value found elsewhere is kept with its true
   id and flagged `relocated`. A value found nowhere is dropped (`ungrounded`) — it is not evidence
   (P3). Code then parses the words: amount and currency, fixed rate, maturity year
   (`ledger/values.py`). The model's own reading of a number is never used.

The output of one filing is a list of `Event`s, each with its citations. A model's choice of *which*
instruments a filing announces, and of each one's action, is a **model judgment** (P8) and is flagged.
"""

from __future__ import annotations

import json
import re
import time
import urllib.request
from dataclasses import asdict, dataclass, field

from ... import config
from ...ledger import values as V

ACTIONS = ["new_issue", "add_on", "new_facility", "draw", "amendment", "redemption", "repayment", "tender_offer",
           "exchange", "conversion", "other"]
ACTION_CLASS = {"new_issue": "new", "add_on": "new", "new_facility": "new", "draw": "new", "amendment": "amend",
                "redemption": "exit", "repayment": "exit", "tender_offer": "exit", "exchange": "exit",
                "conversion": "exit", "other": "other"}
KINDS = ["notes", "convertible_notes", "term_loan", "revolving_facility", "delayed_draw_facility", "other"]

RATE_A = re.compile(r"\d\s*%|\bper annum\b|\binterest rate\b|\bcoupon\b", re.I)
DUE_A = re.compile(r"\bdue\s+(?:in\s+)?20\d\d|\bmatur|\bexpir|20[2-9]\d\s+notes", re.I)
AMOUNT_A = re.compile(r"[$€£]\s?\d|\b\d{1,3}(?:,\d{3}){2,}\b|\b(?:million|billion)\b", re.I)
DEBT_A = re.compile(r"\bnotes?\b|\bdebentures?\b|\bbonds?\b|term loan|credit agreement|credit facilit|revolving|"
                    r"\bcommitments?\b|\bborrow|principal amount|\bloans?\b|indebtedness", re.I)
ACT_A = re.compile(r"redeem|redemption|tender|repurchas|repa(?:y|id)|amend|priced|pricing|offering|issued|entered into",
                   re.I)
TERM_ROW = re.compile(r"principal amount|aggregate principal|coupon|interest rate|maturity|title of (?:the )?securit|"
                      r"security type|price to public|issue price|settlement date|trade date", re.I)
MAX_PASSAGES, MAX_CHARS, PASSAGE_CHARS = 70, 14_000, 900
NO_VALUE = {"null", "none", "n/a", "na", "not stated", "-", "—"}
NUM_CTX, NUM_PREDICT = 12_288, 2_048


@dataclass
class Event:
    action: str
    action_class: str            # new | exit | amend | other
    kind: str
    currency: str | None
    principal: float | None
    coupon_pct: float | None
    floating: bool
    maturity_year: int | None
    cites: dict = field(default_factory=dict)      # field -> {"id", "text", "found": cited|relocated}
    dropped: list = field(default_factory=list)    # fields whose copied words were in no passage
    model_judgment: bool = True


@dataclass
class ReaderResult:
    accession: str
    events: list[Event]
    passages: int
    seconds: float
    error: str | None = None
    raw: str | None = None


# ------------------------------------------------------------------------------------ passages
def _score(text: str) -> int:
    return (2 * bool(RATE_A.search(text)) + 2 * bool(DUE_A.search(text)) + 2 * bool(AMOUNT_A.search(text))
            + bool(DEBT_A.search(text)) + bool(ACT_A.search(text)))


def select_passages(docs: list) -> list[tuple[str, str]]:
    """(id, text) of the passages worth showing, in document order."""
    cands = []           # (score, order, id, text)
    order = 0
    for k, doc in enumerate(docs):
        for s in doc.sentences:
            t = s["text"]
            sc = _score(t)
            if sc >= 4 and DEBT_A.search(t):
                cands.append((sc, order, f"d{k}:{s['id']}", t))
            order += 1
        for tb in doc.tables:
            keep = []
            for i, r in enumerate(tb.rows):
                t = " | ".join(r)
                sc = _score(t) + 3 * bool(TERM_ROW.search(t))
                if sc >= 4:
                    keep.append((sc, order + i, f"d{k}:{tb.id}.r{i}", t))
            if keep and not any(x[2].endswith(".r0") for x in keep) and tb.rows:
                keep.append((max(x[0] for x in keep), order, f"d{k}:{tb.id}.r0", " | ".join(tb.rows[0])))  # header
            cands += keep
            order += len(tb.rows)
    best = sorted(cands, key=lambda x: (-x[0], x[1]))
    chosen, used = [], 0
    for sc, o, pid, t in best:
        t = t[:PASSAGE_CHARS]
        if len(chosen) >= MAX_PASSAGES or used + len(t) > MAX_CHARS:
            continue
        chosen.append((o, pid, t))
        used += len(t)
    return [(pid, t) for _, pid, t in sorted(chosen)]


# ------------------------------------------------------------------------------------ the model
SCHEMA = {"type": "object", "properties": {"instruments": {"type": "array", "items": {"type": "object", "properties": {
    "action": {"type": "string", "enum": ACTIONS},
    "kind": {"type": "string", "enum": KINDS},
    "principal_text": {"type": ["string", "null"]}, "principal_id": {"type": ["string", "null"]},
    "coupon_text": {"type": ["string", "null"]}, "coupon_id": {"type": ["string", "null"]},
    "maturity_text": {"type": ["string", "null"]}, "maturity_id": {"type": ["string", "null"]},
    "floating": {"type": "boolean"}},
    "required": ["action", "kind", "principal_text", "principal_id", "coupon_text", "coupon_id", "maturity_text",
                 "maturity_id", "floating"]}}},
    "required": ["instruments"]}
PROMPT = (
    "You read SEC filings for a tracker of corporate borrowing. Below are numbered passages from ONE filing ({form}).\n"
    "List every bond, note, loan or credit facility whose issue, pricing, borrowing, entry into, amendment, redemption, "
    "repayment, tender or exchange THIS filing announces. One entry per instrument: each tranche of a multi-tranche "
    "deal is its own entry. Do NOT list debt that is only mentioned: tables of existing debt or capitalization, notes "
    "the proceeds will be used to repay (they are not redeemed by this filing), benchmark Treasuries, debt repaid in the "
    "past, examples in definitions.\n"
    "action: new_issue = notes or bonds offered, priced or issued; new_facility = a loan or credit facility entered into; "
    "draw = a borrowing under an existing facility; amendment = an existing agreement changed; redemption / repayment / "
    "tender_offer / exchange / conversion = debt retired.\n"
    "For each value, COPY the exact words from ONE passage and give that passage's id (like d0:s12 or d0:t2.r3):\n"
    "- principal: the amount of that instrument alone (for a facility, its total commitment; for a redemption, the "
    "amount redeemed), copied with its currency sign, e.g. \"$1,250,000,000\" or \"€750 million\";\n"
    "- coupon: its fixed annual interest rate, e.g. \"4.750%\" (null if floating or not stated; set floating=true "
    "if the rate is floating);\n"
    "- maturity: the words that state when it matures, e.g. \"2031\" or \"June 1, 2031\".\n"
    "Use null when the filing does not state a value. Never compute, convert or round a value: copy it.\n\n"
    "PASSAGES:\n{passages}")


def call_model(prompt: str, schema: dict, model: str = "qwen3:4b", host: str | None = None,
               num_predict: int = NUM_PREDICT, num_ctx: int = NUM_CTX) -> tuple[str, dict]:
    req = {"model": model, "stream": False, "format": schema, "keep_alive": "10m", "think": False,
           "messages": [{"role": "user", "content": prompt}],
           "options": {"temperature": 0, "num_ctx": num_ctx, "num_predict": num_predict}}
    with urllib.request.urlopen(urllib.request.Request(f"{host or config.OLLAMA_HOST}/api/chat",
                                                       data=json.dumps(req).encode(),
                                                       headers={"Content-Type": "application/json"}), timeout=600) as r:
        out = json.load(r)
    return out["message"]["content"], out


def ask_model(passages: list[tuple[str, str]], form: str, model: str = "qwen3:4b", host: str | None = None) -> str:
    text = "\n".join(f"[{pid}] {t}" for pid, t in passages)
    content, _ = call_model(PROMPT.format(form=form, passages=text), SCHEMA, model, host)
    return content


# ------------------------------------------------------------------------------------ reading
def _locate(copied: str | None, cited: str | None, passages: dict[str, str]) -> tuple[str | None, str | None, str | None]:
    """(id, span text, how) for a copied value: in the cited passage, else in another one, else nowhere."""
    if not copied or not str(copied).strip() or str(copied).strip().lower() in NO_VALUE:
        return None, None, None      # Week 4: the model sometimes writes the *word* "null" for a missing value
    cid = (cited or "").strip().strip("[]")
    if cid and cid not in passages and len({p.split(":")[0] for p in passages}) == 1:
        cid = f"{next(iter(passages)).split(':')[0]}:{cid}"      # "s12" when there is only one document
    if cid in passages and V.grounded(copied, passages[cid]):
        return cid, passages[cid], "cited"
    for pid, t in passages.items():
        if V.grounded(copied, t):
            return pid, t, "relocated"
    return None, None, "ungrounded"


def resolve(answer: dict, passages: list[tuple[str, str]]) -> list[Event]:
    by_id = dict(passages)
    events, seen = [], set()
    for ins in answer.get("instruments") or []:
        cites, dropped = {}, []
        vals = {}
        for f in ("principal", "coupon", "maturity"):
            pid, span, how = _locate(ins.get(f"{f}_text"), ins.get(f"{f}_id"), by_id)
            if how == "ungrounded":
                dropped.append(f)
            elif pid:
                cites[f] = {"id": pid, "text": str(ins.get(f"{f}_text")), "found": how}
                vals[f] = (str(ins.get(f"{f}_text")), span)
        principal = currency = coupon = year = None
        if "principal" in vals:
            copied, span = vals["principal"]
            got = V.parse_amount(copied, default_currency=V.currency_of(span) or "USD")
            if got:
                principal, currency = got
        floating = bool(ins.get("floating"))
        if "coupon" in vals:
            copied, _ = vals["coupon"]
            floating = floating or V.is_floating(copied)
            coupon = V.parse_rate(copied)
        if "maturity" in vals:
            year = V.parse_year(vals["maturity"][0])
        action = ins.get("action") if ins.get("action") in ACTIONS else "other"
        key = (action, principal, coupon, year)
        if key in seen or (principal is None and coupon is None and year is None):
            continue                     # a repeat (8-K and its press release), or nothing grounded at all
        seen.add(key)
        events.append(Event(action, ACTION_CLASS[action], ins.get("kind") if ins.get("kind") in KINDS else "other",
                            currency, principal, coupon, floating, year, cites, dropped))
    # Merge (code): a tranche the model lists twice — once from the cover sentence with its amount, once
    # from a later "interest on the 2030 Notes …" sentence without — is one instrument. An event with no
    # principal that repeats the coupon and year of an event that has one is dropped.
    full = {(e.action_class, e.coupon_pct, e.maturity_year) for e in events if e.principal is not None}
    return [e for e in events if e.principal is not None or e.coupon_pct is None or e.maturity_year is None
            or (e.action_class, e.coupon_pct, e.maturity_year) not in full]


def salvage(raw: str) -> dict | None:
    """The instruments a cut-off answer did complete. A runaway answer (the model repeating itself until
    the output cap) ends mid-object; every instrument closed before that point is still a whole answer.
    Returns None if not even one instrument was completed."""
    for i in range(len(raw) - 1, 0, -1):
        if raw[i] != "}":
            continue
        try:
            ans = json.loads(raw[: i + 1] + "]}")
        except json.JSONDecodeError:
            continue
        if isinstance(ans, dict) and ans.get("instruments"):
            return ans
    return None


def read_filing(docs: list, accession: str, form: str, model: str = "qwen3:4b", host: str | None = None,
                ask=ask_model) -> ReaderResult:
    """`docs`: the filing's parsed documents (from `DocumentStore.open`), main document first."""
    passages = select_passages(docs)
    t0 = time.time()
    if not passages:
        return ReaderResult(accession, [], 0, 0.0, error="no debt passages")
    raw = None
    try:
        raw = ask(passages, form, model, host)
        answer = json.loads(raw)
    except json.JSONDecodeError:
        answer = salvage(raw or "")
        if answer is None:
            return ReaderResult(accession, [], len(passages), round(time.time() - t0, 2), error="answer did not parse",
                                raw=(raw or "")[:2000])
        return ReaderResult(accession, resolve(answer, passages), len(passages), round(time.time() - t0, 2),
                            error="answer cut off; completed instruments kept", raw=raw[:4000])
    return ReaderResult(accession, resolve(answer, passages), len(passages), round(time.time() - t0, 2), raw=raw[:4000])


def to_json(r: ReaderResult) -> dict:
    return asdict(r)
