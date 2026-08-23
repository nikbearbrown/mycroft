"""Deterministic issuer matcher v1: LEI, alias, SPV unwrap, gated fuzzy.

Four resolution paths, tried in order, each strictly more speculative than the
last. The first one that fires wins and records how it fired, so every resolved
row can be traced to the rule that resolved it:

  lei          ISSUER_LEI is a known issuer LEI                    score 1.00
  alias        the normalised name equals a known alias            score 1.00
  spv          the wrapper's parenthetical resolves via the above  score <= 0.95
  fuzzy        the coverage gate passes, scored by name agreement  score < 1.00

Two things this module does NOT do, on purpose:

  It does not memorise filer spellings. The alias table holds only the names a
  company calls itself plus its corporate forms -- fourteen entries for eleven
  companies. Every one of the 166 distinct spellings in the corpus has to be
  reached by normalisation and fuzzy scoring, or it is a genuine miss. An alias
  table stuffed with observed spellings would score 100% on the golden set and
  tell us nothing about the next quarter.

  It does not adjudicate. Where the filing does not determine the answer -- an
  opaque Fidelity SPV named 'FSOIFD TC HOLDINGS LLC' -- it returns no match
  rather than a guess. Week 5's LLM layer is measured against this floor.

--------------------------------------------------------------------------
Why the fuzzy path needs a gate rather than a threshold
--------------------------------------------------------------------------
rapidfuzz's `token_set_ratio` scores a subset as a perfect match, because the
token intersection ends up compared with itself. Measured on real corpus names:

    token_set_ratio('FIGURE',              'FIGURE AI')  = 100   wrong company
    token_set_ratio('OPEN BAY AUTOS AI',   'OPEN AI')    = 100   wrong company
    token_set_ratio('ANDURIL ENGINEERING', 'ANDURIL')    = 100   right company

A true positive and two false positives, all three at the very top of the
range. No threshold on that scorer can separate them, so the scorer cannot be
the thing that decides.

The gate is therefore a necessary condition evaluated before any score:
*every* token of the alias must be matched by some token of the query at
TOKEN_SIM or better. It rejects 'FIGURE' outright, because nothing in it
accounts for AI; it admits 'ANDURIL ENGINEERING LLC', which is a true Anduril
position confirmed by its price.

It does not save us from 'OPEN BAY AUTOS AI INC.', and that is worth being
plain about: the two-token alias 'OPEN AI' is fully covered by the tokens OPEN
and AI, which that name genuinely contains. What separates it is the
unexplained-token penalty below, which puts it at 0.80 -- alongside three
correct blended SpaceX SPVs, also at 0.80. Nothing separates those four, which
is why the operating point in docs/entity_resolution.md is a review band and
not a threshold.

TOKEN_SIM is 92 rather than a rounder 90 for one measured reason: 'SPACE'
against the alias 'SPACEX' scores 90.9, and 'RELATIVITY SPACE INC' -- 73
holdings of a different rocket company -- is not SpaceX.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from rapidfuzz import fuzz

from src.ingest.universe import UNIVERSE_PATTERNS, WATCHLIST_PATTERNS
from src.resolve.normalize import (
    BASIS_PER_SHARE,
    ShareClass,
    clean,
    normalise_name,
    parse_class,
)

# --------------------------------------------------------------------------
# Aliases -- what a company calls itself, not what filers call it
# --------------------------------------------------------------------------

ALIASES = {
    "Anthropic PBC": ["Anthropic"],
    "OpenAI Group PBC": ["OpenAI", "Open AI"],
    "Databricks, Inc.": ["Databricks"],
    "Space Exploration Technologies Corp.": ["Space Exploration", "SpaceX"],
    "Anduril Industries, Inc.": ["Anduril"],
    "Cerebras Systems Inc.": ["Cerebras"],
    "Figure AI Inc.": ["Figure AI"],
    # Watchlist companies. Captured but not published -- see universe_v1.json.
    "X.AI Corp": ["X.AI", "xAI"],
    "Perplexity AI, Inc.": ["Perplexity"],
    "Groq, Inc.": ["Groq"],
    "Scale AI, Inc.": ["Scale AI"],
}

# Issuer LEIs observed in the corpus, each verified to map to exactly one
# company and to appear on no other issuer's rows. Checked on all 14 quarters:
# 2,951 of 5,806 universe holdings carry one of these, and none of the seven is
# shared. A LEI is a registered identifier, so this path is an identity match,
# not a name guess -- which is why it outranks everything else.
#
# Two companies have two LEIs each because they hold through two registered
# entities (OpenAI LLC and OpenAI Group PBC; Databricks' two filings).
ISSUER_LEIS = {
    "549300B9WLO96RQCXP87": "Space Exploration Technologies Corp.",
    "984500FEDAC7FBD96273": "Databricks, Inc.",
    "984500E549A1FDC76F73": "Databricks, Inc.",
    "254900CIXLZUXXNYQW57": "Anduril Industries, Inc.",
    "984500B6DEB8CEBC4Z70": "Anthropic PBC",
    "9845008AF81ABBC36E24": "OpenAI Group PBC",
    "549300M3WRI6CMX2WP65": "OpenAI Group PBC",
}

# Generic fund-structure vocabulary. A query token from this set is "explained"
# -- it describes the wrapper, not the issuer -- so it does not count against
# the confidence of a match. Sponsor names (TIGER, DXYZ, MWAM) are deliberately
# absent: they are not generic, and an SPV whose sponsor we cannot account for
# should score lower than a direct holding.
_WRAPPER_VOCAB = frozenset(
    """
    ECONOMIC EXPOSURE INVESTED INVESTMENT INVESTMENTS INVESTORS CAPITAL
    FUND FUNDS VENTURE VENTURES PARTNER PARTNERS OPPORTUNITY OPPORTUNITIES
    GROWTH STRATEGIC PORTFOLIO VEHICLE SPV DBA
    """.split()
)

TOKEN_SIM = 92  # gate: minimum per-token similarity, see module docstring
SPV_SCORE_CAP = 0.95  # an unwrapped SPV is never as certain as a direct name
UNEXPLAINED_PENALTY = 0.10  # per query token that is neither alias nor wrapper


@dataclass(frozen=True)
class Match:
    """What the matcher concluded, and how."""

    company: str | None
    score: float  # 0.0 - 1.0
    method: str  # lei | alias | spv | fuzzy | none
    share_class: ShareClass = field(default_factory=lambda: ShareClass("UNKNOWN"))
    wrapper: str = "direct"  # direct | spv_transparent | spv_opaque
    candidates_considered: int = 0
    note: str = ""

    @property
    def resolved(self) -> bool:
        return self.company is not None


# --------------------------------------------------------------------------
# Blocking
#
# Eleven companies makes brute force free, but the production input is 3.2
# million distinct names, so the candidate step is written as an index from the
# start and its reduction ratio is reported rather than assumed.
# --------------------------------------------------------------------------


def _trigrams(text: str) -> set:
    padded = f"  {text} "
    return {padded[i : i + 3] for i in range(len(padded) - 2)}


class _AliasIndex:
    """Trigram inverted index over alias keys."""

    def __init__(self, aliases: dict):
        self.entries = []  # (company, NameKey)
        self.postings = {}
        for company, spellings in aliases.items():
            for spelling in spellings:
                key = normalise_name(spelling)
                if not key:
                    continue
                slot = len(self.entries)
                self.entries.append((company, key))
                for gram in _trigrams(key.dense):
                    self.postings.setdefault(gram, set()).add(slot)

    def candidates(self, key) -> list:
        slots = set()
        for gram in _trigrams(key.dense):
            slots |= self.postings.get(gram, set())
        return [self.entries[s] for s in sorted(slots)]

    def __len__(self) -> int:
        return len(self.entries)


_INDEX = _AliasIndex(ALIASES)


def blocking_stats(key) -> tuple:
    """(candidates, total) for one query -- the reduction ratio, measurable."""
    return len(_INDEX.candidates(key)), len(_INDEX)


# --------------------------------------------------------------------------
# The fuzzy path
# --------------------------------------------------------------------------


def _gate_and_score(query, alias) -> float | None:
    """Coverage gate, then a confidence. None means the gate rejected it.

    The gate is the whole of the discrimination; the score only expresses how
    much of the query the alias accounts for, which is what a review band
    needs in order to be worth having.
    """
    if not query.tokens or not alias.tokens:
        return None

    matched_query_tokens = set()
    coverage = 100.0
    for alias_token in alias.tokens:
        best, best_token = 0.0, None
        for query_token in query.tokens:
            similarity = fuzz.ratio(alias_token, query_token)
            if similarity > best:
                best, best_token = similarity, query_token
        if best < TOKEN_SIM:
            return None  # an alias token is unaccounted for: not this company
        matched_query_tokens.add(best_token)
        coverage = min(coverage, best)

    unexplained = [
        t for t in query.tokens if t not in matched_query_tokens and t not in _WRAPPER_VOCAB
    ]
    score = coverage / 100.0 * (1.0 - UNEXPLAINED_PENALTY * len(unexplained))
    return max(score, 0.0)


# --------------------------------------------------------------------------
# SPV unwrapping
# --------------------------------------------------------------------------


def _spv_payload(raw: str) -> str | None:
    """The part of a wrapper name that names the underlying company.

    Three observed forms, all of them a filer voluntarily disclosing what the
    vehicle holds:
        'U First Capital Fund III LLC (SpaceX)'
        'TIGER GLOBAL PIP 12-1, LLC (INVESTED IN DATABRICKS, INC., PFD SERIES G)'
        'AESTAS LLC dba OPENAI LLC EV UNITS PP'
    An opaque wrapper -- 'FSOIFD TC HOLDINGS LLC' -- has no payload, and that
    absence is the point: nothing in the filing says what it holds.
    """
    text = clean(raw)
    if not text:
        return None
    start = text.rfind("(")
    if start != -1:
        end = text.find(")", start)
        inner = text[start + 1 : end if end != -1 else len(text)].strip()
        if inner:
            return inner
    marker = " DBA "
    if marker in text:
        return text.split(marker, 1)[1].strip()
    return None


# --------------------------------------------------------------------------
# The matcher
# --------------------------------------------------------------------------


def resolve(issuer_name, issuer_title=None, issuer_lei=None, _depth=0) -> Match:
    """Resolve one holding's issuer to a canonical company, or to nothing."""
    share_class = parse_class(issuer_title, issuer_name)
    key = normalise_name(issuer_name)
    candidates = _INDEX.candidates(key)

    # ---- 1. LEI. A registered identifier beats every name heuristic.
    lei = (issuer_lei or "").strip()
    if len(lei) == 20 and lei in ISSUER_LEIS:
        return Match(
            company=ISSUER_LEIS[lei],
            score=1.0,
            method="lei",
            share_class=share_class,
            candidates_considered=len(candidates),
            note=f"LEI {lei}",
        )

    # ---- 2. Exact alias, on either the spaced or the de-spaced key.
    for company, alias in candidates:
        if key.core == alias.core or key.dense == alias.dense:
            return Match(
                company=company,
                score=1.0,
                method="alias",
                share_class=share_class,
                candidates_considered=len(candidates),
                note=f"exact alias '{alias.core}'",
            )

    # ---- 3. An SPV that discloses its underlying. Resolve the payload, keep
    #         the wrapper's own class parse (the payload rarely restates it).
    if _depth == 0:
        payload = _spv_payload(issuer_name)
        if payload:
            inner = resolve(payload, issuer_title, None, _depth=1)
            if inner.resolved:
                return Match(
                    company=inner.company,
                    score=min(inner.score, SPV_SCORE_CAP),
                    method="spv",
                    share_class=share_class,
                    wrapper="spv_transparent",
                    candidates_considered=len(candidates),
                    note=f"underlying disclosed as '{payload[:60]}' via {inner.method}",
                )

    # ---- 4. Gated fuzzy.
    best_match, best_score, best_alias = None, 0.0, ""
    for company, alias in candidates:
        score = _gate_and_score(key, alias)
        if score is not None and score > best_score:
            best_match, best_score, best_alias = company, score, alias.core
    if best_match is not None:
        return Match(
            company=best_match,
            score=round(best_score, 4),
            method="fuzzy",
            share_class=share_class,
            candidates_considered=len(candidates),
            note=f"gate passed against '{best_alias}'",
        )

    # ---- 5. Nothing. If the name looks like a wrapper, say so: an opaque SPV
    #         is a different kind of unresolved than an unrelated issuer, and
    #         only the first one is worth a human's time.
    looks_like_wrapper = any(
        token in {"LLC", "LP", "HOLDINGS", "FUND"} for token in clean(issuer_name).split()
    )
    return Match(
        company=None,
        score=0.0,
        method="none",
        share_class=share_class,
        wrapper="spv_opaque" if looks_like_wrapper else "direct",
        candidates_considered=len(candidates),
        note="no alias accounted for by the name",
    )


# --------------------------------------------------------------------------
# Baseline A: the frozen LIKE patterns Week 2 shipped
#
# Reimplemented here in Python so both systems can be scored against the same
# labels without a database round trip. This is a mirror, not a variant: any
# disagreement with universe.company_case_expr() is a defect, and a test in
# tests/test_resolve.py pins the two together on every corpus name.
# --------------------------------------------------------------------------

_LIKE_ARMS = [
    (company, [p.strip("%") for p in patterns])
    for group in (UNIVERSE_PATTERNS, WATCHLIST_PATTERNS)
    for company, patterns in group.items()
]


def like_pattern_company(issuer_name) -> str | None:
    """What the frozen Week 2 pattern set would call this row. First arm wins."""
    upper = (issuer_name or "").upper()
    for company, literals in _LIKE_ARMS:
        if any(literal in upper for literal in literals):
            return company
    return None
