"""Matcher v2: the deterministic floor, with an LLM asked only where it can help.

Week 4 measured the deterministic matcher at precision 0.9959 and recall 1.0000
on the golden set. There is almost no headroom, so the question this week is not
"can a language model resolve issuer names" -- it plainly can -- but "does adding
one to *this* pipeline make it better, and at what cost". Those are different
questions and only the second one matters.

--------------------------------------------------------------------------
Where the model is allowed to speak
--------------------------------------------------------------------------
`POLICY_BAND` is the shipping policy. The model is consulted only where the
deterministic matcher is already unsure:

    lei          1.00   never adjudicated -- a registered identifier is identity
    alias        1.00   never adjudicated -- the name IS the company's own name
    >= 0.90             never adjudicated -- the auto-accept band from Week 4
    0.80 - 0.90         adjudicated       -- the review band
    unresolved          adjudicated       -- nothing fired

This is deliberately conservative, and the reason is the failure it prevents:
a model that overrules an LEI match is not adding judgment, it is adding noise
to the one part of the pipeline that was never in doubt.

`POLICY_ALL` overrules everything below an exact match, and exists so the
conservative choice can be *measured* rather than assumed. `POLICY_LLM_ONLY`
ignores the deterministic matcher entirely -- that number says what the model
can do unaided, which is the interesting one for Week 6 and beyond.

--------------------------------------------------------------------------
What the model is shown
--------------------------------------------------------------------------
Issuer name, issuer title, filer, and the candidate list -- exactly what
plan.md specifies, and deliberately no price. The deterministic matcher does
not get price evidence either, so withholding it keeps the comparison a
comparison. Price is what settled the hard labels in Week 4 (docs/
entity_resolution.md section 6) and handing it over would measure a different
system than the one being scored.

The golden set's `company` field is never in the prompt. A test asserts it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from src.resolve.llm import parse_json_object
from src.resolve.match import ALIASES, resolve
from src.resolve.normalize import parse_class

NOT_IN_UNIVERSE = "NOT_IN_UNIVERSE"
UNKNOWN = "UNKNOWN"

# Week 4's measured operating points, docs/entity_resolution.md section 7.
AUTO_ACCEPT = 0.90
REVIEW_FLOOR = 0.80

POLICY_BAND = "band"  # consult in the review band and on unresolved names
POLICY_ALL = "all"  # ablation: overrule everything short of an exact match
POLICY_LLM_ONLY = "llm_only"  # ablation: ignore the deterministic matcher
POLICY_VETO = "veto"  # ship this one -- see below

# --------------------------------------------------------------------------
# POLICY_VETO, and the fact that it was designed after seeing the results
#
# The first measurement (docs/_adjudication_metrics.json, and section 9 of
# docs/entity_resolution.md) is blunt: on the whole golden set the model costs
# 5.1 points of precision. It fixed one holding and broke fourteen.
#
# Every one of those fourteen has the same shape. The deterministic matcher had
# resolved nothing, and the model *promoted* the row to a company on a
# resemblance -- HYPERSCALE DATA to Scale AI, ABL Space Systems to SpaceX,
# COHERE TECHNOLOGIES to Cerebras, and a Fidelity internal security code,
# 'XAI3-FT5O.AF', to X.AI. The one fix has the opposite shape: the matcher had
# claimed OpenAI for a used-car marketplace and the model *demoted* it.
#
# So the model is a good skeptic and a bad proposer, on this corpus, at this
# size. POLICY_VETO grants it only the power it demonstrated: it may withdraw a
# weak deterministic claim, never invent one.
#
# This policy was written after reading the failures, which means the golden set
# motivated it and cannot also validate it -- the same caveat as Week 4's
# dot-TLD fix, and it is stated in section 9 rather than buried here.
# --------------------------------------------------------------------------

CANONICAL = list(ALIASES)

# Ollama constrains decoding to this when the server supports it, which removes
# a whole class of failure -- a confident answer in the wrong shape.
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "company": {"type": "string", "enum": CANONICAL + [NOT_IN_UNIVERSE, UNKNOWN]},
        "share_class": {"type": "string"},
        "confidence": {"type": "number"},
        "reason": {"type": "string"},
    },
    "required": ["company", "share_class", "confidence", "reason"],
}

SYSTEM_PROMPT = """\
You are a securities-filing analyst. You read one holding line from an SEC Form \
N-PORT filing and decide which private company it is a position in.

You answer with a JSON object and nothing else. No prose, no code fences.

The company must be exactly one of the names in the candidate list you are given, \
or one of these two:

  NOT_IN_UNIVERSE - the holding is in some other company. Most holdings are. A \
name that merely resembles a candidate, or shares a common word with one, is \
usually a different company.
  UNKNOWN - the filing names a fund vehicle or shell and does not disclose what \
it holds. You cannot tell, and saying so is the correct answer.

Rules you must follow:

1. Decide from the text you are given. Do not use outside knowledge of who \
invested in whom. If the name does not identify the company, the answer is \
NOT_IN_UNIVERSE or UNKNOWN.
2. UNKNOWN is for "the filing does not say". NOT_IN_UNIVERSE is for "this is a \
different company". They are not interchangeable.
3. A wrapper that discloses its holding - "Fund III LLC (invested in X)" - is a \
position in X. A wrapper that discloses nothing is UNKNOWN.
4. share_class: use PFD:<series> for preferred, COM:CLASS <letter> for common, \
RIGHTS or UNITS if the instrument is not a share, MIXED if one line spans \
several classes, UNKNOWN if the title does not say. Never invent a series letter.
5. confidence is 0.0 to 1.0 and is your own. Be honest downward. A guess with \
confidence 0.9 is worse than an UNKNOWN.\
"""

USER_TEMPLATE = """\
Candidate companies:
{candidates}

Holding:
  issuer name:  {issuer_name}
  issuer title: {issuer_title}
  filed by:     {filer}

Which company is this a position in?\
"""


@dataclass(frozen=True)
class Adjudication:
    company: str | None  # None means NOT_IN_UNIVERSE
    share_class: str
    confidence: float
    reason: str
    raw: str = ""
    seconds: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    error: str = ""

    @property
    def ok(self) -> bool:
        return not self.error


def candidate_block() -> str:
    """The closed list, with each company's own names. Eleven lines."""
    return "\n".join(
        f"  {company}  (also written: {', '.join(spellings)})"
        for company, spellings in ALIASES.items()
    )


def build_prompt(issuer_name: str, issuer_title=None, filer=None) -> tuple:
    """(system, user). Nothing here may derive from the golden-set label."""
    return SYSTEM_PROMPT, USER_TEMPLATE.format(
        candidates=candidate_block(),
        issuer_name=issuer_name or "(blank)",
        issuer_title=issuer_title or "(blank)",
        filer=filer or "(not recorded)",
    )


def _coerce(value, low=0.0, high=1.0) -> float:
    try:
        return max(low, min(high, float(value)))
    except (TypeError, ValueError):
        return 0.0


def adjudicate(backend, issuer_name, issuer_title=None, filer=None) -> Adjudication:
    """Ask the model about one holding. Never raises; failures come back typed.

    A backend error or an unparseable reply is recorded as an error and treated
    downstream as "no answer", not as NOT_IN_UNIVERSE. The difference matters:
    one is the model declining, the other is the plumbing breaking, and a run
    that conflates them reports a precision it did not earn.
    """
    system, user = build_prompt(issuer_name, issuer_title, filer)
    try:
        reply = backend.chat(system, user)
    except Exception as exc:
        return Adjudication(None, UNKNOWN, 0.0, "", error=f"backend: {exc}")

    try:
        parsed = parse_json_object(reply.text)
    except ValueError as exc:
        return Adjudication(
            None, UNKNOWN, 0.0, "", raw=reply.text, seconds=reply.seconds,
            prompt_tokens=reply.prompt_tokens, completion_tokens=reply.completion_tokens,
            error=f"unparseable: {exc}",
        )

    company = str(parsed.get("company", "")).strip()
    if company in (NOT_IN_UNIVERSE, ""):
        resolved = None
    elif company == UNKNOWN:
        resolved = UNKNOWN
    elif company in CANONICAL:
        resolved = company
    else:
        # A name outside the closed list is a schema violation, not an answer.
        return Adjudication(
            None, UNKNOWN, 0.0, str(parsed.get("reason", ""))[:300], raw=reply.text,
            seconds=reply.seconds, prompt_tokens=reply.prompt_tokens,
            completion_tokens=reply.completion_tokens,
            error=f"off-list company {company!r}",
        )

    return Adjudication(
        company=resolved,
        share_class=str(parsed.get("share_class", UNKNOWN)).strip() or UNKNOWN,
        confidence=_coerce(parsed.get("confidence")),
        reason=str(parsed.get("reason", "")).strip()[:300],
        raw=reply.text,
        seconds=reply.seconds,
        prompt_tokens=reply.prompt_tokens,
        completion_tokens=reply.completion_tokens,
    )


@dataclass(frozen=True)
class MatchV2:
    company: str | None
    score: float
    method: str  # lei | alias | spv | fuzzy | llm | none
    share_class: str
    consulted_llm: bool
    deterministic_company: str | None
    deterministic_score: float
    note: str = ""


def resolve_v2(issuer_name, issuer_title=None, issuer_lei=None, filer=None,
               backend=None, policy: str = POLICY_BAND,
               adjudication: Adjudication | None = None) -> MatchV2:
    """Deterministic first, then the model where the policy allows it.

    `adjudication` lets a caller pass a cached result instead of a backend, so
    the metrics can be recomputed from stored model output without re-running
    the model. Every number in docs/entity_resolution.md section 9 is produced
    that way -- see docs/_adjudication_results.json.
    """
    base = resolve(issuer_name, issuer_title, issuer_lei)
    base_class = base.share_class.label()

    def ask() -> Adjudication | None:
        if adjudication is not None:
            return adjudication
        if backend is None:
            return None
        return adjudicate(backend, issuer_name, issuer_title, filer)

    if policy == POLICY_LLM_ONLY:
        verdict = ask()
        if verdict is None or not verdict.ok:
            return MatchV2(None, 0.0, "none", base_class, True, base.company,
                           base.score, note=(verdict.error if verdict else "no backend"))
        company = None if verdict.company in (None, UNKNOWN) else verdict.company
        return MatchV2(company, verdict.confidence, "llm",
                       verdict.share_class or base_class, True, base.company,
                       base.score, note=verdict.reason)

    # An exact identity match is never put to a vote.
    if base.method in ("lei", "alias"):
        return MatchV2(base.company, base.score, base.method, base_class, False,
                       base.company, base.score, note=base.note)

    if policy == POLICY_VETO:
        # The model is only a skeptic here. Nothing to be skeptical about if the
        # matcher resolved nothing, so do not even spend the call.
        if base.company is None or base.score >= AUTO_ACCEPT:
            return MatchV2(base.company, base.score, base.method, base_class, False,
                           base.company, base.score, note=base.note)
        verdict = ask()
        if verdict is None or not verdict.ok:
            return MatchV2(base.company, base.score, base.method, base_class, False,
                           base.company, base.score,
                           note=(verdict.error if verdict else "no backend; kept deterministic"))
        # A veto is the only thing that can change the answer. Agreement, a
        # different company, an UNKNOWN -- anything that is not "no" leaves the
        # deterministic answer standing, because promotion is the move the
        # model was measured to be bad at.
        if verdict.company is None:
            return MatchV2(None, verdict.confidence, "llm_veto", base_class, True,
                           base.company, base.score,
                           note=f"model withdrew the claim: {verdict.reason}")
        return MatchV2(base.company, base.score, base.method, base_class, True,
                       base.company, base.score,
                       note=f"model did not object ({verdict.company})")

    if policy == POLICY_BAND and base.score >= AUTO_ACCEPT:
        return MatchV2(base.company, base.score, base.method, base_class, False,
                       base.company, base.score, note=base.note)

    verdict = ask()
    if verdict is None or not verdict.ok:
        # No model, or the model failed. Fall back to the floor rather than
        # dropping the row -- the deterministic answer is still the answer.
        return MatchV2(base.company, base.score, base.method, base_class, False,
                       base.company, base.score,
                       note=(verdict.error if verdict else "no backend; kept deterministic"))

    if verdict.company == UNKNOWN:
        return MatchV2(None, verdict.confidence, "llm", verdict.share_class or base_class,
                       True, base.company, base.score,
                       note=f"model says the filing does not disclose: {verdict.reason}")

    return MatchV2(verdict.company, verdict.confidence, "llm",
                   verdict.share_class or base_class, True, base.company, base.score,
                   note=verdict.reason)


def would_consult(issuer_name, issuer_title=None, issuer_lei=None,
                  policy: str = POLICY_BAND) -> bool:
    """Would this holding reach the model at all? Sizes the bill before it runs."""
    if policy == POLICY_LLM_ONLY:
        return True
    base = resolve(issuer_name, issuer_title, issuer_lei)
    if base.method in ("lei", "alias"):
        return False
    if policy == POLICY_VETO:
        return base.company is not None and base.score < AUTO_ACCEPT
    return not (policy == POLICY_BAND and base.score >= AUTO_ACCEPT)


def schema_json() -> str:
    return json.dumps(RESPONSE_SCHEMA, indent=1)
