"""Week 7: the marks panel and the split detector.

The pure tests need nothing. The rest build a small synthetic corpus in their
own throwaway database -- one holding per hazard -- and skip, loudly, when no
Postgres answers. They never touch DATABASE_URL: the project's own database is
not a test fixture.

Every hazard in the corpus is a real one taken from the filings:

  amendment       one fund/period filed twice, the amendment restating it
  two lots        one security on two lines, to be summed and not averaged
  blended         two lines, same title and category, ten times apart
  rights          a title that prices per dollar, not per share
  split           a 10x step between consecutive periods
  repricing       a 2.06x step, which is a round and not a split
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import psycopg2
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.marks.build import (  # noqa: E402
    BLEND_TOLERANCE,
    build_marks,
    build_securities,
    classify,
    coverage,
)
from src.marks.splits import (  # noqa: E402
    LARGE_MOVE_RATIO,
    adjudicate,
    SPLIT_MAX_RATIO,
    SPLIT_MIN_RATIO,
    SPLIT_TOLERANCE,
    detect,
    is_split_ratio,
)

SCHEMA = ROOT / "src" / "db" / "schema.sql"
CANDIDATE_URLS = [
    os.getenv("REVIEW_TEST_DB_URL"),
    "postgresql://postgres:postgres@127.0.0.1:55432/postgres",
    "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
]


# --------------------------------------------------------------------------
# The split rule
# --------------------------------------------------------------------------


def test_the_split_rule_catches_the_case_plan_md_names():
    """plan.md's verification list requires that Perplexity's 695 -> 58 is
    flagged. That ratio is 11.93.

    Week 6 used an absolute window of 0.02, which misses it by a factor of
    three -- the rule looked right because the other Perplexity step lands on
    exactly 10.000. A relative 1% window catches both.
    """
    assert is_split_ratio(11.93)
    assert abs(11.93 - 12) > 0.02, "an absolute 0.02 window would have missed this"
    assert is_split_ratio(10.0)


def test_the_split_rule_leaves_repricings_alone():
    """X.AI reprices at 2.064x forty-four times, Cerebras at 2.457x, Figure AI
    at 8.299x. None is near-integer and none may be quarantined: a repricing is
    the signal this project exists to measure."""
    for ratio in (2.064, 2.457, 2.732, 8.299, 1.87):
        assert not is_split_ratio(ratio), ratio


def test_the_cap_is_what_excludes_the_placeholder_artifact():
    """OpenAI's $1.00 convertible-right rows produce ratios in the hundreds
    against a real mark. They are excluded by the cap, not by the tolerance --
    which is the whole reason the cap exists."""
    assert not is_split_ratio(320.539)
    assert not is_split_ratio(348.5255)
    assert SPLIT_MAX_RATIO == 20
    assert is_split_ratio(float(SPLIT_MAX_RATIO))
    assert not is_split_ratio(SPLIT_MAX_RATIO + 1)


def test_the_split_rule_is_symmetric_and_bounded_below():
    assert is_split_ratio(float(SPLIT_MIN_RATIO))
    assert not is_split_ratio(1.999)      # below the floor
    assert not is_split_ratio(None)
    assert SPLIT_TOLERANCE == 0.01
    assert LARGE_MOVE_RATIO == 2.0


# --------------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------------


def test_the_title_beats_the_filed_category():
    """ARK tags preferred stock as EC. A title that says SERIES F is preferred
    whatever the filer ticked."""
    label, basis = classify("ANTHROPIC PBC SERIES F PC PP", "EC")
    assert label == "PFD:F"
    assert basis == "per_share"


def test_the_category_fills_in_when_the_title_is_silent():
    """BlackRock files `ANTHROPIC PBC` with no class at all. Without the
    category fallback every such line would be UNKNOWN and common would merge
    with preferred."""
    assert classify("ANTHROPIC PBC", "EC")[0] == "COM:UNSPECIFIED"
    assert classify("ANTHROPIC PBC", "EP")[0] == "PFD:UNSPECIFIED"
    assert classify("ANTHROPIC PBC", None)[0] == "UNKNOWN"


def test_some_titles_are_not_share_prices_at_all():
    """`CVT INT RIGHTS` prices per dollar of right and `EV UNITS` per vehicle
    unit. Publishing either as a share price is how $1.00 gets into a series."""
    for title in ("OPEN AI GLOBAL LLC CONVERTIBLE INTEREST RT PP",
                  "AESTAS LLC DBA OPENAI LLC EV UNITS PP"):
        assert classify(title, "EC")[1] != "per_share", title


def test_world_labs_c_and_c_prime_stay_apart():
    """plan.md: a genuine class differential that must survive the pipeline."""
    assert classify("WORLD LABS SER C PC PP", "EP")[0] == "PFD:C"
    assert classify("WORLD LABS SER C PRIME PC PP", "EP")[0] == "PFD:C PRIME"


# --------------------------------------------------------------------------
# Database fixtures
# --------------------------------------------------------------------------


def _reachable(url):
    try:
        conn = psycopg2.connect(url, connect_timeout=3)
    except Exception:
        return False
    conn.close()
    return True


@pytest.fixture(scope="module")
def db_url():
    for url in CANDIDATE_URLS:
        if url and _reachable(url):
            break
    else:
        pytest.skip("no Postgres reachable; set REVIEW_TEST_DB_URL to run the marks tests")

    name = f"marks_test_{uuid.uuid4().hex[:8]}"
    admin = psycopg2.connect(url)
    admin.autocommit = True
    with admin.cursor() as cur:
        cur.execute(f'CREATE DATABASE "{name}"')
    admin.close()
    yield url.rsplit("/", 1)[0] + "/" + name
    admin = psycopg2.connect(url)
    admin.autocommit = True
    with admin.cursor() as cur:
        cur.execute(f"""SELECT pg_terminate_backend(pid) FROM pg_stat_activity
                         WHERE datname = '{name}' AND pid <> pg_backend_pid()""")
        cur.execute(f'DROP DATABASE IF EXISTS "{name}"')
    admin.close()


# (period, form, title, category, balance, value) -- price is the quotient
CORPUS = [
    # one security, two lots, same price: must sum to one mark of 300 shares
    ("2025-03-31", "NPORT-P", "ACME SERIES A PC PP", "EP", 100, 1000),
    ("2025-03-31", "NPORT-P", "ACME SERIES A PC PP", "EP", 200, 2000),
    # blended: same title and category, ten times apart
    ("2025-03-31", "NPORT-P", "ACME COMMON", "EC", 100, 1000),
    ("2025-03-31", "NPORT-P", "ACME COMMON", "EC", 100, 10000),
    # not a share price
    ("2025-03-31", "NPORT-P", "ACME LLC CONVERTIBLE INTEREST RT PP", "EC", 500, 500),
    # the series that splits: 10.00 -> 100.00 -> 10.00 (a 10x step)
    ("2025-06-30", "NPORT-P", "ACME SERIES A PC PP", "EP", 100, 1000),
    ("2025-09-30", "NPORT-P", "ACME SERIES A PC PP", "EP", 100, 10000),
    # a repricing, not a split: 100.00 -> 206.40 is 2.064x
    ("2025-12-31", "NPORT-P", "ACME SERIES A PC PP", "EP", 100, 20640),
    # an amendment restating 2026-03-31: the original says 500, the amendment 900
    ("2026-03-31", "NPORT-P", "ACME SERIES A PC PP", "EP", 100, 50000),
    ("2026-03-31", "NPORT-P/A", "ACME SERIES A PC PP", "EP", 100, 90000),
]


def _build_corpus(conn):
    with conn.cursor() as cur:
        cur.execute(SCHEMA.read_text(encoding="utf-8"))
        cur.execute("INSERT INTO companies (canonical_name, status, universe_version) "
                    "VALUES ('Acme AI, Inc.', 'full', 1) RETURNING company_id")
        company_id = cur.fetchone()[0]
        cur.execute("INSERT INTO funds (cik, series_id, fund_name, family) "
                    "VALUES ('0000000001', 'S1', 'Test Fund', 'TestCo') RETURNING fund_id")
        fund_id = cur.fetchone()[0]

        filings, n = {}, 0
        for period, form, title, category, balance, value in CORPUS:
            key = (period, form)
            if key not in filings:
                cur.execute(
                    "INSERT INTO filings (fund_id, accession, form_type, period_end, "
                    "filed_date) VALUES (%s, %s, %s, %s, %s) RETURNING filing_id",
                    (fund_id, f"acc-{period}-{form}", form, period, period))
                filings[key] = cur.fetchone()[0]
            n += 1
            cur.execute("""
                INSERT INTO raw_holdings
                    (filing_id, holding_id, issuer_name, title_of_issue, asset_category,
                     currency, balance, value_usd, price_per_share, is_spv, source_quarter)
                VALUES (%s, %s, 'ACME', %s, %s, 'USD', %s, %s, %s, false, '2025q1')
                RETURNING raw_id
            """, (filings[key], f"h{n}", title, category, balance, value,
                  value / balance))
            raw_id = cur.fetchone()[0]
            cur.execute("INSERT INTO match_decisions (raw_id, company_id, method) "
                        "VALUES (%s, %s, 'alias')", (raw_id, company_id))
    conn.commit()


@pytest.fixture(scope="module")
def db(db_url):
    conn = psycopg2.connect(db_url)
    _build_corpus(conn)
    build_securities(conn)
    build_marks(conn)
    detect(conn)
    yield conn
    conn.close()


def _one(conn, sql, args=None):
    with conn.cursor() as cur:
        cur.execute(sql, args)
        return cur.fetchone()


# --------------------------------------------------------------------------
# Database tests
# --------------------------------------------------------------------------


def test_an_amendment_supersedes_its_original(db):
    """The original said $500 a share and the amendment $900. Only one mark may
    exist for that period, and it must be the amendment's."""
    row = _one(db, """
        SELECT m.price_per_share, fl.form_type
          FROM marks m JOIN filings fl ON fl.filing_id = m.filing_id
         WHERE m.period_end = DATE '2026-03-31'
    """)
    assert row is not None, "the amended period produced no mark"
    assert float(row[0]) == 900.0
    assert row[1] == "NPORT-P/A"


def test_two_lots_of_one_security_are_summed_not_averaged(db):
    """100 shares at $10 and 200 at $10 is 300 shares at $10, on one mark."""
    balance, value, price, lines = _one(db, """
        SELECT balance, value_usd, price_per_share, lines
          FROM marks m JOIN securities s ON s.security_id = m.security_id
         WHERE m.period_end = DATE '2025-03-31' AND s.class_normalized = 'PFD:A'
    """)
    assert (float(balance), float(value), float(price), lines) == (300.0, 3000.0, 10.0, 2)


def test_lines_that_disagree_on_price_produce_no_price(db):
    """Same title, same category, ten times apart. A blended price belongs to
    neither class, so none is published -- but what the lines said is kept."""
    price, blended, lo, hi, reason = _one(db, """
        SELECT price_per_share, is_blended, price_min, price_max, block_reason
          FROM marks m JOIN securities s ON s.security_id = m.security_id
         WHERE m.is_blended
    """)
    assert price is None
    assert blended is True
    assert (float(lo), float(hi)) == (10.0, 100.0)
    assert "belongs to neither" in reason


def test_a_title_that_is_not_a_share_price_carries_no_price(db):
    price, reason = _one(db, """
        SELECT price_per_share, block_reason
          FROM marks m JOIN securities s ON s.security_id = m.security_id
         WHERE s.price_basis <> 'per_share'
    """)
    assert price is None
    assert "not a share price" in reason


def test_a_tenfold_step_is_suspected_and_blocked(db):
    ratio, suspected, adjudicated, blocked, reason = _one(db, """
        SELECT split_ratio, split_suspected, split_adjudicated, change_blocked, block_reason
          FROM marks WHERE period_end = DATE '2025-09-30'
    """)
    assert float(ratio) == 10.0
    assert suspected is True
    assert adjudicated is False, "nothing may adjudicate itself"
    assert blocked is True
    assert "never enters a change series" in reason


def test_a_repricing_is_not_blocked(db):
    """2.064x is a round. Quarantining it would delete the signal."""
    ratio, suspected, blocked, reason = _one(db, """
        SELECT split_ratio, split_suspected, change_blocked, split_reason
          FROM marks WHERE period_end = DATE '2025-12-31'
    """)
    assert abs(float(ratio) - 2.064) < 0.001
    assert suspected is False
    assert blocked is False
    assert reason.startswith("large move")


def test_the_series_is_flagged_but_only_the_step_is_blocked(db):
    """plan.md blocks the mark, not the security. Blocking the whole series
    would have quarantined 90 further marks in the real panel."""
    flagged, blocked = _one(db, """
        SELECT count(*) FILTER (WHERE series_flagged),
               count(*) FILTER (WHERE change_blocked AND split_suspected)
          FROM marks m JOIN securities s ON s.security_id = m.security_id
         WHERE s.class_normalized = 'PFD:A'
    """)
    assert blocked == 1
    assert flagged > blocked, "the rest of the series should be flagged, not blocked"


def test_re_mark_and_carry_forward_are_different_facts(db):
    """A price that did not move is a carry-forward. A first observation has no
    prior at all. Neither may be recorded as a re-mark."""
    remarked, carried, first = _one(db, """
        SELECT count(*) FILTER (WHERE is_remark),
               count(*) FILTER (WHERE is_remark IS FALSE),
               count(*) FILTER (WHERE is_remark IS NULL AND price_per_share IS NOT NULL)
          FROM marks
    """)
    assert first >= 1, "the first period of a series has no prior"
    assert remarked >= 1
    assert carried >= 1, "10.00 -> 10.00 between March and June is a carry-forward"


def test_every_holding_is_accounted_for(db):
    cov = coverage(db)
    assert cov["reconciles"], cov
    assert cov["superseded_by_amendment"] == 1


def test_rebuilding_is_idempotent(db):
    """The panel is a pure function of the raw layer and the recorded
    decisions. Building twice must not double it."""
    before = _one(db, "SELECT count(*), sum(lines) FROM marks")
    build_securities(db)
    build_marks(db)
    detect(db)
    assert _one(db, "SELECT count(*), sum(lines) FROM marks") == before


def test_the_blend_tolerance_admits_rounding_and_nothing_else():
    """Five real line groups differ only in the fourth decimal (73.5629 against
    73.5630). Those are one security. 1.79x and 10x are not."""
    assert 73.5630 / 73.5629 < 1 + BLEND_TOLERANCE
    assert 41.3443 / 41.3442 < 1 + BLEND_TOLERANCE
    assert 769.43 / 429.99 > 1 + BLEND_TOLERANCE
    assert 735.6295 / 73.5629 > 1 + BLEND_TOLERANCE


# --------------------------------------------------------------------------
# Adjudication
# --------------------------------------------------------------------------


def test_a_split_verdict_must_carry_a_factor(db):
    """Regression, and a real one: the first version of this lived in the CLI,
    accepted `--factor 10`, and never wrote it. A recorded adjudication
    silently carried a null factor, which is the number Week 8 divides by.

    The factor is not the detected ratio. ARK's Perplexity step reads 11.93
    because a 10:1 split and a 16% markdown fell in one period.
    """
    with pytest.raises(ValueError, match="factor"):
        adjudicate(db, company="Acme", verdict="split", reviewer="test-reviewer",
                   rationale="ten for one", factor=None)
    with pytest.raises(ValueError, match="reviewer"):
        adjudicate(db, company="Acme", verdict="split", reviewer="  ",
                   rationale="ten for one", factor=10)
    with pytest.raises(ValueError, match="reason"):
        adjudicate(db, company="Acme", verdict="split", reviewer="test-reviewer",
                   rationale="", factor=10)
    with pytest.raises(ValueError, match="verdict"):
        adjudicate(db, company="Acme", verdict="probably", reviewer="test-reviewer",
                   rationale="unsure", factor=10)


def test_a_confirmed_split_records_its_factor_and_stays_blocked(db):
    result = adjudicate(db, company="Acme", verdict="split", reviewer="test-reviewer",
                        rationale="shares x10, value unchanged", factor=10)
    assert result["marks"] == 1
    factor, adjudicated, blocked, reason, stamp = _one(db, """
        SELECT split_factor, split_adjudicated, change_blocked, block_reason,
               split_adjudication
          FROM marks WHERE split_suspected
    """)
    assert float(factor) == 10.0, "the factor Week 8 divides by must be persisted"
    assert adjudicated is True
    assert blocked is True, "a confirmed split is adjusted in Week 8, not unblocked here"
    assert "awaiting adjustment" in reason
    assert "test-reviewer" in stamp


def test_a_not_a_split_verdict_lifts_the_block(db):
    """The step is a real repricing, so it belongs in the change series."""
    adjudicate(db, company="Acme", verdict="not_a_split", reviewer="test-reviewer",
               rationale="share count constant; only the value moved")
    adjudicated, blocked, reason, flagged = _one(db, """
        SELECT split_adjudicated, change_blocked, block_reason,
               (SELECT count(*) FROM marks WHERE series_flagged)
          FROM marks WHERE split_suspected
    """)
    assert adjudicated is True
    assert blocked is False
    assert reason is None
    assert flagged == 0, "nothing is left unadjudicated, so no series stays flagged"
