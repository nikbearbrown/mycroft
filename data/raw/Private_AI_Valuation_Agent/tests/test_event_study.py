"""The Cerebras event study harness, tested before its data exists.

The study cannot run today: the Level 1 marks it needs have period ends after
the bulk archive's last one. That is exactly why these tests matter. A harness
that will not be exercised for months has to be shown to work now, on injected
data, or the day the archive catches up nobody will know whether the silence
means "no crossing" or "the code is broken".

So the fixture builds a company with a Level 3 run-up and then injects a Level
1 observation, and the tests assert the arithmetic the report will print.
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

from src.signal.event_study import boundary, public_observations, ready, study  # noqa: E402

SCHEMA = ROOT / "src" / "db" / "schema.sql"
CANDIDATE_URLS = [
    os.getenv("REVIEW_TEST_DB_URL"),
    "postgresql://postgres:postgres@127.0.0.1:55432/postgres",
    "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
]

COMPANY = "Cerebras Systems Inc."

# The real Level 3 run-up, abridged: the last three observations the panel has.
PRIVATE = [("2025-12-31", 36.23), ("2026-03-31", 89.02), ("2026-04-30", 100.26)]


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
    name = f"event_test_{uuid.uuid4().hex[:8]}"
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


@pytest.fixture(scope="module")
def db(db_url):
    conn = psycopg2.connect(db_url)
    with conn.cursor() as cur:
        cur.execute(SCHEMA.read_text(encoding="utf-8"))
        cur.execute("INSERT INTO companies (canonical_name, status, universe_version) "
                    "VALUES (%s, 'full', 1) RETURNING company_id", (COMPANY,))
        company_id = cur.fetchone()[0]
        cur.execute("INSERT INTO securities (company_id, share_class_raw, "
                    "class_normalized, price_basis) VALUES (%s, 'SER G PC', 'PFD:G', "
                    "'per_share') RETURNING security_id", (company_id,))
        security_id = cur.fetchone()[0]
        cur.execute("INSERT INTO funds (cik, series_id, fund_name, family) "
                    "VALUES ('0000000001', 'S1', 'Test', 'Fidelity') RETURNING fund_id")
        fund_id = cur.fetchone()[0]
        for i, (period, price) in enumerate(PRIVATE):
            cur.execute("INSERT INTO filings (fund_id, accession, form_type, period_end) "
                        "VALUES (%s, %s, 'NPORT-P', %s) RETURNING filing_id",
                        (fund_id, f"acc-{i}", period))
            filing_id = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO marks (security_id, company_id, fund_id, filing_id,
                                   period_end, balance, value_usd, price_per_share, lines)
                VALUES (%s, %s, %s, %s, %s, 100, %s, %s, 1)
            """, (security_id, company_id, fund_id, filing_id, period,
                  price * 100, price))
    conn.commit()
    yield conn
    conn.close()


def _inject_level_1(conn, period="29-MAY-2026", price=236.99, level="1"):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO public_observations
                (source_quarter, accession, period_end, registrant, issuer_name,
                 title_of_issue, fair_value_level, balance, value_usd,
                 price_per_share, company_provisional)
            VALUES ('2026q3', %s, %s, 'BlackRock', 'CEREBRAS SYSTEMS INC',
                    'CEREBRAS SYSTEMS INC COMMON', %s, 1000, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (f"acc-public-{period}-{level}", period, level, price * 1000, price,
              COMPANY))
    conn.commit()


# --------------------------------------------------------------------------
# Before the archive catches up
# --------------------------------------------------------------------------


def test_the_study_reports_why_it_cannot_run(db):
    """Silence is not an answer. With no Level 1 rows the study has to say what
    is missing and what would unblock it."""
    result = study(db, COMPANY)
    assert result["runnable"] is False
    assert "Level 1" in result["reason"]
    assert "2026q3" in result["unblocks_when"]
    assert result["discounts"] == []


def test_the_private_leg_is_reported_even_when_the_study_cannot_run(db):
    """The measurable half is still worth having."""
    result = study(db, COMPANY)
    assert len(result["private_leg"]) == len(PRIVATE)
    assert float(result["private_first"]["price_min"]) == pytest.approx(36.23)
    assert float(result["private_last"]["price_max"]) == pytest.approx(100.26)
    assert result["private_return"] == pytest.approx(100.26 / 36.23 - 1, abs=1e-4)


def test_no_crossing_is_detected_before_one_exists(db):
    edge = boundary(db, COMPANY)
    assert edge["crossed"] is False
    assert edge["first_level_1_period"] is None
    assert edge["last_level_3_period"] == "2026-04-30"


def test_nothing_is_runnable_yet(db):
    assert ready(db)["any_runnable"] is False


# --------------------------------------------------------------------------
# After it does
# --------------------------------------------------------------------------


def test_the_study_runs_once_a_level_1_mark_arrives(db):
    """The harness proven on injected data, because the real data is months
    away and a harness nobody has run is not a harness."""
    _inject_level_1(db)

    edge = boundary(db, COMPANY)
    assert edge["crossed"] is True
    assert edge["first_level_1_period"] == "2026-05-29"
    assert edge["last_level_3_period"] == "2026-04-30"
    assert edge["gap_days"] == 29

    result = study(db, COMPANY)
    assert result["runnable"] is True
    assert result["reference"]["price"] == pytest.approx(236.99)

    # The discount each private mark carried against the first quoted price.
    last = result["discounts"][-1]
    assert last["period_end"] == "2026-04-30"
    assert last["level_3_price"] == pytest.approx(100.26)
    assert last["discount"] == pytest.approx(100.26 / 236.99 - 1, abs=1e-4)
    assert last["days_before_first_level_1"] == 29

    first = result["discounts"][0]
    assert first["discount"] < last["discount"], "the gap should close as the IPO nears"
    assert result["closing"]["narrowed_by"] == pytest.approx(
        last["discount"] - first["discount"], abs=1e-4)


def test_the_reference_is_the_earliest_level_1_not_the_cheapest(db):
    """A later, lower quote must not become the benchmark. The market moves
    after an IPO for reasons that have nothing to do with the private marks."""
    _inject_level_1(db, period="30-JUN-2026", price=150.00)
    result = study(db, COMPANY)
    assert result["reference"]["period_end"] == "2026-05-29"
    assert result["reference"]["price"] == pytest.approx(236.99)


def test_a_level_2_observation_does_not_count_as_a_crossing(db):
    """Level 2 is an observable input, not a quoted price. Only Level 1 is the
    market."""
    _inject_level_1(db, period="31-JUL-2026", price=999.0, level="2")
    assert boundary(db, COMPANY)["first_level_1_period"] == "2026-05-29"
    levels = {r["level"] for r in public_observations(db, COMPANY)}
    assert "2" in levels, "the Level 2 row is still captured"
    assert study(db, COMPANY)["reference"]["price"] == pytest.approx(236.99)


def test_the_caveats_travel_with_the_result(db):
    """A discount against a mark on a different date needs saying so, every
    time, not once in a doc nobody opens beside the number."""
    result = study(db, COMPANY)
    joined = " ".join(result["caveats"]).lower()
    assert "period end" in joined
    assert "lock-up" in joined
    assert "offer price" in joined
