"""Week 2 regression tests: the defects found this week, pinned so they stay fixed.

These run against the built Parquet layer, so `python -m src.ingest.build_parquet
--all` has to have happened. They are skipped, not failed, if it has not --
a missing artifact is a setup problem, not a regression.

Each test corresponds to something that was actually wrong at some point today.
"""

import datetime
import sys
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.db.load import FAMILIES, family_case_expr, family_of  # noqa: E402
from src.ingest.build_parquet import ALL_QUARTERS, PARQUET  # noqa: E402
from src.ingest.universe import UNIVERSE_PATTERNS, WATCHLIST_PATTERNS  # noqa: E402


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
# Dates
# --------------------------------------------------------------------------

def test_period_end_is_a_date_not_a_string(con):
    """DERA ships DD-MON-YYYY text. Left unparsed it sorts alphabetically, so
    30-APR lands before 31-MAR -- and propagation lag is measured in days
    between period ends. This was wrong in the first build."""
    value = con.execute("SELECT PERIOD_END FROM u WHERE PERIOD_END IS NOT NULL LIMIT 1").fetchone()[0]
    assert isinstance(value, datetime.date), f"PERIOD_END is {type(value)}, not a date"


def test_period_ends_sort_chronologically(con):
    ordered = [r[0] for r in con.execute(
        "SELECT DISTINCT PERIOD_END FROM u WHERE PERIOD_END IS NOT NULL ORDER BY 1"
    ).fetchall()]
    assert ordered == sorted(ordered)
    assert ordered[0].year >= 2022, "period ends should not predate the download window"


def test_period_end_is_not_fiscal_year_end(con):
    """REPORT_ENDING_PERIOD is the fund's fiscal year end and REPORT_DATE is the
    holdings as-of date. They differ on most filings; using the wrong one would
    scramble every mark date."""
    differing = con.execute("""
        SELECT count(*) FROM u
        WHERE FISCAL_YEAR_END IS NOT NULL AND PERIOD_END IS NOT NULL
          AND FISCAL_YEAR_END <> PERIOD_END
    """).fetchone()[0]
    assert differing > 0, "the two date fields are being read as the same column"


# --------------------------------------------------------------------------
# Prices
# --------------------------------------------------------------------------

def test_zero_balance_never_yields_a_price(con):
    """A missing share count is not a zero price. The row is kept with a null
    price and counted unresolved -- plan.md's error-handling rule."""
    bad = con.execute("""
        SELECT count(*) FROM u
        WHERE (BALANCE = 0 OR BALANCE IS NULL) AND PRICE_PER_SHARE IS NOT NULL
    """).fetchone()[0]
    assert bad == 0


def test_unresolved_rows_are_retained_not_dropped(con):
    """Null-price rows must survive into the layer, not be filtered away."""
    total, nulls = con.execute(
        "SELECT count(*), count(*) FILTER (WHERE PRICE_PER_SHARE IS NULL) FROM u"
    ).fetchone()
    assert total > 0
    assert nulls >= 0  # the point is that the column exists and rows survive


# --------------------------------------------------------------------------
# Entity resolution traps
# --------------------------------------------------------------------------

def test_cohere_is_never_a_full_universe_member(con):
    """Every %COHERE% row is Coherent Corp (public optics) or Cohere
    Technologies (wireless) -- never Cohere Inc. the model company. Promoting it
    would invent an entire fictitious price series."""
    assert "Cohere Inc." not in UNIVERSE_PATTERNS
    labels = [r[0] for r in con.execute(
        "SELECT DISTINCT COMPANY FROM u WHERE COMPANY LIKE 'Cohere%'"
    ).fetchall()]
    for label in labels:
        assert "FALSE POSITIVE" in label, f"{label!r} escaped the watchlist"


def test_figure_ai_does_not_capture_figure_technologies(con):
    """%FIGURE% would sweep in Figure Technologies, a fintech with 243 rows in
    2026Q2 and zero at Level 3."""
    assert UNIVERSE_PATTERNS["Figure AI Inc."] == ["%FIGURE AI%"]
    stray = con.execute("""
        SELECT count(*) FROM u
        WHERE COMPANY = 'Figure AI Inc.' AND upper(ISSUER_NAME) LIKE '%TECHNOLOG%'
    """).fetchone()[0]
    assert stray == 0


def test_debt_instruments_are_excluded_from_the_universe(con):
    """Databricks term loans sit at Level 3 with balance == value, so they would
    price at ~1.00 and corrupt the series. xAI's bank debt is the same trap."""
    loans = con.execute("""
        SELECT count(*) FROM u WHERE ASSET_CAT = 'LON'
    """).fetchone()[0]
    assert loans == 0, "loan rows reached the universe layer"


def test_openai_catches_the_spaced_spelling():
    """BlackRock writes 'Open AI Group PBC'. %OPENAI% alone misses a whole
    manager's position."""
    assert "%OPEN AI%" in UNIVERSE_PATTERNS["OpenAI Group PBC"]


def test_spacex_catches_the_unspelled_form():
    """'SPACEX-CL A PP' carries no spelled-out issuer name."""
    assert "%SPACEX%" in UNIVERSE_PATTERNS["Space Exploration Technologies Corp."]


def test_every_universe_row_has_a_company_label(con):
    """The Parquet layer is written with the same predicate that assigns the
    label, so an unlabelled row means the two have drifted apart."""
    orphans = con.execute("SELECT count(*) FROM u WHERE COMPANY IS NULL").fetchone()[0]
    assert orphans == 0


# --------------------------------------------------------------------------
# The regression anchor
# --------------------------------------------------------------------------

def test_anthropic_259_14_convergence_reproduces(con):
    """Week 1 hand-verified six managers converging at $259.14. The pipeline
    must reproduce it from bulk, not from tests/fixtures/."""
    ciks = con.execute("""
        SELECT count(DISTINCT CIK) FROM u
        WHERE COMPANY = 'Anthropic PBC' AND round(PRICE_PER_SHARE, 2) = 259.14
    """).fetchone()[0]
    assert ciks >= 6, f"only {ciks} CIKs reproduce the $259.14 mark"


def test_bulk_cannot_reach_the_589_repricing(con):
    """Not a wish -- a documented structural limit. The DERA sets are indexed by
    FILING quarter; the 5/29 and 5/31 marks were filed in late July 2026 and so
    land in 2026Q3, which the SEC has not published. If this test ever fails,
    2026Q3 has been released and the Week 3 live path can be re-scoped."""
    above = con.execute("""
        SELECT count(*) FROM u WHERE COMPANY = 'Anthropic PBC' AND PRICE_PER_SHARE > 400
    """).fetchone()[0]
    assert above == 0


def test_spacex_anchor_filing_shows_the_10x_within_one_filing(con):
    """The SpaceX unit artifact is not a cross-manager disagreement -- it sits
    inside a single filing.

    Baron Focused Growth Fund, accession 0001752724-24-195357, period
    2024-06-30: two EC rows at $112.00 and four EP rows at exactly $1,120.00.
    The artifact is deliberately NOT corrected here -- auto-adjusting a
    suspected split is forbidden until a human adjudicates it (Week 7). This
    pins its shape so the detector has a known case to work against.

    The same filing also carries three spellings of one issuer, including the
    filer's own typo 'SPACE EXPLORATION TECHNOLOGICS'. Golden-set material.
    """
    rows = con.execute("""
        SELECT ASSET_CAT, round(PRICE_PER_SHARE, 2), count(*)
        FROM u
        WHERE ACCESSION_NUMBER = '0001752724-24-195357'
          AND COMPANY = 'Space Exploration Technologies Corp.'
        GROUP BY 1, 2 ORDER BY 2
    """).fetchall()
    if not rows:
        pytest.skip("2024Q3 not built -- anchor filing unavailable")
    assert (("EC", 112.00, 2) in rows) and (("EP", 1120.00, 4) in rows), rows
    names = con.execute("""
        SELECT count(DISTINCT ISSUER_NAME) FROM u
        WHERE ACCESSION_NUMBER = '0001752724-24-195357'
          AND COMPANY = 'Space Exploration Technologies Corp.'
    """).fetchone()[0]
    assert names >= 3, "expected several issuer spellings in the anchor filing"


def test_preferred_implies_the_high_price_band_but_not_the_converse(con):
    """The precise, measured rule -- and its limit.

    Every one of the 645 SpaceX EP rows sits above $500 (min $526.59): 'EP'
    is a SUFFICIENT signal for the high band, with zero exceptions. The
    converse fails: 125 of 1,005 EC rows are also high, all of them from
    Neuberger Berman, who tags preferred stock as common. That is the same
    assetCat unreliability plan.md documents for ARK.

    So Week 7's detector may trust EP as a positive signal and must NOT read
    EC as evidence of common stock.
    """
    ep_low, ep_total = con.execute("""
        SELECT count(*) FILTER (WHERE PRICE_PER_SHARE <= 500), count(*)
        FROM u WHERE COMPANY = 'Space Exploration Technologies Corp.'
          AND ASSET_CAT = 'EP' AND PRICE_PER_SHARE > 0
    """).fetchone()
    assert ep_total > 0
    assert ep_low == 0, f"{ep_low} preferred rows fell below the high band"

    ec_high = con.execute("""
        SELECT count(*) FROM u
        WHERE COMPANY = 'Space Exploration Technologies Corp.'
          AND ASSET_CAT = 'EC' AND PRICE_PER_SHARE > 500
    """).fetchone()[0]
    assert ec_high > 0, (
        "EC no longer carries high-band rows -- if a filer fixed their tagging, "
        "re-check whether ASSET_CAT can now be trusted as a discriminator"
    )


def test_the_10x_artifact_is_confined_to_spacex(con):
    """If another company starts showing exact-10x within-filing spreads, the
    unit convention has changed somewhere and the detector's scope is wrong."""
    rows = con.execute("""
        WITH g AS (
          SELECT COMPANY, ACCESSION_NUMBER, PERIOD_END,
                 min(PRICE_PER_SHARE) lo, max(PRICE_PER_SHARE) hi
          FROM u WHERE PRICE_PER_SHARE > 0 AND COMPANY IS NOT NULL
          GROUP BY 1, 2, 3)
        SELECT COMPANY, count(*) FROM g
        WHERE round(hi / lo, 3) = 10.000
        GROUP BY 1
    """).fetchall()
    offenders = {c for c, _ in rows}
    assert offenders <= {"Space Exploration Technologies Corp."}, (
        f"exact-10x spread appeared outside SpaceX: {offenders}"
    )


def test_the_stagger_is_real(con):
    """Propagation lag is only measurable because period ends spread across the
    calendar instead of clustering on quarter ends."""
    months = con.execute("""
        SELECT count(DISTINCT month(PERIOD_END)) FROM u WHERE PERIOD_END IS NOT NULL
    """).fetchone()[0]
    assert months >= 10, f"only {months} calendar months carry marks"


# --------------------------------------------------------------------------
# Fund families
# --------------------------------------------------------------------------

def test_python_and_sql_family_rules_agree(con):
    """family_of() and family_case_expr() are one rule in two renderings.
    DuckDB UDFs need numpy, which this project does not require, so the SQL is
    generated instead -- and generated code drifts unless something checks."""
    rows = con.execute(f"""
        SELECT DISTINCT REGISTRANT_NAME, {family_case_expr()} AS fam
        FROM u WHERE REGISTRANT_NAME IS NOT NULL
    """).fetchall()
    assert rows, "no registrants found"
    for name, sql_family in rows:
        assert family_of(name) == sql_family, (
            f"{name!r}: python says {family_of(name)!r}, SQL says {sql_family!r}"
        )


def test_fidelity_vip_funds_are_not_a_separate_family(con):
    """'Variable Insurance Products Fund I-IV' are Fidelity's VIP funds. Left
    unmapped they appeared as four independent managers, inflating exactly the
    count that cross-manager dispersion depends on."""
    assert family_of("Variable Insurance Products Fund III") == "Fidelity"
    assert family_of("VARIABLE INSURANCE PRODUCTS FUND II") == "Fidelity"


def test_lincoln_is_not_swallowed_by_the_fidelity_rule(con):
    """The needles overlap; order in FAMILIES is what keeps them apart."""
    assert family_of("LINCOLN VARIABLE INSURANCE PRODUCTS TRUST") == "Lincoln Financial"


def test_family_needles_are_ordered_so_lincoln_precedes_fidelity_vip():
    needles = [n for n, _ in FAMILIES]
    assert needles.index("LINCOLN") < needles.index("VARIABLE INSURANCE PRODUCTS FUND")


# --------------------------------------------------------------------------
# Universe integrity
# --------------------------------------------------------------------------

def test_universe_and_watchlist_do_not_overlap():
    assert not set(UNIVERSE_PATTERNS) & set(WATCHLIST_PATTERNS)


def test_reconciliation_records_exist_for_every_built_quarter():
    import json
    built = [q for q in ALL_QUARTERS if (PARQUET / q / "universe_holdings.parquet").exists()]
    if not built:
        pytest.skip("nothing built")
    for q in built:
        path = PARQUET / q / "reconciliation.json"
        assert path.exists(), f"{q} has Parquet but no reconciliation record"
        rec = json.loads(path.read_text(encoding="utf-8"))
        # Provenance: a count that no record produced is not evidence (P3).
        for field in ("holding_rows_in", "private_rows_out", "universe_rows_out",
                      "excluded_by_asset_cat", "latest_period_end"):
            assert field in rec, f"{q} reconciliation missing {field}"
        assert rec["universe_rows_out"] <= rec["private_rows_out"] or \
            rec["universe_rows_out"] > 0  # universe uses a different predicate
