"""Week 8: the four measurements.

The pure tests hold the price-level clustering to account, which is the one
piece of judgment in this module that is not a database query. The rest build a
synthetic panel in a throwaway database, engineered so each measurement has a
known right answer, and skip loudly when no Postgres answers.
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

from src.signal.findings import (  # noqa: E402
    LEVEL_REL,
    MIN_HOLDERS,
    OUTLIER_FACTOR,
    WINDOW_DAYS,
    _levels,
    dispersion,
    guards,
    propagation,
    remark_frequency,
)

SCHEMA = ROOT / "src" / "db" / "schema.sql"
CANDIDATE_URLS = [
    os.getenv("REVIEW_TEST_DB_URL"),
    "postgresql://postgres:postgres@127.0.0.1:55432/postgres",
    "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
]


# --------------------------------------------------------------------------
# Price-level clustering
# --------------------------------------------------------------------------


def test_rounding_differences_are_one_level():
    """Ten manager families report Anthropic at 259.14 and split into 259.1364
    and 259.1400 at four decimals. Fidelity reports 261.5705 for the same
    round. All of those are one price level."""
    levels = _levels([259.1364, 259.1400, 259.0082, 261.5705], LEVEL_REL)
    assert len(levels) == 1


def test_a_round_change_is_a_different_level():
    """203.36 against 259.14 is 27% and a different round."""
    levels = _levels([140.9676, 203.36, 259.1364], LEVEL_REL)
    assert len(levels) == 3


def test_the_anthropic_propagation_window_decomposes():
    """The real window: five managers at 141, one at 203, four near 259. The
    measurement has to see more than one level here, or an 85% spread gets
    reported as manager disagreement."""
    prices = [140.9676, 141.5965, 203.36, 243.40, 250.91, 254.43, 259.0082,
              259.1364, 261.5705]
    levels = _levels(prices, LEVEL_REL)
    assert len(levels) > 1
    assert levels[0][0] == pytest.approx(140.9676)


def test_clustering_is_single_linkage_and_that_is_deliberate():
    """A chain of prices each within the tolerance of the last is one level,
    even though the ends are further apart than the tolerance. That is what
    keeps 259.0082 and 261.5705 together via the 259.14 consensus."""
    chained = _levels([100.0, 101.5, 103.0, 104.5], LEVEL_REL)
    assert len(chained) == 1
    assert (104.5 / 100.0 - 1) > LEVEL_REL, "the ends exceed the tolerance"


def test_clustering_handles_the_degenerate_cases():
    assert _levels([], LEVEL_REL) == []
    assert _levels([42.0], LEVEL_REL) == [[42.0]]


def test_the_thresholds_are_what_the_report_claims():
    assert MIN_HOLDERS == 3
    assert WINDOW_DAYS == 31, "31 days matches plan.md's 4/30-to-5/31 example"
    assert OUTLIER_FACTOR == 5.0
    assert LEVEL_REL == 0.02


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
        pytest.skip("no Postgres reachable; set REVIEW_TEST_DB_URL to run these")
    name = f"findings_test_{uuid.uuid4().hex[:8]}"
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


# Three managers on one company. Alpha and Beta move to 200 on 2025-03-31;
# Gamma does not reach it until 2025-06-30, which is a 91-day propagation and
# a two-level same-date window on 2025-03-31.
PANEL = [
    # manager, period_end, price, blocked, remark
    ("Alpha", "2024-12-31", 100.0, False, None),
    ("Beta",  "2024-12-31", 100.0, False, None),
    ("Gamma", "2024-12-31", 100.0, False, None),
    ("Alpha", "2025-03-31", 200.0, False, True),
    ("Beta",  "2025-03-31", 200.0, False, True),
    ("Gamma", "2025-03-31", 100.0, False, False),   # carried forward
    ("Alpha", "2025-06-30", 200.0, False, False),   # carried forward
    ("Beta",  "2025-06-30", 200.0, False, False),   # carried forward
    ("Gamma", "2025-06-30", 200.0, False, True),    # catches up
    # a blocked mark that must not enter any measurement
    ("Delta", "2025-06-30", 9999.0, True, True),
]


def _build(conn):
    with conn.cursor() as cur:
        cur.execute(SCHEMA.read_text(encoding="utf-8"))
        cur.execute("INSERT INTO companies (canonical_name, status, universe_version) "
                    "VALUES ('Acme AI, Inc.', 'full', 1) RETURNING company_id")
        company_id = cur.fetchone()[0]
        cur.execute("INSERT INTO securities (company_id, share_class_raw, "
                    "class_normalized, price_basis) VALUES (%s, 'ACME COMMON', "
                    "'COM:UNSPECIFIED', 'per_share') RETURNING security_id",
                    (company_id,))
        security_id = cur.fetchone()[0]
        cur.execute("INSERT INTO runs (periods_ingested, complete) "
                    "VALUES (ARRAY['t'], true) RETURNING run_id")
        run_id = cur.fetchone()[0]

        funds, previous = {}, {}
        for i, (manager, period, price, blocked, remark) in enumerate(PANEL):
            if manager not in funds:
                cur.execute("INSERT INTO funds (cik, series_id, fund_name, family) "
                            "VALUES (%s, 'S1', %s, %s) RETURNING fund_id",
                            (f"000000000{len(funds)}", manager, manager))
                funds[manager] = cur.fetchone()[0]
            cur.execute("INSERT INTO filings (fund_id, accession, form_type, period_end) "
                        "VALUES (%s, %s, 'NPORT-P', %s) RETURNING filing_id",
                        (funds[manager], f"acc-{i}", period))
            filing_id = cur.fetchone()[0]
            # prior_price_per_share is what the real detector writes, and the
            # sensitivity measurement reads it. Leaving it null made the first
            # version of this fixture exercise none of that path.
            cur.execute("""
                INSERT INTO marks (security_id, company_id, fund_id, filing_id,
                                   period_end, balance, value_usd, price_per_share,
                                   prior_price_per_share, is_remark, change_blocked,
                                   run_id, lines)
                VALUES (%s, %s, %s, %s, %s, 100, %s, %s, %s, %s, %s, %s, 1)
            """, (security_id, company_id, funds[manager], filing_id, period,
                  price * 100, price, previous.get(manager), remark, blocked, run_id))
            previous[manager] = price
    conn.commit()


@pytest.fixture(scope="module")
def db(db_url):
    conn = psycopg2.connect(db_url)
    _build(conn)
    yield conn
    conn.close()


# --------------------------------------------------------------------------
# Database tests
# --------------------------------------------------------------------------


def test_a_blocked_mark_enters_no_measurement(db):
    """plan.md's invariant, enforced in one place so no measurement can skip it."""
    assert guards(db)["change_blocked"] == 1
    overall = remark_frequency(db)["overall"]
    assert overall["steps"] == 6, "3 managers x 2 steps; the blocked mark is excluded"
    for window in dispersion(db, window_days=0)["windows"]:
        assert float(window["price_max"]) < 9999


def test_carry_forward_and_re_mark_are_counted_apart(db):
    overall = remark_frequency(db)["overall"]
    assert overall["moved"] == 3
    assert overall["unchanged"] == 3
    assert overall["first_observation"] == 3
    assert overall["share_unchanged"] == pytest.approx(0.5)


def test_same_date_dispersion_sees_the_laggard(db):
    """On 2025-03-31 two managers are at 200 and one is still at 100. That is a
    100% spread and two price levels -- and the two levels are the point: it is
    a round in flight, not a disagreement about value."""
    windows = dispersion(db, window_days=0)["windows"]
    march = [w for w in windows if w["anchor"] == "2025-03-31"]
    assert march, "the three-manager same-date group should be found"
    window = march[0]
    assert window["managers"] == 3
    assert window["spread"] == pytest.approx(1.0)
    assert window["levels"] == 2
    assert window["state"] == "transition"
    assert "Gamma" in window["laggards"]
    assert "Alpha" in window["movers"] and "Beta" in window["movers"]


def test_a_window_where_everyone_agrees_is_steady(db):
    windows = dispersion(db, window_days=0)["windows"]
    december = [w for w in windows if w["anchor"] == "2024-12-31"][0]
    assert december["state"] == "steady"
    assert december["levels"] == 1
    assert december["spread"] == pytest.approx(0.0)


def test_propagation_measures_the_lag_to_the_new_level(db):
    """Alpha and Beta reach 200 on 2025-03-31, Gamma on 2025-06-30. First to
    half is 0 days -- two of three is already half -- and first to last is 91."""
    events = propagation(db)["events"]
    level = [e for e in events if abs(float(e["price"]) - 200.0) < 0.01]
    assert level, "the 200.00 level should be an event"
    event = level[0]
    assert event["managers"] == 3
    assert event["lag_to_half_days"] == 0
    assert event["lag_to_all_days"] == 91


def test_a_level_below_the_holder_threshold_is_not_an_event(db):
    """Two adopters is not propagation. MIN_HOLDERS is what keeps a pair of
    funds from becoming a finding."""
    events = propagation(db, min_holders=4)["events"]
    assert events == []


def test_the_guards_report_the_inert_one_honestly(db):
    """There are no incomplete runs in the fixture either, so the guard removes
    nothing -- and the report has to be able to say so."""
    g = guards(db)
    assert g["incomplete_runs"] == 0
    assert g["on_incomplete_runs"] == 0
