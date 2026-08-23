"""Name normalisation and share-class grammar for N-PORT issuer strings.

Filers write the same company several dozen ways. Databricks alone appears under
51 distinct ISSUER_NAME spellings and 69 distinct ISSUER_TITLE spellings across
fourteen quarters. This module turns those strings into two things a matcher can
compare, and one thing the marks panel needs:

  normalise_name()  ->  NameKey(core, dense, tokens)
  parse_class()     ->  ShareClass(kind, series, subclass, basis)

Three design decisions, each forced by an observed row rather than assumed:

  1. Dots inside an alphabetic run are deleted, not spaced. 'X.AI' and 'xAI'
     are the same company; the frozen LIKE pattern '%X.AI%' misses Fidelity's
     'XAI CORP' spelling, which is 82 holdings -- the single largest recall gap
     in the pattern set. Deleting the dot closes it.

  2. A `dense` key with all separators removed is kept alongside `core`.
     'OPEN AI' vs 'OPENAI' and 'X.AI' vs 'XAI' are separator disagreements, not
     spelling differences, and a token-based scorer cannot see that.

  3. Series designators are never folded. 'WORLD LABS SER C PRIME PC PP' and
     'WORLD LABS SER C PC PP' are two different securities held by the same ten
     funds at different prices; anything that collapses 'C PRIME' to 'C' merges
     two real price series into one. The suffix is preserved verbatim.

Nothing here reads the network or the database. It is pure string work, so it
is cheap to test and cheap to run over 3.2 million distinct names.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

# --------------------------------------------------------------------------
# Noise that carries no identity
#
# Every literal below was taken from a real ISSUER_NAME or ISSUER_TITLE in the
# 22M-row private layer. 'PP' is private placement, 'DRS' is direct
# registration, and The Private Shares Fund terminates every title with three
# spaces and a slash. None of it distinguishes one issuer from another.
# --------------------------------------------------------------------------

_PARENTHETICAL_NOISE = (
    "(PHYSICAL)",
    "(NOT LISTED OR TRADING)",
    "(DRS)",
    "(NOT LISTED)",
)

# Corporate form and generic descriptors. Stripped only as whole tokens, never
# as substrings -- 'INC' must not eat the 'INC' in 'PRINCIPAL'. Note what is
# NOT here: no word that is part of a distinctive name. 'EXPLORATION' stays,
# because 'SPACE EXPLORATION' is the identity.
_SUFFIX_TOKENS = frozenset(
    """
    INC INCORPORATED CORP CORPORATION CO COMPANY LLC LLP LP LTD LIMITED PLC
    PBC PCB SA NV BV AG GMBH TRUST FUND HOLDINGS HOLDING GROUP PARTNERS
    TECHNOLOGIES TECHNOLOGY TECH SYSTEMS INDUSTRIES GLOBAL
    """.split()
)

# Deliberately absent from the list above: LABS. It reads like a generic
# descriptor and is not one -- 'World Labs' is the whole of that company's
# identity, and stripping it leaves the bare word 'WORLD', which fuzzy-matches
# a dozen unrelated issuers.

# 'PCB' is in the list above on purpose and it is not a typo of ours: two
# filers write 'OPENAI GROUP PCB', transposing PBC. Treating it as a corporate
# form makes the transposition disappear instead of having to be spelled out.

_CLASS_NOISE_TOKENS = frozenset(
    """
    PP PRIVATE PLACEMENT COMMON COM SHARES SHARE STOCK STK STCK STOCKS EQUITY
    EQ PREFERRED PREF PFD PRD CVT CVY CONVERTIBLE CONV SERIES SERIE SERES SER
    CLASS CL PC RT RTS RIGHTS RIGHT UNITS UNIT INTEREST INT PARTICIPATION
    PROFIT PHYSICAL LISTED TRADING NOT OR DRS USD PRIME
    """.split()
)

# PRIME belongs here rather than in the suffix list because it is class
# information: 'WORLD LABS SER C PRIME' is the C-Prime round of World Labs, so
# PRIME must leave the name key and survive in the class designator.


@dataclass(frozen=True)
class NameKey:
    """Three views of one issuer string, all uppercase."""

    core: str  # suffixes and class noise removed, single-spaced
    dense: str  # core with every separator removed
    tokens: tuple  # core split on space

    def __bool__(self) -> bool:
        return bool(self.core)


def _strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def _deparenthesise_noise(text: str) -> str:
    for literal in _PARENTHETICAL_NOISE:
        text = text.replace(literal, " ")
    return text


def clean(raw):
    """Uppercase, de-accent, drop trailing filer punctuation. No token removal.

    This is the shallowest layer: it is what gets stored so a human reading an
    audit can still recognise the string they saw in the filing.
    """
    if not raw:
        return ""
    text = _strip_accents(str(raw)).upper()
    text = _deparenthesise_noise(text)
    # 'DATABRICKS, INC. SERES G   /' -- The Private Shares Fund's terminator.
    text = re.sub(r"[\s/]+$", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _dedot(text: str) -> str:
    """'X.AI' -> 'XAI', but 'INC. SERIES' -> 'INC SERIES'.

    A dot between two letters is an abbreviation inside one token. A dot
    followed by a space or end-of-string is sentence punctuation. The first
    must vanish; the second must become a boundary.
    """
    text = re.sub(r"(?<=[A-Z])\.(?=[A-Z])", "", text)
    return text.replace(".", " ")


# A dot-TLD is punctuation with a domain name attached, not identity. It has to
# be removed *before* _dedot, because de-dotting fuses it into the stem:
# 'OPENAIR.COM' becomes the single token 'OPENAIRCOM', which then scores 75
# against the alias OPENAI and is rejected. That cost five real OpenAI holdings
# -- BlackRock's and New York Life's 'OpenAir.com, Series C' at 687.6869 -- and
# the golden set is what caught it.
#
# '.AI' is deliberately absent from this list and must stay absent: 'X.AI' is a
# company's whole identity, and stripping it would break the 85-holding recall
# fix that motivated _dedot in the first place. The four listed here are safe
# because no universe company is named after one -- the corpus's other dot-TLD
# issuers are Amazon.com, Businessolver.com, Mercor.io and their kind.
_DOT_TLD_RE = re.compile(r"\.(?:COM|NET|ORG|IO)\b")


def _drop_dot_tld(text: str) -> str:
    return _DOT_TLD_RE.sub("", text)


def _drop_lot_suffix(text: str) -> str:
    """'ANDURIL INDUSTRIES, INC. - 2' -> 'ANDURIL INDUSTRIES, INC.'

    BlackRock appends ' - <n>' to distinguish tax lots of the same security.
    The lot number is position bookkeeping, not identity, and leaving it in
    makes every lot look like a different issuer.
    """
    return re.sub(r"\s*[-–]\s*\d+\s*$", "", text)


def normalise_name(raw):
    """Reduce an issuer name or title to comparable keys."""
    text = clean(raw)
    if not text:
        return NameKey("", "", ())

    text = _drop_lot_suffix(text)
    text = _drop_dot_tld(text)
    text = _dedot(text)
    # Everything that is not a letter, digit or space becomes a boundary. Done
    # after _dedot so 'X.AI' has already been joined.
    text = re.sub(r"[^A-Z0-9 ]+", " ", text)

    kept = []
    for token in text.split():
        if token in _SUFFIX_TOKENS or token in _CLASS_NOISE_TOKENS:
            continue
        # A bare series or class letter ('G', or 'F-1' after the split into
        # 'F' '1') is class information, not identity.
        if len(token) <= 1:
            continue
        if re.fullmatch(r"[A-Z]\d{1,2}|\d{1,3}", token):
            continue
        kept.append(token)

    core = " ".join(kept)
    dense = core.replace(" ", "")
    return NameKey(core=core, dense=dense, tokens=tuple(kept))


# --------------------------------------------------------------------------
# Share-class grammar
#
# The kinds are deliberately coarse. 'Is this a share at all' is the question
# the marks panel needs answered, and getting it wrong is worse than leaving it
# UNKNOWN: a convertible interest right whose balance is a dollar amount
# produces a price of exactly 1.00, which looks like a price and is not one.
# --------------------------------------------------------------------------

COMMON = "COM"
PREFERRED = "PFD"
RIGHTS = "RIGHTS"  # convertible interest rights -- balance is dollars
UNITS = "UNITS"  # profit-participation / EV units -- balance is units
UNKNOWN = "UNKNOWN"
MIXED = "MIXED"  # one line spanning several classes

BASIS_PER_SHARE = "per_share"
BASIS_NOT_A_SHARE_PRICE = "not_a_share_price"
BASIS_BLENDED = "blended_classes"


@dataclass(frozen=True)
class ShareClass:
    kind: str
    series: str = ""  # 'F-1', 'C PRIME', 'H', or '' when absent
    subclass: str = ""  # the class letter, when distinct from the series
    basis: str = BASIS_PER_SHARE

    def label(self) -> str:
        """A single comparable string, e.g. 'PFD:F-1', 'COM:CLASS A', 'RIGHTS'."""
        tail = " ".join(
            p for p in (self.series, f"CLASS {self.subclass}" if self.subclass else "") if p
        )
        return f"{self.kind}:{tail}" if tail else self.kind


# 'RT'/'RTS' and the 1:1 ratio form both mean a right, not a share.
_RIGHTS_RE = re.compile(r"\b(CVT INT RIGHTS|CONVERTIBLE INTEREST RT|RTS?|RIGHTS)\b")
_UNITS_RE = re.compile(r"\b(EV UNITS|(?:PROFIT )?PARTICIPATION UNITS?)\b")

# 'PC' is Fidelity's preferred-convertible marker. Verified against ASSET_CAT
# on all 14 quarters: of 1,987 universe holdings whose title contains ' PC ',
# all 1,987 are tagged EP and none is tagged EC or OTHER. It is the most
# reliable preferred signal in the corpus, and the only one that is a bare
# two-letter token, so it is matched with word boundaries.
_PREFERRED_RE = re.compile(r"\b(PFD|PREF|PREFERRED|PRD|PC)\b")
_COMMON_RE = re.compile(r"\b(COMMON|COM STOCK|COM SHARES|COM UNITS)\b")

# 'SER E P' -- SpaceX's truncated preferred marker, seen at prices in the
# 810-5265 band while the same filer's common sits at 70-527. A trailing bare
# 'P' after a series letter means preferred.
_TRUNCATED_PFD_RE = re.compile(r"\bSER(?:IES)?\s+[A-Z](?:-?\d+)?\s+P\b")

# 'SERIES C PRIME', 'SER F-1', 'SERES G' (typo), 'SERIES A-3'. PRIME is part of
# the designator and must survive.
_SERIES_RE = re.compile(
    r"\b(?:SER|SERIES|SERIE|SERES)\s+([A-Z](?:\s*-\s*\d{1,2}|\d{1,2})?(?:\s+PRIME)?)\b"
)
_CLASS_RE = re.compile(r"\b(?:CL|CLASS)\s+([A-Z](?:\s*-\s*\d{1,2})?)\b")

# 'economic exposure to ... 55% Class A Common Stock and 45% Class C Common
# Stock' -- one holding line spanning two classes. Its price per share is a
# weighted blend of two different securities and belongs to neither.
_BLEND_RE = re.compile(r"\d{1,3}\s*%")


def _tidy_designator(text: str) -> str:
    """'F - 1' -> 'F-1', 'F1' -> 'F-1', 'C  PRIME' -> 'C PRIME'."""
    text = re.sub(r"\s*-\s*", "-", text.strip())
    text = re.sub(r"(?<=[A-Z])(?=\d)", "-", text)
    return re.sub(r"\s+", " ", text)


def parse_class(title, name=None):
    """Read the share class out of a title, falling back to the issuer name.

    Filers split the same information across the two fields inconsistently --
    'DATABRICKS SER H CVT' arrives as the *name* for some filers and as the
    *title* for others -- so both are searched, title first.
    """
    haystack = " ".join(p for p in (clean(title), clean(name)) if p)
    if not haystack:
        return ShareClass(UNKNOWN)

    if _UNITS_RE.search(haystack):
        return ShareClass(UNITS, basis=BASIS_NOT_A_SHARE_PRICE)
    if _RIGHTS_RE.search(haystack):
        return ShareClass(RIGHTS, basis=BASIS_NOT_A_SHARE_PRICE)

    series_match = _SERIES_RE.search(haystack)
    class_match = _CLASS_RE.search(haystack)
    series = _tidy_designator(series_match.group(1)) if series_match else ""
    subclass = _tidy_designator(class_match.group(1)) if class_match else ""

    if _BLEND_RE.search(haystack):
        # A blended line may name several classes; keep whichever was found for
        # the audit trail, but mark the price as not attributable to either.
        return ShareClass(MIXED, series=series, subclass=subclass, basis=BASIS_BLENDED)

    if _PREFERRED_RE.search(haystack) or _TRUNCATED_PFD_RE.search(haystack):
        kind = PREFERRED
    elif _COMMON_RE.search(haystack):
        kind = COMMON
    elif series:
        # A bare series letter on a private company designates a preferred
        # round; private companies do not issue 'Series G common'. Measured
        # agreement with ASSET_CAT is reported in docs/entity_resolution.md --
        # this is the rule most worth checking, not the most obvious one.
        kind = PREFERRED
    elif subclass:
        kind = COMMON
    else:
        kind = UNKNOWN

    if kind == PREFERRED and not series and subclass:
        # 'ANTHROPIC PBC CL F-1 PFD PP' and 'ANTHROPIC PBC SER F-1 CVT PFD PP'
        # are the same security: one filer calls the F-1 round a class, another
        # calls it a series. For a preferred, the round designator is the
        # series wherever the filer put it -- otherwise the same Anthropic
        # position lands in two different buckets in the marks panel.
        series, subclass = subclass, ""

    return ShareClass(kind, series=series, subclass=subclass)
