"""The `triage` node (DESIGN.md §7.3): which filings in the window are about debt, and what happened.

Rules first, the model only for the doubtful middle — the design's §7.1 rule 6 ("use the AI only
where judgment is needed"). A filing is **debt-relevant** when it announces or documents a change to
the company's (or a subsidiary's) borrowings: new bonds or notes (offering, pricing, closing); a new,
amended, drawn, repaid or terminated loan or credit facility; a commercial paper programme;
redemption, repurchase, tender, exchange or conversion of notes; default or acceleration. Earnings
releases that merely mention debt balances, equity offerings, management changes, votes, stock
buybacks and dividends are not. (The same definition labelled the evaluation set before triage ran.)

Rules, in order — each decision records which rule made it:

  R1  8-K item 2.03 (a new direct financial obligation) or 2.04 (acceleration)      → relevant
  R2  424B prospectus whose cover offers notes / debentures                        → relevant
      424B whose cover offers only shares, warrants or units                       → not relevant
  R3  FWP term sheet for notes                                                     → relevant
  R4  a debt announcement in the lead of the 8-K or its press release
      (priced / closed an offering of notes, entered a credit agreement, called notes for
      redemption, launched a tender or exchange offer …)                           → relevant
  R5  no debt vocabulary anywhere in what was read                                 → not relevant
  R6  everything else (debt words, but not in the lead: earnings releases, 8.01s, merger 8-Ks)
      → `qwen3:4b` decides, with the passages around the debt words; its answer is a
        **model judgment** (P8), labelled as such, and its quoted evidence must appear in the text.

The event type comes from the same lead text (or the model): new_bond_issue, new_loan_or_facility,
facility_amendment, redemption_or_repayment, tender_or_exchange, conversion, other_debt_event.
"""

from __future__ import annotations

import json
import re
import time
import urllib.request
from dataclasses import asdict, dataclass

from ... import config

EVENT_TYPES = ["new_bond_issue", "new_loan_or_facility", "facility_amendment", "redemption_or_repayment",
               "tender_or_exchange", "conversion", "other_debt_event", "not_debt"]
NOTE_WORDS = r"(?:senior\s+|subordinated\s+|secured\s+|unsecured\s+|convertible\s+|exchangeable\s+|guaranteed\s+|" \
             r"fixed[- ]rate\s+|floating[- ]rate\s+)*(?:notes|debentures|bonds)"
NOTE_OFFER = re.compile(rf"\d{{1,2}}\.\d{{1,4}}\s?%\s+{NOTE_WORDS}|floating[- ]rate\s+notes|{NOTE_WORDS}\s+due\s+20\d\d|"
                        r"aggregate principal amount", re.I)
EQUITY = re.compile(r"\bshares of (?:our |its )?(?:class [ab] )?common stock\b|\bcommon stock\b|\bwarrants\b|\bunits\b|"
                    r"\bdepositary shares\b|\bpreferred stock\b", re.I)
DEBT_WORDS = re.compile(r"\bnotes?\b(?! to (?:the )?(?:condensed )?(?:consolidated )?financial)|\bdebentures?\b|\bbonds?\b|"
                        r"credit agreement|credit facilit|term loan|revolving|indenture|borrow|\bdebt\b|"
                        r"commercial paper|principal amount|redemption|tender offer|exchange offer", re.I)
def _rx(pattern: str) -> re.Pattern:
    """`[^.]` means 'within one sentence' — but a full stop inside "9.250%" or "U.S." does not end a
    sentence, so only a full stop followed by whitespace does."""
    return re.compile(pattern.replace("[^.]", r"(?:[^.]|\.(?!\s))"), re.I)


LEAD = [  # (event type, pattern) — a debt announcement stated in the lead of a filing
    ("tender_or_exchange", _rx(r"(?:commenced|announce[ds]?|launch(?:ed|es)?|results of|expiration of|early "
                               r"tender)[^.]{0,120}(?:tender offer|exchange offer|consent solicitation)")),
    ("redemption_or_repayment", _rx(r"(?:notice of (?:full |partial |conditional )?redemption|(?:will|to|elected to|has "
                                    r"elected to|intends to) redeem|called (?:for redemption )?(?:all|the)|"
                                    r"redemption of (?:all|the)[^.]{0,60}(?:notes|debentures)|repaid in full|"
                                    r"repurchase of[^.]{0,60}notes)")),
    ("conversion", _rx(r"(?:settle|settlement of)[^.]{0,40}conversions?|conversion of[^.]{0,60}notes")),
    ("facility_amendment", _rx(r"(?:amendment|amended and restated|extension)[^.]{0,80}(?:credit agreement|credit "
                               r"facility|term loan|loan agreement|revolving)")),
    ("new_loan_or_facility", _rx(r"(?:entered into|executed|closed)[^.]{0,120}(?:credit agreement|credit facility|"
                                 r"term loan|loan agreement|delayed draw|bridge (?:loan|facility)|financing "
                                 r"agreement)|commercial paper program")),
    ("new_bond_issue", _rx(r"(?:pric(?:ed|ing)|completed|closed|consummated|issued|offering of|proposed "
                           r"offering|intends to offer)[^.]{0,160}" + NOTE_WORDS)),
]
LEAD_CHARS = 2_500
MODEL_CHARS = 6_000


@dataclass
class TriageResult:
    accession: str
    form: str
    items: list[str]
    relevant: bool
    event_type: str
    decided_by: str          # "rule R1".."rule R5" | "model"
    model_judgment: bool
    evidence: str
    seconds: float = 0.0


def lead_event(text: str) -> str | None:
    lead = text[:LEAD_CHARS]
    for event, pat in LEAD:
        if pat.search(lead):
            return event
    return None


def event_from_text(text: str) -> str:
    return lead_event(text) or next((e for e, p in LEAD if p.search(text)), "other_debt_event")


def _quote(text: str, pat: re.Pattern, width: int = 160) -> str:
    m = pat.search(text)
    if not m:
        return ""
    return " ".join(text[max(0, m.start() - 40): m.end() + width].split())


def rules(form: str, items: list[str], texts: dict[str, str]) -> TriageResult | None:
    """Decide by rule, or return None for the model. `texts` maps document type ("8-K", "EX-99.1",
    "424B5", "FWP" …) to the start of that document's plain text."""
    main = next((t for k, t in texts.items() if k == form or k.startswith(form[:4])), "")
    lead_docs = [main] + [t for k, t in texts.items() if k.startswith("EX-99")]
    allt = " ".join(texts.values())

    def res(rel, event, rule, evidence):
        return TriageResult("", form, items, rel, event if rel else "not_debt", f"rule {rule}", False, evidence[:300])

    if form.startswith("8-K") and ({"2.03", "2.04"} & set(items)):
        return res(True, event_from_text(allt), "R1", f"8-K item {'2.03' if '2.03' in items else '2.04'}")
    if form.startswith("424B"):
        cover = main[:8_000]
        if NOTE_OFFER.search(cover):
            return res(True, "new_bond_issue", "R2", _quote(cover, NOTE_OFFER))
        if EQUITY.search(cover):
            return res(False, "not_debt", "R2", _quote(cover, EQUITY))
    if form == "FWP":
        if NOTE_OFFER.search(main[:8_000]):
            return res(True, "new_bond_issue", "R3", _quote(main, NOTE_OFFER))
    for t in lead_docs:
        ev = lead_event(_strip_boilerplate(t))
        if ev:
            body = _strip_boilerplate(t)
            pat = next(p for e, p in LEAD if e == ev)
            return res(True, ev, "R4", _quote(body, pat))
    if not DEBT_WORDS.search(_strip_boilerplate(allt)):
        return res(False, "not_debt", "R5", "no debt vocabulary in what was read")
    return None


def _strip_boilerplate(text: str) -> str:
    """Drop the 8-K cover page (registrant name, addresses, check boxes) so 'the lead' is the
    first item's text, where the news is."""
    m = re.search(r"Item\s+\d\.\d{2}", text)
    if m and m.start() < 12_000:
        return text[m.start():]
    return text


SCHEMA = {"type": "object", "properties": {
    "relevant": {"type": "boolean"},
    "event_type": {"type": "string", "enum": EVENT_TYPES},
    "evidence": {"type": "string"}},
    "required": ["relevant", "event_type", "evidence"]}
PROMPT = (
    "You triage SEC filings for a tracker of corporate borrowing. A filing is DEBT-RELEVANT only if it announces or "
    "documents a change to the company's (or a subsidiary's) borrowings: new bonds or notes (offering, pricing, closing); "
    "a new, amended, drawn, repaid or terminated loan or credit facility; a commercial paper programme; redemption, "
    "repurchase, tender, exchange or conversion of notes; default or acceleration. NOT relevant: earnings results that "
    "merely mention debt balances, equity offerings, management changes, shareholder votes, stock buybacks, dividends. "
    "Answer with JSON: relevant (true/false), event_type, and evidence = a short quote copied exactly from the text "
    "(empty if not relevant).\n\nFILING: {form}, items {items}\n\nTEXT:\n{text}")


def model_text(texts: dict[str, str]) -> str:
    """What the model reads: the lead of each document, then the passages around debt words."""
    parts, used = [], 0
    for k, t in texts.items():
        body = _strip_boilerplate(t)
        lead = body[:1_500]
        parts.append(f"[{k}] {lead}")
        used += len(lead)
        for m in DEBT_WORDS.finditer(body[1_500:]):
            if used > MODEL_CHARS:
                break
            s = 1_500 + m.start()
            snip = body[max(0, s - 250): s + 350]
            parts.append(f"[{k} …] {snip}")
            used += len(snip)
    return "\n".join(parts)[:MODEL_CHARS + 2_000]


def ask_model(form: str, items: list[str], texts: dict[str, str], model: str = "qwen3:4b",
              host: str | None = None) -> tuple[dict, float]:
    text = model_text(texts)
    req = {"model": model, "stream": False, "format": SCHEMA, "keep_alive": "10m", "think": False,
           "messages": [{"role": "user", "content": PROMPT.format(form=form, items=", ".join(items) or "none", text=text)}],
           "options": {"temperature": 0, "num_ctx": 8192, "num_predict": 300}}
    t0 = time.time()
    with urllib.request.urlopen(urllib.request.Request(f"{host or config.OLLAMA_HOST}/api/chat",
                                                       data=json.dumps(req).encode(),
                                                       headers={"Content-Type": "application/json"}), timeout=300) as r:
        out = json.load(r)
    try:
        ans = json.loads(out["message"]["content"])
    except json.JSONDecodeError:
        # a runaway answer cut off by num_predict: triage is a recall-first filter, so an answer that
        # cannot be read keeps the filing for the event reader — flagged, and counted in the report
        return ({"relevant": True, "event_type": "other_debt_event", "evidence": "", "evidence_found": True,
                 "unparsed": True}, time.time() - t0)
    # grounding check: a quote that is not in the text is not evidence (P3)
    ev = " ".join((ans.get("evidence") or "").split())
    flat = " ".join(text.split())
    ans["evidence_found"] = bool(ev) and ev[:80] in flat
    return ans, time.time() - t0


def triage(form: str, items: list[str], texts: dict[str, str], accession: str = "", model: str = "qwen3:4b",
           host: str | None = None, ask=ask_model) -> TriageResult:
    r = rules(form, items, texts)
    if r is not None:
        r.accession = accession
        return r
    ans, secs = ask(form, items, texts, model, host)
    rel = bool(ans.get("relevant"))
    event = ans.get("event_type") if ans.get("event_type") in EVENT_TYPES else "other_debt_event"
    if rel and event == "not_debt":
        event = "other_debt_event"
    ev = ans.get("evidence") or ""
    if ans.get("unparsed"):
        ev = "[model answer did not parse; kept for the reader]"
    elif rel and not ans.get("evidence_found", True):
        ev = "[quote not found in the text] " + ev
    return TriageResult(accession, form, items, rel, event if rel else "not_debt", "model", True, ev[:300], round(secs, 2))


def to_json(r: TriageResult) -> dict:
    return asdict(r)
