"""Week 4 regression tests: entity resolution, the golden set, and the baseline.

Three kinds of test here, and the third is the one that matters most:

  * unit tests on normalisation and the share-class grammar, each pinned to a
    real issuer string from the corpus;
  * integrity tests on the golden-set fixture, so a malformed label cannot
    silently become a metric;
  * a pinned baseline. The measured precision and recall are asserted, so any
    later change to the matcher has to move the numbers on purpose and say so
    in the RUN_LOG. A matcher that quietly gets worse is the failure mode this
    whole week exists to prevent.

Tests that need the Parquet layer skip rather than fail when it is absent --
a missing artifact is a setup problem, not a regression.
"""

import json
import sys
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.ingest.build_parquet import ALL_QUARTERS, PARQUET  # noqa: E402
from src.ingest.universe import company_case_expr  # noqa: E402
from src.resolve.match import (  # noqa: E402
    ALIASES,
    ISSUER_LEIS,
    TOKEN_SIM,
    blocking_stats,
    like_pattern_company,
    resolve,
)
from src.resolve.normalize import (  # noqa: E402
    BASIS_BLENDED,
    BASIS_NOT_A_SHARE_PRICE,
    BASIS_PER_SHARE,
    COMMON,
    PREFERRED,
    normalise_name,
    parse_class,
)

FIXTURE = ROOT / "tests" / "fixtures" / "golden_set_v1.json"


@pytest.fixture(scope="module")
def golden():
    if not FIXTURE.exists():
        pytest.skip("golden set not built -- run python -m scripts.label_golden_set")
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def con():
    files = [
        (PARQUET / q / "universe_holdings.parquet").as_posix()
        for q in ALL_QUARTERS
        if (PARQUET / q / "universe_holdings.parquet").exists()
    ]
    if not files:
        pytest.skip("no universe Parquet built -- run src.ingest.build_parquet --all")
    c = duckdb.connect()
    c.execute(f"CREATE VIEW u AS SELECT * FROM read_parquet([{', '.join(repr(f) for f in files)}])")
    return c


# --------------------------------------------------------------------------
# Normalisation
# --------------------------------------------------------------------------

def test_dot_inside_a_word_is_deleted_not_spaced():
    """'X.AI' and 'xAI' are one company. This is the fix that recovers the 85
    Fidelity holdings the frozen '%X.AI%' pattern misses."""
    assert normalise_name("X.AI Corp").dense == normalise_name("XAI CORP").dense == "XAI"


def test_dot_before_a_space_is_still_a_boundary():
    """Deleting every dot would fuse 'INC.' into the next token."""
    assert normalise_name("Databricks, Inc. Series G").core == "DATABRICKS"


def test_separator_disagreement_collapses_on_the_dense_key():
    """BlackRock writes 'Open AI', everyone else writes 'OpenAI'."""
    assert normalise_name("OPEN AI GLOBAL LLC").dense == normalise_name("OPENAI").dense


def test_tax_lot_suffix_is_not_identity():
    """BlackRock appends ' - 2' to distinguish lots of the same security."""
    assert normalise_name("Anduril Industries, Inc. - 2").core == "ANDURIL"


def test_labs_survives_normalisation():
    """LABS reads like a generic descriptor and is not one: it is the whole of
    World Labs' identity, and stripping it leaves the bare word 'WORLD'."""
    assert normalise_name("WORLD LABS SER C PC PP").core == "WORLD LABS"


def test_a_dot_tld_is_stripped_but_never_dot_ai():
    """A dot-TLD is punctuation with a domain attached. It has to go before
    _dedot, which would otherwise fuse it into the stem -- 'OPENAIR.COM' became
    the single token 'OPENAIRCOM', scored 75 against the alias OPENAI, and cost
    five real OpenAI holdings.

    '.AI' must survive, because 'X.AI' is a company's whole identity and
    stripping it would undo the 85-holding recall fix that motivated _dedot."""
    assert normalise_name("OpenAir.com").core == "OPENAIR"
    assert normalise_name("AMAZON.COM INC").core == "AMAZON"
    assert normalise_name("MERCOR.IO CORPORATION").core == "MERCOR"
    assert normalise_name("X.AI HOLDINGS CORP").core == "XAI"
    assert normalise_name("X.AI, CORP.").dense == normalise_name("XAI CORP").dense


@pytest.mark.parametrize(
    "name",
    [
        "AMAZON.COM INC",
        "BUSINESSOLVER.COM, INC.",
        "MERCOR.IO CORPORATION (SERIES C PREFERRED STOCK)",
        "WAY.COM, INC.",
        "CARD.IO, INC.",
        "TOKENS.COM CORP",
        "INTEGRATE.COM INC",
        "XPRESSMYSELF.COM LLC",
    ],
)
def test_the_dot_tld_strip_claims_nothing_new(name):
    """The fix that recovers OpenAir.com must not start claiming every dot-com
    in the corpus."""
    assert resolve(name).company is None


def test_the_private_shares_fund_row_terminator_is_stripped():
    assert normalise_name("DATABRICKS, INC. SERES G   /").core == "DATABRICKS"


def test_pcb_transposition_disappears():
    """Two filers write 'OPENAI GROUP PCB', transposing PBC."""
    assert normalise_name("OPENAI GROUP PCB CLASS A COMMON PP").core == "OPENAI"


# --------------------------------------------------------------------------
# Share-class grammar
# --------------------------------------------------------------------------

def test_series_c_and_series_c_prime_stay_distinct():
    """plan.md week 4's named case. The same ten funds hold both, at 315 and
    338 a share; anything that folds 'C PRIME' into 'C' merges two real price
    series into one and the spread disappears into a dispersion figure."""
    c = parse_class("WORLD LABS SER C PC PP")
    c_prime = parse_class("WORLD LABS SER C PRIME PC PP")
    assert c.label() == "PFD:C"
    assert c_prime.label() == "PFD:C PRIME"
    assert c.label() != c_prime.label()


def test_class_and_series_agree_for_a_preferred_round():
    """'CL F-1 PFD' and 'SER F-1 CVT PFD' are one security written two ways."""
    assert parse_class("ANTHROPIC PBC CL F-1 PFD PP (PHYSICAL)").label() == "PFD:F-1"
    assert parse_class("ANTHROPIC PBC SER F-1 CVT PFD PP").label() == "PFD:F-1"
    assert parse_class("Anthropic PBC, Series F1").label() == "PFD:F-1"


def test_pc_marks_preferred(con):
    """Fidelity's 'PC' token. Verified against ASSET_CAT, which the parser
    never reads: every universe holding whose title contains ' PC ' is tagged
    EP by its filer, and none is tagged EC."""
    assert parse_class("ANTHROPIC PBC SERIES F PC PP").kind == PREFERRED
    bad = con.execute("""
        SELECT count(*) FROM u
        WHERE (upper(ISSUER_TITLE) LIKE '% PC %' OR upper(ISSUER_TITLE) LIKE '% PC')
          AND ASSET_CAT IN ('EC', 'OTHER')
    """).fetchone()[0]
    assert bad == 0, f"{bad} holdings contradict the PC rule -- the grammar has drifted"


def test_truncated_preferred_marker_is_read():
    """'SER E P' is SpaceX preferred, priced in the 810-5,265 band while the
    same filer's common sits at 70-527."""
    assert parse_class("SPACE EXPLORATION TECH SER E P").kind == PREFERRED


def test_a_bare_series_letter_means_preferred():
    """Private companies do not issue 'Series G common'."""
    assert parse_class("Databricks, Inc., Series G").kind == PREFERRED
    assert parse_class("DATABRICKS, INC. SERES G   /").kind == PREFERRED


def test_spacex_class_letters_mean_common():
    assert parse_class("Space Exploration Technologies Corp., Class A").kind == COMMON


def test_a_convertible_right_is_not_a_share_price():
    """'OPEN AI GLOBAL LLC CONVERTIBLE INTEREST RT PP' carries balance equal to
    value, so it prices at exactly 1.00. That is a dollar commitment, not a
    share price, and it must never reach the marks panel."""
    parsed = parse_class("OPEN AI GLOBAL LLC CONVERTIBLE INTEREST RT PP")
    assert parsed.basis == BASIS_NOT_A_SHARE_PRICE
    assert parse_class("OPENAI GLOBAL LLC RTS 1:1 @ USD PP (DRS)").basis == BASIS_NOT_A_SHARE_PRICE
    assert parse_class("AESTAS LLC dba OPENAI LLC EV UNITS PP").basis == BASIS_NOT_A_SHARE_PRICE


def test_a_blended_line_is_not_attributable_to_one_class():
    """'55% Class A Common Stock and 45% Class C Common Stock' on one holding
    line: the price is a weighted blend and belongs to neither class."""
    parsed = parse_class(
        "MWAM VC SpaceX-II, LLC (economic exposure to Space Exploration "
        "Technologies Corp., 55% Class A Common Stock and 45% Class C Common Stock)"
    )
    assert parsed.basis == BASIS_BLENDED


def test_an_ordinary_share_keeps_the_per_share_basis():
    assert parse_class("DATABRICKS SER H CVT PFD STOCK PP").basis == BASIS_PER_SHARE


# --------------------------------------------------------------------------
# The matcher
# --------------------------------------------------------------------------

def test_the_missed_fidelity_spelling_now_resolves():
    """'XAI CORP' is 82 holdings the frozen pattern set does not select. It is
    the largest single recall gap this week found."""
    match = resolve("XAI CORP", "xAI Corp SER C PC PP")
    assert match.company == "X.AI Corp"
    assert match.score == 1.0


def test_lei_outranks_the_name():
    """A registered identifier is identity; a name is a heuristic."""
    match = resolve("SOME UNRECOGNISED WRAPPER LLC", None, "984500B6DEB8CEBC4Z70")
    assert match.company == "Anthropic PBC"
    assert match.method == "lei"


def test_every_verified_lei_maps_to_exactly_one_company():
    """The short-circuit is only sound if no LEI spans two issuers."""
    assert len(ISSUER_LEIS) == len(set(ISSUER_LEIS)), "duplicate LEI keys"
    for lei in ISSUER_LEIS:
        assert len(lei) == 20, f"{lei} is not a 20-character LEI"


def test_verified_leis_are_never_shared_across_companies(con):
    rows = con.execute("""
        SELECT ISSUER_LEI, count(DISTINCT COMPANY) FROM u
        WHERE length(ISSUER_LEI) = 20 GROUP BY 1 HAVING count(DISTINCT COMPANY) > 1
    """).fetchall()
    assert rows == [], f"an LEI appears on more than one company: {rows}"


@pytest.mark.parametrize(
    "name",
    [
        "RELATIVITY SPACE INC",          # a real space company, not SpaceX
        "SPACESHIP PURCHASER, INC.",
        "SPACE INTERMEDIATE III, INC.",
        "ANYSCALE, INC.",
        "SCALED AGILE INC",
        "HYPERSCALE DATA INC",
        "GROUNDWORKS, LLC",
        "GROTECH VENTURES IV LP",
        "COHERE TECHNOLOGIES, INC. PREFERRED SERIES D-1   /",
        "OPEN SPACE LABS INC",
        "OPENMARKET INC.",
        "WORLD LABS",
        "Figure Technologies, Inc.",
        "XAIE-LMBK.AF",
    ],
)
def test_near_misses_are_rejected(name):
    """Each of these is in the private layer, scores >= 82 against a universe
    token on partial_ratio, and is a different company."""
    assert resolve(name).company is None, f"{name} was claimed"


def test_token_set_ratio_cannot_separate_right_from_wrong():
    """The reason the matcher has a gate and not just a threshold: a subset
    scores as a perfect match, so one true positive and two false positives all
    sit at exactly 100 and no cut-off can tell them apart."""
    from rapidfuzz import fuzz

    assert fuzz.token_set_ratio("FIGURE", "FIGURE AI") == 100  # wrong company
    assert fuzz.token_set_ratio("OPEN BAY AUTOS AI", "OPEN AI") == 100  # wrong company
    assert fuzz.token_set_ratio("ANDURIL ENGINEERING", "ANDURIL") == 100  # right company


def test_the_coverage_gate_rejects_what_it_can():
    """The gate is a necessary condition evaluated before any score. It rejects
    'FIGURE' (nothing accounts for AI) and 'RELATIVITY SPACE' (nothing accounts
    for EXPLORATION, and SPACE scores 90.9 against SPACEX, below the gate)."""
    assert resolve("Figure Technologies, Inc.").company is None
    assert resolve("RELATIVITY SPACE INC").company is None
    assert resolve("Anduril Engineering LLC").company == "Anduril Industries, Inc."


def test_token_sim_is_92_because_space_scores_909_against_spacex():
    from rapidfuzz import fuzz

    assert fuzz.ratio("SPACE", "SPACEX") < TOKEN_SIM
    assert fuzz.ratio("ANTHROPICS", "ANTHROPIC") >= TOKEN_SIM


def test_a_transparent_spv_resolves_to_its_underlying():
    for name, expected in [
        ("U First Capital Fund III LLC (SpaceX)", "Space Exploration Technologies Corp."),
        ("Studio Type One Soul II LLC (OpenAI)", "OpenAI Group PBC"),
        (
            "TIGER GLOBAL PIP 12-1, LLC (INVESTED IN DATABRICKS, INC., PREFERRED SERIES G)",
            "Databricks, Inc.",
        ),
        (
            "Magnitude ANC III, LLC (economic exposure to Anthropic PBC. Series B Preferred Shares)",
            "Anthropic PBC",
        ),
    ]:
        match = resolve(name)
        assert match.company == expected, name
        assert match.wrapper == "spv_transparent"
        assert match.score <= 0.95, "an unwrapped SPV is never as certain as a direct name"


@pytest.mark.parametrize(
    "name", ["FSOIFD TC HOLDINGS LLC", "FSOIFD VETERINARY Holdings LLC", "FSOIFDA FHUS HOLDINGS LLC"]
)
def test_an_opaque_spv_resolves_to_nothing_and_is_flagged_as_a_wrapper(name):
    """The filing names a Fidelity vehicle and no underlying. Returning nothing
    is correct; returning a guess is not. Flagging it as a wrapper is what
    separates 'we cannot tell' from 'this is somebody else'."""
    match = resolve(name)
    assert match.company is None
    assert match.wrapper == "spv_opaque"


def test_typos_are_absorbed():
    assert resolve("SPACE EXPLORATION TECHNOLOGICS").company == (
        "Space Exploration Technologies Corp."
    )
    assert resolve("X.AI, CORP. PERFERRED SERIES C   /").company == "X.AI Corp"
    assert resolve("DATABRICKS SER G CVY PFD STCK PP").company == "Databricks, Inc."


def test_blocking_reduces_the_candidate_set():
    """Eleven companies makes brute force free, but the production input is 3.2
    million distinct names, so the reduction is measured rather than assumed.

    Blocking is a recall-preserving filter and nothing more: it must never drop
    a name the scorer would have accepted, and it is allowed to keep names the
    scorer then rejects. 'PUBLIC JOINT STOCK COMPANY PHOSAGRO' survives
    blocking on the trigram 'GRO' it shares with GROQ, and is rejected a step
    later -- that division of labour is the point."""
    candidates, total = blocking_stats(normalise_name("ANTHROPIC PBC"))
    assert 1 <= candidates < total
    assert blocking_stats(normalise_name("DATABRICKS INC"))[0] == 1
    survives, total = blocking_stats(normalise_name("PUBLIC JOINT STOCK COMPANY PHOSAGRO"))
    assert survives < total
    assert resolve("PUBLIC JOINT STOCK COMPANY PHOSAGRO").company is None


def test_aliases_are_self_names_not_filer_spellings():
    """An alias table stuffed with observed spellings would score perfectly on
    the golden set and predict nothing about next quarter. Fourteen entries for
    eleven companies is the budget."""
    total = sum(len(v) for v in ALIASES.values())
    assert total <= 16, f"{total} aliases -- the table is memorising spellings"


# --------------------------------------------------------------------------
# Baseline A is a faithful mirror of the shipped SQL
# --------------------------------------------------------------------------

def test_python_and_sql_pattern_rules_agree(con):
    """like_pattern_company() must call every corpus name exactly what
    universe.company_case_expr() calls it. Any disagreement makes the baseline
    a different system from the one Week 2 shipped, and the comparison a lie."""
    rows = con.execute(f"""
        SELECT DISTINCT ISSUER_NAME, {company_case_expr()} AS SQL_COMPANY FROM u
    """).fetchall()
    assert rows, "no rows to compare"
    mismatches = [
        (name, sql, like_pattern_company(name))
        for name, sql in rows
        if like_pattern_company(name) != sql
    ]
    assert mismatches == [], f"{len(mismatches)} disagreements, e.g. {mismatches[:3]}"


# --------------------------------------------------------------------------
# Golden-set integrity
# --------------------------------------------------------------------------

def test_golden_set_is_well_formed(golden):
    entries = golden["entries"]
    assert 200 <= len(entries) <= 400, f"{len(entries)} entries"
    assert len({e["id"] for e in entries}) == len(entries), "duplicate ids"
    required = {
        "id", "issuer_name", "issuer_title", "strata", "holdings", "company",
        "evidence_class", "label_reason", "share_class", "price_basis",
    }
    for entry in entries:
        assert required <= set(entry), f"{entry.get('id')} is missing {required - set(entry)}"
        assert entry["strata"], f"{entry['id']} has no stratum"
        assert entry["label_reason"], f"{entry['id']} has a label with no reason"
        assert entry["holdings"] >= 1


def test_every_label_is_a_known_company_or_an_explicit_non_answer(golden):
    allowed = set(ALIASES) | {"NOT_IN_UNIVERSE", "UNKNOWN"}
    for entry in golden["entries"]:
        assert entry["company"] in allowed, f"{entry['id']}: {entry['company']}"


def test_the_fixture_still_matches_the_frame_it_was_built_from(golden):
    """Re-derive every label from the committed sampling frame and compare.

    This is the cheap half of a reproducibility check -- it does not re-run the
    3.2-million-name sweep, but it does catch the labelling procedure drifting
    away from the fixture it produced, which is the failure that would quietly
    invalidate every metric in docs/entity_resolution.md.

    The expensive half was checked by hand: the frame builder now rebuilds
    byte-identically across runs. It did not at first -- DuckDB's DISTINCT
    gives no ordering guarantee and process.extract() breaks equal scores by
    input position, so the frame came out with 322 strings on one run and 323
    on the next."""
    from scripts.label_golden_set import FRAME, build

    if not FRAME.exists():
        pytest.skip("frame absent -- run python -m scripts.build_golden_candidates")
    rebuilt = {e["id"]: e for e in build()["entries"]}
    committed = {e["id"]: e for e in golden["entries"]}
    assert set(rebuilt) == set(committed), "the fixture and the frame disagree on which strings"
    drifted = [
        (i, committed[i]["company"], rebuilt[i]["company"])
        for i in committed
        if committed[i]["company"] != rebuilt[i]["company"]
        or committed[i]["evidence_class"] != rebuilt[i]["evidence_class"]
        or committed[i]["share_class"] != rebuilt[i]["share_class"]
    ]
    assert drifted == [], f"{len(drifted)} labels drifted, e.g. {drifted[:3]}"


def test_the_attestation_records_its_own_scope(golden):
    """The labels are agent-assigned and a human attested to part of them. Both
    halves have to be legible, which is the whole of P1: a machine may propose a
    label, only a human may attest, and an attestation that does not say what it
    covers is worth less than none."""
    attestation = golden["human_attestation"]
    assert attestation, "attestation missing"
    assert "agent" in golden["labelled_by"]
    for field in ("by", "date", "scope", "voids_on", "golden_set_version"):
        assert attestation.get(field), f"attestation has no {field}"
    assert attestation["golden_set_version"] == golden["golden_set_version"]
    assert "Did NOT review" in attestation["scope"], "the scope must say what it excludes"


def test_the_withdrawn_attestation_is_not_counted_as_confirmed(golden):
    """OPENAIR.COM was attested as NOT_IN_UNIVERSE and the attestation was
    withdrawn the same day, because the reason given for that label was factually
    wrong. The corrected label is OpenAI Group PBC and is not attested. An
    approval obtained on a false statement must not survive the correction."""
    attestation = golden["human_attestation"]
    withdrawn = attestation.get("attestation_withdrawn", [])
    assert "OPENAIR.COM" in withdrawn
    confirmed = set(attestation["confirmed_merges"]) | set(
        attestation["confirmed_not_in_universe"]
    )
    assert confirmed.isdisjoint(set(withdrawn))
    entry = next(e for e in golden["entries"] if e["issuer_name"] == "OPENAIR.COM")
    assert entry["company"] == "OpenAI Group PBC"


def test_openair_dot_com_is_openai():
    """Five holdings -- BlackRock's three and New York Life's two -- titled
    'OpenAir.com, Series C' at 687.6869, which is the OpenAI Series C consensus
    to four decimals on both period ends they appear in.

    This is the entry the golden set earned its keep on. It was labelled
    NOT_IN_UNIVERSE, attested as such, and both were wrong."""
    match = resolve("OpenAir.com", "OpenAir.com, Series C")
    assert match.company == "OpenAI Group PBC"
    assert match.score >= 0.90, "it must land in the auto-accept band, not the review band"


def test_the_plan_s_named_hard_cases_are_all_present(golden):
    """plan.md week 4 names five. A sampling change that drops one of them
    changes what the metrics mean, so it has to fail here."""
    strata = {s for entry in golden["entries"] for s in entry["strata"]}
    for tag in (
        "S3_anthropic_variants",
        "S3_opaque_spv",
        "S3_ark_ec_tagged_preferred",
        "S3_spacex_10x",
        "S3_world_labs_c_prime",
    ):
        assert tag in strata, f"{tag} fell out of the sample"


def test_the_five_anthropic_title_variants_are_covered(golden):
    """plan.md calls for the five known Anthropic variants. The corpus has
    more than five distinct title forms; all of them are in the set."""
    variants = {
        entry["issuer_title"]
        for entry in golden["entries"]
        if entry["company"] == "Anthropic PBC"
    }
    assert len(variants) >= 5, sorted(variants)


def test_opaque_wrappers_are_unknown_not_negative(golden):
    """'FSOIFD TC HOLDINGS LLC' holds something priced at $590 to $889 a share
    and the filing does not say what. Labelling it NOT_IN_UNIVERSE would be a
    claim the filing cannot support."""
    opaque = [e for e in golden["entries"] if "S3_opaque_spv" in e["strata"]]
    assert opaque
    for entry in opaque:
        assert entry["company"] == "UNKNOWN", f"{entry['id']} was labelled {entry['company']}"


def test_world_labs_c_and_c_prime_are_labelled_as_different_classes(golden):
    classes = {
        entry["issuer_title"]: entry["share_class"]
        for entry in golden["entries"]
        if "WORLD LABS" in entry["issuer_name"]
    }
    prime = {t: c for t, c in classes.items() if "PRIME" in t}
    plain = {t: c for t, c in classes.items() if "PRIME" not in t and "C" in t}
    assert prime and plain
    assert set(prime.values()).isdisjoint(set(plain.values()))


# --------------------------------------------------------------------------
# The pinned baseline
#
# Measured on golden set v1.0.0 -- see docs/entity_resolution.md. These are
# floors, not targets: a change that lowers them fails here and has to be
# argued for in the RUN_LOG rather than absorbed.
# --------------------------------------------------------------------------

BASELINE = {
    # (subset, system, weighting): (precision, recall)
    ("all", "B_matcher_v1", "macro"): (0.9959, 1.0000),
    ("all", "B_matcher_v1", "micro"): (0.9998, 1.0000),
    ("hard", "B_matcher_v1", "macro"): (0.9929, 1.0000),
    ("all", "A_like_patterns", "macro"): (0.9916, 0.9792),
    # Baseline A has perfect precision on the hard subset and matcher v1 does
    # not. Pinned because it is the uncomfortable half of the result and should
    # not be allowed to quietly disappear: v1's case rests on recall.
    ("hard", "A_like_patterns", "macro"): (1.0000, 0.9929),
}


def test_measured_precision_and_recall_do_not_regress(golden):
    from scripts.score_matcher import score

    entries = golden["entries"]
    hard = [e for e in entries if e["evidence_class"] not in ("E2_self_name", "E0_none")]
    subsets = {"all": entries, "hard": hard}
    systems = {
        "A_like_patterns": lambda e: like_pattern_company(e["issuer_name"]),
        "B_matcher_v1": lambda e: (
            resolve(e["issuer_name"], e["issuer_title"]).company
        ),
    }
    weights = {"macro": lambda e: 1, "micro": lambda e: e["holdings"]}

    for (subset, system, weighting), (precision, recall) in BASELINE.items():
        result = score(subsets[subset], systems[system], weights[weighting])["overall"]
        assert result["precision"] >= precision - 1e-4, (
            f"{subset}/{system}/{weighting} precision fell to {result['precision']}"
        )
        assert result["recall"] >= recall - 1e-4, (
            f"{subset}/{system}/{weighting} recall fell to {result['recall']}"
        )


def test_matcher_v1_beats_the_frozen_patterns_on_recall(golden):
    """The reason this week's work exists. If this ever fails, the deterministic
    matcher is not earning its place and the honest move is to say so."""
    from scripts.score_matcher import score

    entries = golden["entries"]
    a = score(entries, lambda e: like_pattern_company(e["issuer_name"]))["overall"]
    b = score(entries, lambda e: resolve(e["issuer_name"], e["issuer_title"]).company)["overall"]
    assert b["recall"] > a["recall"]
    assert b["fn"] < a["fn"]


def test_matcher_v1_does_not_have_the_better_precision(golden):
    """Stated as a test so it cannot be quietly forgotten: on the hard subset
    the frozen Week 2 patterns have perfect precision and matcher v1 does not,
    because v1 claims OPEN BAY AUTOS AI INC. and the patterns do not. v1's case
    is recall -- 85 holdings of XAI CORP that the patterns miss entirely -- not
    precision, and overstating it would be the easy lie here."""
    from scripts.score_matcher import score

    hard = [e for e in golden["entries"]
            if e["evidence_class"] not in ("E2_self_name", "E0_none")]
    a = score(hard, lambda e: like_pattern_company(e["issuer_name"]))["overall"]
    b = score(hard, lambda e: resolve(e["issuer_name"], e["issuer_title"]).company)["overall"]
    assert a["precision"] == 1.0
    assert b["precision"] < a["precision"]
    assert b["recall"] > a["recall"]


def test_the_one_known_false_positive_is_still_the_only_one(golden):
    """'OPEN BAY AUTOS AI INC.' is a used-car marketplace whose name happens to
    contain the tokens OPEN and AI in that order, which is the whole of the
    two-token 'OPEN AI' alias. It scores 0.80, and so do three correct blended
    SpaceX SPVs -- so no single threshold separates them. That tie is the
    argument for a review band, and it is pinned here."""
    from scripts.score_matcher import score

    errors = score(
        golden["entries"], lambda e: resolve(e["issuer_name"], e["issuer_title"]).company
    )["errors"]
    assert [e["issuer_name"] for e in errors] == ["OPEN BAY AUTOS AI INC."]
    assert resolve("OPEN BAY AUTOS AI INC.").score == 0.80
    blended = resolve(
        "MWAM VC SPACEX-II, LLC (ECONOMIC EXPOSURE TO SPACE EXPLORATION TECHNOLOGIES "
        "CORP., 55% CLASS A COMMON STOCK AND 45% CLASS C COMMON STOCK)"
    )
    assert blended.company == "Space Exploration Technologies Corp."
    assert blended.score == 0.80, "the tie that makes a single threshold impossible"
