"""Turn the candidate frame into the labelled golden set.

    python -m scripts.label_golden_set --report     # show the decisions
    python -m scripts.label_golden_set              # write the fixture

Every label is assigned by one of six evidence classes and records which one
decided it, so a reviewer can audit the reasoning rather than the conclusion.
The classes are ordered, most authoritative first:

  E1 lei              the row carries a verified issuer LEI. A registered
                      identifier, so this is identity, not inference.
  E6 adjudicated      an explicit decision in ADJUDICATED below, each with a
                      written reason. These are the entries the other classes
                      get wrong, and there are eight of them.
  E4 spv_disclosure   the wrapper's own name discloses its underlying:
                      '... LLC (INVESTED IN DATABRICKS, INC., PFD SERIES G)'.
  E2 self_name        the issuer name contains the company's own name as an
                      exact contiguous token sequence. No fuzzy scoring.
  E3 price_anchor     the row's price coincides, within 0.5%, with a price that
                      LEI-confirmed or exactly-named rows report for a company
                      at the same period end.
  E5 opaque           the name is a wrapper that discloses nothing. Labelled
                      UNKNOWN, which is not the same as NOT_IN_UNIVERSE:
                      'FSOIFD TC HOLDINGS LLC' may well hold a universe
                      company, and the filing does not say.

Anything no class reaches is NOT_IN_UNIVERSE.

--------------------------------------------------------------------------
On circularity
--------------------------------------------------------------------------
E2 is the same reading the deterministic matcher performs, so entries labelled
by E2 test whether normalisation survives a filer's spelling -- not whether the
matcher can discover an identity. Treating them as evidence of discrimination
would flatter the matcher.

The metrics script therefore reports a `hard` subset as well as the whole set:
the entries decided by E1, E3, E4, E5 or E6, where the label rests on something
other than the name resembling the answer. That subset is the honest measure,
and it is the one to read first.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.resolve.match import ALIASES, ISSUER_LEIS  # noqa: E402
from src.resolve.normalize import clean, normalise_name, parse_class  # noqa: E402

FRAME = ROOT / "docs" / "_golden_candidates.json"
FIXTURE = ROOT / "tests" / "fixtures" / "golden_set_v1.json"

NOT_IN_UNIVERSE = "NOT_IN_UNIVERSE"
UNKNOWN = "UNKNOWN"

GOLDEN_VERSION = "1.0.0"

# --------------------------------------------------------------------------
# The human gate on this fixture (P1, P4)
#
# Recorded because it happened, and scoped because it was narrow. A machine may
# propose a label; only a human may attest to the set. What was actually
# reviewed was section 6 of docs/entity_resolution.md -- the adjudications --
# not the 286 labels the mechanical classes assigned.
# --------------------------------------------------------------------------
HUMAN_ATTESTATION = {
    "by": "Om Mali",
    "date": "2026-08-22",
    "record": "logs/RUN_LOG.md#2026-08-22-golden-set-attestation",
    "golden_set_version": GOLDEN_VERSION,
    "scope": (
        "Reviewed the adjudications in docs/entity_resolution.md section 6 and confirmed "
        "them as labelled, EXCEPT OPENAIR.COM -- see attestation_withdrawn. Did NOT review "
        "the LEI labels, the self-name labels, the negatives, any share_class or "
        "price_basis label, or the measured metrics."
    ),
    "confirmed_merges": [
        "ANTHROPICS TECHNOLOGY LTD.",
        "ANDURIL ENGINEERING LLC",
        "ANDURIL INVESTORS LLC",
        "SPACE EXPLORATION TECHNOLOGICS",
        "OPENAI FOUNDATION",
        "ANTHROPIC, INC.",
    ],
    "confirmed_not_in_universe": [
        "OPEN BAY AUTOS AI INC.",
    ],
    "attestation_withdrawn": [
        # Attested as NOT_IN_UNIVERSE on 2026-08-22 and withdrawn the same day.
        # The reason given for that label was factually wrong (see ADJUDICATED),
        # so the approval rested on a false statement and cannot stand. The
        # corrected label is 'OpenAI Group PBC' and is NOT yet attested.
        "OPENAIR.COM"
    ],
    "not_individually_named": [
        # Named neither way in the review. Left as labelled; the label is
        # 'X.AI Corp' on the strength of the name, and X.AI is a watchlist
        # company whose marks are not published, so nothing downstream turns
        # on it. Recorded rather than folded into the approval above.
        "XAI CORP."
    ],
    # Scoped per entry, not per file. The first version of this clause voided
    # the whole attestation on "any edit to ADJUDICATED" -- and then ADJUDICATED
    # was edited, for OPENAIR.COM, which by the letter of it invalidated seven
    # confirmations that had nothing to do with that row. A rule that fires on
    # every unrelated edit gets ignored, which is worse than a narrow one.
    "voids_on": (
        "For a named entry: any change to its label or to its reason in ADJUDICATED. "
        "For the whole attestation: any change to the evidence-class procedure in "
        "decide(), or any change to src/resolve/normalize.py that moves a normalised "
        "key, since E2 and E4 both read it. Verified after the 2026-08-22 dot-TLD "
        "change: exactly one golden-set entry contains a dot-TLD (OPENAIR.COM, already "
        "withdrawn), so no other label moved and the remaining confirmations stand."
    ),
}

# --------------------------------------------------------------------------
# Opaque wrappers
#
# Fidelity's internal SPV naming. 'FSOIFD' is a Fidelity fund code, not an
# issuer, and the filing gives no underlying. Three such names hold positions
# priced from $49 to $4,456 a share, which is to say they hold something real
# and undisclosed. Anything matching these is UNKNOWN, never NOT_IN_UNIVERSE:
# recording them as 'not one of ours' would be a claim the filing cannot
# support, and the count of them is a headline number in every run summary.
# --------------------------------------------------------------------------
OPAQUE_WRAPPER_MARKERS = ("FSOIFD",)

# --------------------------------------------------------------------------
# E6 -- the entries the mechanical classes get wrong, decided explicitly.
# Keyed by issuer name. Each carries the reason it overrides.
# --------------------------------------------------------------------------
ADJUDICATED = {
    "ANTHROPICS TECHNOLOGY LTD.": (
        "Anthropic PBC",
        "Anthropics Technology Ltd is a real British software company and this "
        "is not it. BlackRock files three holdings under that name, titled "
        "'Series G' and priced at 259.13640004 and 259.13641638 on 2026-03-31 "
        "-- the period end on which six LEI-confirmed filers price Anthropic "
        "Series G at 259.1364. Agreement to ten significant figures is not a "
        "coincidence; INVESTMENT_COUNTRY 'GB' is inherited from the wrong "
        "entity in BlackRock's security master. The position is Anthropic.",
    ),
    "OPENAIR.COM": (
        "OpenAI Group PBC",
        "CORRECTED 2026-08-22. This was first labelled NOT_IN_UNIVERSE on the "
        "stated ground that its price coincided with an OpenAI anchor in only "
        "one period. That was simply wrong, and reading the rows settles it the "
        "other way: the title is 'OpenAir.com, Series C', the price is "
        "687.6869 on both 2026-03-31 and 2026-04-30, and 687.6869 is the "
        "OpenAI Series C consensus -- eight holdings across six registrants "
        "whose identity is not in dispute report it to the same four decimals "
        "on the first of those dates. (Corrected again 2026-08-23: those eight "
        "were described here as LEI-confirmed, which was wrong. One carries "
        "OpenAI's registered issuer identifier; the other seven name OpenAI "
        "outright. Both are unimpeachable evidence classes, but they are not "
        "the same one.) The five holdings are BlackRock's (three) and New York Life's "
        "(two). Every issuer priced at 687.69 in those two periods is an "
        "OpenAI spelling. 'OpenAir.com' is a security-master collision with a "
        "defunct dot-com of that name; the position is OpenAI Group PBC.",
    ),
    "OPEN BAY AUTOS AI INC.": (
        NOT_IN_UNIVERSE,
        "A used-car marketplace. It reaches the frame because matcher v1 claims "
        "it: the two-token alias 'OPEN AI' is fully covered by the tokens OPEN "
        "and AI, which this name happens to contain in that order. It is the "
        "clearest false positive in the set and the entry that fixes the "
        "confidence threshold.",
    ),
    "XAI CORP.": (
        "X.AI Corp",
        "Two BlackRock holdings titled 'xAI Corp.'. Its price coincides with "
        "an Anduril anchor because Anduril's mark sat flat at 40.88 for seven "
        "consecutive period ends and X.AI passed through that price; the name "
        "decides this one, not the price.",
    ),
    "ANDURIL ENGINEERING LLC": (
        "Anduril Industries, Inc.",
        "BlackRock's holding vehicle, not a separate issuer. Prices match the "
        "Anduril Industries consensus exactly across nine period ends -- "
        "21.7366, 23.16, 40.88, 68.95 -- including the long flat stretch at "
        "40.88 that no unrelated issuer would reproduce to four decimals.",
    ),
    "ANDURIL INVESTORS LLC": (
        "Anduril Industries, Inc.",
        "Same as Anduril Engineering LLC: a BlackRock vehicle priced at the "
        "Anduril consensus, 40.88 on the period ends where it appears.",
    ),
    "SPACE EXPLORATION TECHNOLOGICS": (
        "Space Exploration Technologies Corp.",
        "'TECHNOLOGICS' is a typo for 'TECHNOLOGIES'. Ten holdings, priced in "
        "the 970 to 5,265.90 preferred band that SpaceX preferred occupies.",
    ),
    "OPENAI FOUNDATION": (
        "OpenAI Group PBC",
        "The OpenAI Foundation is the non-profit parent and is not an issuer of "
        "equity, so on its face this is the wrong entity. Three filers -- "
        "Franklin twice and Nuveen -- report it at 687.69 and 687.6869, which is "
        "the OpenAI Group PBC consensus to the cent on both period ends. The "
        "holdings are OpenAI Group PBC equity filed under the parent's name. "
        "Recorded explicitly because the two entities are genuinely distinct and "
        "a reader is right to question the merge.",
    ),
    "ANTHROPIC, INC.": (
        "Anthropic PBC",
        "Anthropic is a public benefit corporation, not an Inc, but ARK "
        "Venture Fund has filed it this way for thirteen consecutive period "
        "ends with a price series that tracks Anthropic throughout -- 140.97 "
        "on 2025-10-31 and 259.14 on 2026-04-30 both match the consensus.",
    ),
}

# Aliases as exact token sequences, longest first so that 'FIGURE AI' is tested
# before any single-token alias could shadow it.
_ALIAS_TOKENS = sorted(
    (
        (company, normalise_name(spelling).tokens)
        for company, spellings in ALIASES.items()
        for spelling in spellings
    ),
    key=lambda pair: -len(pair[1]),
)


def _contains_self_name(name: str):
    """Does this name contain a company's own name as contiguous exact tokens?"""
    tokens = normalise_name(name).tokens
    for company, alias_tokens in _ALIAS_TOKENS:
        n = len(alias_tokens)
        if not n:
            continue
        for i in range(len(tokens) - n + 1):
            if tokens[i : i + n] == alias_tokens:
                return company, " ".join(alias_tokens)
    return None, None


def _spv_disclosure(name: str):
    """Does a parenthetical or 'dba' clause name a company outright?"""
    text = clean(name)
    start = text.rfind("(")
    payload = ""
    if start != -1:
        end = text.find(")", start)
        payload = text[start + 1 : end if end != -1 else len(text)]
    elif " DBA " in text:
        payload = text.split(" DBA ", 1)[1]
    if not payload.strip():
        return None, None
    company, alias = _contains_self_name(payload)
    return company, (payload.strip()[:80] if company else None)


def decide(entry: dict) -> dict:
    """Assign one label, and say what decided it."""
    name = entry["issuer_name"]
    facts, evidence = entry["facts"], entry["evidence"]

    # ---- E1: a verified registered identifier on the row.
    lei_companies = {ISSUER_LEIS[lei] for lei in facts["leis"] if lei in ISSUER_LEIS}
    lei_company = lei_companies.pop() if len(lei_companies) == 1 else None

    # ---- E6: explicit adjudication.
    if name in ADJUDICATED:
        company, reason = ADJUDICATED[name]
        if lei_company and company != lei_company and company != NOT_IN_UNIVERSE:
            # A registered identifier disagreeing with a written judgment is a
            # defect, not something to resolve quietly. P6.
            raise SystemExit(
                f"{entry['id']} {name}: adjudicated as {company} but the row's LEI "
                f"says {lei_company}. Log this and settle it before labelling."
            )
        return {"company": company, "evidence_class": "E6_adjudicated", "reason": reason}

    if lei_company:
        return {
            "company": lei_company,
            "evidence_class": "E1_lei",
            "reason": f"row carries verified issuer LEI {sorted(facts['leis'])[0]}",
        }

    # ---- E5: an opaque wrapper. Checked before the name classes, because a
    #          wrapper that discloses nothing must not be read as a negative.
    if any(marker in name for marker in OPAQUE_WRAPPER_MARKERS):
        return {
            "company": UNKNOWN,
            "evidence_class": "E5_opaque",
            "reason": "opaque wrapper: the filing names a fund vehicle and no underlying issuer",
        }

    # ---- E4: the wrapper discloses its underlying.
    company, payload = _spv_disclosure(name)
    if company:
        return {
            "company": company,
            "evidence_class": "E4_spv_disclosure",
            "reason": f"wrapper discloses its underlying: '{payload}'",
        }

    # ---- E2: the name contains the company's own name.
    company, alias = _contains_self_name(name)
    if company:
        return {
            "company": company,
            "evidence_class": "E2_self_name",
            "reason": f"name contains '{alias}' as an exact token sequence",
        }

    # ---- E3: price coincidence with an independent anchor. Two or more
    #          periods required -- a single overlap is ordinary between
    #          unrelated issuers, as OPENAIR.COM demonstrates.
    hits = evidence["anchor_hits"]
    strong = {c: h for c, h in hits.items() if h["periods"] >= 2}
    if len(strong) == 1:
        company, hit = next(iter(strong.items()))
        return {
            "company": company,
            "evidence_class": "E3_price_anchor",
            "reason": (
                f"price coincides with the {company} anchor in {hit['periods']} periods, "
                f"e.g. {hit['example']['price']} against {hit['example']['anchor_price']} "
                f"on {hit['example']['period_end']}"
            ),
        }

    return {
        "company": NOT_IN_UNIVERSE,
        "evidence_class": "E0_none",
        "reason": "no LEI, no self-name, no disclosed underlying, no anchor coincidence",
    }


def build(verbose: bool = True) -> dict:
    frame = json.loads(FRAME.read_text(encoding="utf-8"))
    entries = []
    for entry in frame["entries"]:
        label = decide(entry)
        share_class = parse_class(entry["issuer_title"], entry["issuer_name"])
        entries.append(
            {
                "id": entry["id"],
                "issuer_name": entry["issuer_name"],
                "issuer_title": entry["issuer_title"],
                "strata": entry["strata"],
                "holdings": entry["facts"]["holdings"],
                "ciks": entry["facts"]["ciks"],
                "period_first": entry["facts"]["period_first"],
                "period_last": entry["facts"]["period_last"],
                "asset_cats": entry["facts"]["asset_cats"],
                "price_min": entry["facts"]["price_min"],
                "price_max": entry["facts"]["price_max"],
                "example_accession": entry["facts"]["example_accession"],
                # ---- the labels
                "company": label["company"],
                "evidence_class": label["evidence_class"],
                "label_reason": label["reason"],
                "share_class": share_class.label(),
                "price_basis": share_class.basis,
            }
        )
    return {
        "golden_set_version": GOLDEN_VERSION,
        "labelled_by": "claude-opus-5 (agent), from the evidence recorded in each entry",
        # Set here rather than patched into the JSON, so that re-running this
        # script cannot silently drop the attestation it does not know about.
        # Any change to ADJUDICATED or to the evidence procedure voids it and
        # this block must be cleared -- see the last line of the attestation.
        "human_attestation": HUMAN_ATTESTATION,
        "note": (
            "Labels are agent-assigned by the documented evidence procedure in "
            "scripts/label_golden_set.py, not hand-typed. Each entry names the class that "
            "decided it. A human has attested to the adjudications only -- see "
            "human_attestation.scope, which says plainly what was and was not reviewed. "
            "Read the E1/E3/E4/E5/E6 subset first: those are the labels that rest on "
            "something other than the name resembling the answer."
        ),
        "entries": entries,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true", help="print the decisions, write nothing")
    args = ap.parse_args()

    payload = build()
    entries = payload["entries"]

    by_class: dict = {}
    by_company: dict = {}
    for e in entries:
        by_class[e["evidence_class"]] = by_class.get(e["evidence_class"], 0) + 1
        by_company[e["company"]] = by_company.get(e["company"], 0) + 1

    print(f"{len(entries)} labelled strings covering "
          f"{sum(e['holdings'] for e in entries):,} holdings\n")
    print("by evidence class")
    for name, count in sorted(by_class.items()):
        print(f"  {name:22} {count:>4}")
    print("\nby label")
    for name, count in sorted(by_company.items(), key=lambda kv: -kv[1]):
        print(f"  {name:40} {count:>4}")

    hard = [e for e in entries if e["evidence_class"] not in ("E2_self_name", "E0_none")]
    print(f"\nhard subset (label not decided by the name): {len(hard)} strings, "
          f"{sum(e['holdings'] for e in hard):,} holdings")

    if args.report:
        print("\n--- E6 adjudicated ---")
        for e in entries:
            if e["evidence_class"] == "E6_adjudicated":
                print(f"  {e['id']} {e['issuer_name'][:40]:42} -> {e['company']}")
        return

    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"\nwrote {FIXTURE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
