"""Form D lane: the name trap, the date formats, and the valuation ban.

These are offline. The archive is on disk and the identity rules are pure
functions, so nothing here needs the SEC or the database.
"""

import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.ingest import form_d  # noqa: E402
from src.resolve import identity  # noqa: E402


# --------------------------------------------------------------------- dates

@pytest.mark.parametrize("text,expected", [
    ("2015-03-31 17:28:10", date(2015, 3, 31)),   # pre-2020 FILING_DATE
    ("30-SEP-2024", date(2024, 9, 30)),           # post-2020 FILING_DATE
    ("2015-03-31", date(2015, 3, 31)),            # SALE_DATE
    ("12/31/2024", date(2024, 12, 31)),
    ("", None),
    (None, None),
    ("Indefinite", None),
])
def test_every_filed_date_format_in_the_archive_parses(text, expected):
    assert form_d._date(text) == expected


def test_a_timestamped_filing_date_is_not_silently_dropped():
    """The bug this file exists to prevent from coming back.

    The first version tried '%Y-%m-%d' against '2015-03-31 17:28:10', failed,
    and returned None. Eleven years of filings read as undated, which looks
    exactly like an archive that has no dates rather than a parser that
    cannot read them.
    """
    assert form_d._date("2015-03-31 17:28:10") is not None


# ------------------------------------------------------------------- amounts

def test_indefinite_offering_is_null_not_zero():
    """A fund with no cap raised an unknown amount, not nothing."""
    assert form_d._money("Indefinite") is None
    assert form_d.is_indefinite("Indefinite") is True
    assert form_d.is_indefinite("5000000") is False


def test_money_strips_filed_formatting():
    assert form_d._money("$1,250,000") == 1250000.0
    assert form_d._money("") is None


# ---------------------------------------------------------------- the pattern

def test_philanthropic_matches_the_anthropic_pattern():
    """The substring trap, kept as a test because it is not hypothetical.

    'Community Philanthropic Ventures, LLC' is a real Form D filer and
    contains ANTHROPIC. The scan is expected to catch it -- that is what a
    candidate pool is for -- and the identity layer is expected to reject it.
    """
    assert form_d.company_for({"ENTITYNAME": "Community Philanthropic Ventures, LLC"}) \
        == "Anthropic PBC"


def test_previous_names_are_searched():
    """Groq filed as 'Groq, Inc.' and is now 'Groq LLC' on EDGAR."""
    assert form_d.company_for({"ENTITYNAME": "Some Holdco LLC",
                               "EDGAR_PREVIOUSNAME_1": "Groq, Inc."}) == "Groq, Inc."


# ------------------------------------------------------- the pooled-fund flag

def test_pooled_flag_classifies_a_feeder_as_a_vehicle():
    assert form_d._flag("true") is True
    assert form_d._flag("false") is False
    assert form_d._flag("") is None


# ------------------------------------------------------------ identity rules

@pytest.mark.parametrize("filed,canonical", [
    ("Databricks, Inc.", "Databricks, Inc."),
    ("DATABRICKS INC", "Databricks, Inc."),
    ("X.AI CORP.", "X.AI Corp"),
    ("Groq LLC", "Groq, Inc."),
])
def test_legal_form_does_not_change_identity(filed, canonical):
    assert identity.normalize_entity(filed) == identity.normalize_entity(canonical)


@pytest.mark.parametrize("name", [
    "Anthropic Jan 2026 a Series of CGF2021 LLC",
    "HII Cerebras V, a Series of HII Cerebras, LLC",
    "Anduril Investors II LLC",
    "Eagle VP Fund 2 LLC-Series SpaceX",
    "Adit Growth Equity Co-Invest, LLC - Series SpaceX-1",
])
def test_feeder_vehicles_are_recognised_by_shape(name):
    assert identity.looks_like_vehicle(name)


@pytest.mark.parametrize("name", [
    "Databricks, Inc.",
    "SPACE EXPLORATION TECHNOLOGIES CORP",
    "X.AI Holdings Corp.",
])
def test_operating_companies_are_not(name):
    assert not identity.looks_like_vehicle(name)


def test_some_vehicles_are_invisible_to_name_shape():
    """'Gaingels Databricks 2024 LLC' is a feeder and reads like a company.

    It carries no pooling token -- no "series of", no "fund", no "SPV" -- and
    a rule wide enough to catch it on the strength of "LLC" would also catch
    operating companies that file as LLCs. This is the residue the human gate
    exists for, and it is recorded here so the gap is a known one.

    What matters is the direction of the error: the proposal is wrong but
    safe. The filed name does not normalise to "Databricks", so the proposer
    says `not_in_universe` rather than `operating_company`, and a wrong label
    that still refuses to join is not a number on a timeline.
    """
    assert not identity.looks_like_vehicle("Gaingels Databricks 2024 LLC")

    proposal = identity.propose(
        {"cik": "c", "entity_name": "Gaingels Databricks 2024 LLC", "filings": 1,
         "entity_types": "Limited Liability Company", "industry_groups": "Other"},
        "Databricks, Inc.")
    assert proposal["proposed_verdict"] != "operating_company"


def test_the_two_x_ai_filers_are_indistinguishable_by_name():
    """Why `edgar_facts` exists.

    `x.ai, inc.` (CIK 1609052, Delaware, New York, Form Ds 2014-2017) is a
    different company from `X.AI CORP.` (CIK 2002695, Nevada, Palo Alto,
    2023-). They normalise to the same string, so no amount of string work
    separates them and the proposer will suggest `operating_company` for
    both. Only a human looking at the EDGAR record can tell them apart.
    """
    assert identity.normalize_entity("x.ai, inc.") == \
        identity.normalize_entity("X.AI CORP.")

    for name in ("x.ai, inc.", "X.AI CORP."):
        proposal = identity.propose(
            {"cik": "x", "entity_name": name, "filings": 4,
             "entity_types": "Corporation", "industry_groups": "Other Technology"},
            "X.AI Corp")
        assert proposal["proposed_verdict"] == "operating_company"
        assert proposal["is_judgment"] is True


def test_propose_calls_a_feeder_a_vehicle():
    proposal = identity.propose(
        {"cik": "c", "entity_name": "Anthropic Jan 2026 a Series of CGF2021 LLC",
         "filings": 1, "entity_types": "Limited Liability Company",
         "industry_groups": "Pooled Investment Fund"},
        "Anthropic PBC")
    assert proposal["proposed_verdict"] == "vehicle"


def test_propose_rejects_a_colliding_name():
    proposal = identity.propose(
        {"cik": "c", "entity_name": "Siscale AI, Inc.", "filings": 1,
         "entity_types": "Corporation", "industry_groups": "Other Technology"},
        "Scale AI, Inc.")
    assert proposal["proposed_verdict"] == "not_in_universe"


def test_a_proposal_is_never_a_decision():
    """`propose` returns a judgment and writes nothing (P8)."""
    proposal = identity.propose(
        {"cik": "c", "entity_name": "Databricks, Inc.", "filings": 17,
         "entity_types": "Corporation", "industry_groups": "Other Technology"},
        "Databricks, Inc.")
    assert proposal["is_judgment"] is True
    assert "reviewer" not in proposal


# --------------------------------------------------------------- affirm rules

class FakeCursor:
    def __init__(self):
        self.executed = []

    def execute(self, sql, args=None):
        self.executed.append((sql, args))

    def fetchone(self):
        return (1,)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class FakeConn:
    def __init__(self):
        self.cur = FakeCursor()
        self.committed = False

    def cursor(self):
        return self.cur

    def commit(self):
        self.committed = True


def test_affirm_refuses_an_unnamed_reviewer():
    with pytest.raises(ValueError, match="named reviewer"):
        identity.affirm(FakeConn(), cik="1", verdict="vehicle",
                        reviewer="auto", evidence="x")
    with pytest.raises(ValueError, match="named reviewer"):
        identity.affirm(FakeConn(), cik="1", verdict="vehicle",
                        reviewer="   ", evidence="x")


def test_affirm_refuses_evidence_free_decisions():
    with pytest.raises(ValueError, match="written evidence"):
        identity.affirm(FakeConn(), cik="1", verdict="vehicle",
                        reviewer="Om Mali", evidence="")


def test_affirm_refuses_to_link_a_vehicle_to_a_company():
    """The error that would put an SPV's raise on a company's timeline."""
    with pytest.raises(ValueError, match="must not carry a company"):
        identity.affirm(FakeConn(), cik="1", verdict="vehicle",
                        reviewer="Om Mali", evidence="a feeder",
                        company="Anthropic PBC")


def test_affirm_requires_a_company_for_an_operating_verdict():
    with pytest.raises(ValueError, match="must name the company"):
        identity.affirm(FakeConn(), cik="1", verdict="operating_company",
                        reviewer="Om Mali", evidence="it is the company")


def test_affirm_rejects_an_unknown_verdict():
    with pytest.raises(ValueError, match="verdict must be one of"):
        identity.affirm(FakeConn(), cik="1", verdict="probably",
                        reviewer="Om Mali", evidence="x")


# ------------------------------------------------- the valuation prohibition

def test_form_d_stores_no_price_and_no_share_count():
    """plan.md: Form D is "dates and amounts only, never valuation".

    Enforced against the INSERT rather than against prose, because prose does
    not fail. Form D has no share count, so any per-share number derived from
    it would be invented -- and a valuation needs shares outstanding, which
    neither this source nor N-PORT carries.
    """
    banned = ("price", "per_share", "valuation", "shares_outstanding",
              "post_money", "pre_money")
    statement = form_d.UPSERT.lower()
    for token in banned:
        assert token not in statement, f"{token!r} appeared in the Form D insert"


def test_the_form_d_schema_has_no_price_column():
    import re

    schema = (ROOT / "src" / "db" / "schema.sql").read_text(encoding="utf-8")
    start = schema.index("CREATE TABLE IF NOT EXISTS form_d_filings")
    body = schema[start:schema.index(");", start)]
    # Column definitions only. The table's own comment says the words "no
    # price, no share count, no valuation", and a test that reads comments
    # would fail on the sentence promising the thing it is checking.
    columns = " ".join(re.sub(r"--.*$", "", line) for line in body.splitlines())
    for token in ("price", "per_share", "valuation", "shares_outstanding"):
        assert token not in columns.lower(), \
            f"{token!r} appeared in a form_d_filings column"


def test_resolved_join_is_on_cik_not_on_name():
    """The whole point of the week, asserted against the SQL.

    If this join ever moves back to `company_provisional`, 595 pooled
    vehicles re-enter the round timeline.
    """
    sql = " ".join(form_d.resolved.__doc__ or "")
    statement = form_d.resolved.__code__.co_consts
    joined = " ".join(str(c) for c in statement if isinstance(c, str)).lower()
    assert "i.cik = f.cik" in joined
    assert "company_provisional" not in joined
    assert "verdict = 'operating_company'" in joined
    assert sql is not None


def test_the_contiguous_archive_excludes_the_orphan_quarters():
    """2008Q1 and 2012Q1 are published; 2008Q2-2013Q4 are not.

    Including an orphan would make "earliest Form D observed" depend on
    whether a company happened to appear in one isolated quarter.
    """
    assert form_d.QUARTERS[0] == "2014q1"
    assert form_d.QUARTERS[-1] == "2026q1"
    assert "2012q1" not in form_d.QUARTERS
    assert "2008q1" not in form_d.QUARTERS
    assert len(form_d.QUARTERS) == 49
