"""The restricted-securities footnote parser, against real filed HTML.

Every fixture in `tests/fixtures/ncsr_footnotes_v1.json` was lifted verbatim
out of a filing on EDGAR. Nothing here is HTML I wrote, because a parser whose
only test is markup written by its own author proves that the author is
self-consistent, not that the parser survives what filing agents emit.

Five layouts, five filers:

    baron      table, Value only, cost given once per fund
    fidelity   table, Acquisition Cost per position
    lincoln    table, Cost then Value
    neuberger  table, Cost, Value and percentage of net assets
    blackrock  NO TABLE -- an "(Acquired ..., cost $...)" parenthetical
               inside the Schedule of Investments line item
"""

import json
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.ingest import ncsr  # noqa: E402

FIXTURE = json.loads(
    (ROOT / "tests" / "fixtures" / "ncsr_footnotes_v1.json").read_text("utf-8"))
FILERS = FIXTURE["filers"]

TABLE_FILERS = ("baron", "fidelity", "lincoln", "neuberger")


def lots_for(key: str) -> list[dict]:
    filer = FILERS[key]
    document = "".join(filer.get("tables") or filer.get("excerpts") or [])
    return ncsr.parse_document(document)


# ------------------------------------------------------------- every layout

@pytest.mark.parametrize("key", TABLE_FILERS)
def test_each_table_layout_yields_universe_lots(key):
    lots = lots_for(key)
    assert lots, f"{key}: parsed nothing out of its own filed table"
    for lot in lots:
        assert lot["company_provisional"]
        assert lot["acquisition_date_first"] is not None


@pytest.mark.parametrize("key", TABLE_FILERS)
def test_no_layout_needs_a_filer_specific_branch(key):
    """Columns are found by reading the header, not by knowing the filer.

    The point of the design: a sixth filer with a labelled header works
    without a code change. If this ever needs a per-filer switch, the
    abstraction has failed.
    """
    tables = FILERS[key]["tables"]
    headers = []
    for table in tables:
        for match in ncsr._TABLE.finditer(table):
            header, _, _ = ncsr.read_table(match.group(0))
            columns = ncsr.map_columns(header)
            if columns:
                headers.append((header, columns))
    assert headers, f"{key}: no header named an acquisition-date column"
    for _, columns in headers:
        assert "date" in columns


# ----------------------------------------------------------- the date range

def test_a_date_range_keeps_both_ends():
    """Baron: "11/15/2017-8/4/2020" is a position built over three years."""
    ranges = [l for l in lots_for("baron") if l["acquisition_date_is_range"]]
    assert ranges, "baron's fixture should contain at least one range"
    lot = next(l for l in ranges if l["acquisition_date_raw"].startswith("11/15/2017"))
    assert lot["acquisition_date_first"] == date(2017, 11, 15)
    assert lot["acquisition_date_last"] == date(2020, 8, 4)


def test_a_single_date_is_not_reported_as_a_range():
    singles = [l for l in lots_for("baron") if not l["acquisition_date_is_range"]]
    assert singles
    for lot in singles:
        assert lot["acquisition_date_first"] == lot["acquisition_date_last"]


# ------------------------------------------------------------ the cost scope

def test_baron_cost_is_recorded_as_a_fund_total_not_as_absent():
    """Baron discloses cost, just not per position.

    "Total Restricted Securities: $3,274,271,150 (Cost $253,013,093)". Calling
    that `absent` would say the filer withheld something it did not, and
    putting 253,013,093 in `cost_usd` would read as the entry price of one
    SpaceX position.
    """
    lots = lots_for("baron")
    assert all(l["cost_basis_scope"] == "fund_total" for l in lots)
    assert all(l["cost_usd"] is None for l in lots)


@pytest.mark.parametrize("key", ("fidelity", "lincoln", "neuberger"))
def test_position_level_cost_is_recorded_as_such(key):
    lots = lots_for(key)
    assert any(l["cost_basis_scope"] == "position" for l in lots)
    for lot in lots:
        if lot["cost_basis_scope"] == "position":
            assert lot["cost_usd"] is not None


def test_cost_and_value_are_assigned_by_header_order_not_by_size():
    """Lincoln's Russian book is carried at 0 against a cost of $16.3m.

    An earlier design took "the larger number is the value", which is wrong
    for every position a fund is underwater on. Here Databricks is up, so the
    ordering is checked against the header instead: Cost comes before Value.
    """
    lots = {l["issuer_name_raw"]: l for l in lots_for("lincoln")}
    lot = lots["Databricks, Inc. Series F"]
    assert lot["cost_usd"] == 885940.0
    assert lot["value_usd"] == 13784042.0
    assert lot["cost_usd"] < lot["value_usd"]

    header = ["Investment", "Date of Acquisition", "Cost", "Value"]
    columns = ncsr.map_columns(header)
    assert columns["cost"] < columns["value"]


def test_acquisition_cost_header_is_not_read_as_a_value_column():
    """Fidelity's only money column is called "Acquisition Cost ($)"."""
    columns = ncsr.map_columns(["Security", "Acquisition Date",
                                "Acquisition Cost ($)"])
    assert columns["cost"] == 2
    assert "value" not in columns


def test_value_as_of_a_date_is_not_read_as_a_cost_column():
    columns = ncsr.map_columns([
        "Restricted Security", "Acquisition Date(s)", "Acquisition Cost",
        "Value as of 2/28/2026",
        "Fair Value Percentage of Net Assets as of 2/28/2026"])
    assert columns["cost"] == 2
    assert columns["value"] == 3
    assert columns["pct"] == 4


# ------------------------------------------------------------- the fund name

def test_a_fund_name_is_taken_only_from_the_table_structure():
    """Baron prints it above the table, so it is recovered."""
    names = {l["fund_name"] for l in lots_for("baron")}
    assert "Baron Partners Fund" in names


def test_a_fund_name_is_never_guessed_from_surrounding_prose():
    """The regression this rule exists for.

    Fidelity's note is preceded by "each Fidelity Central Fund's financial
    statements ... are available on the SEC's website". An earlier version
    searched that prose and returned "Fidelity Central Fund" -- a real but
    unrelated vehicle -- for every Anduril and Anthropic lot in the filing.
    NULL is the correct answer here.
    """
    for lot in lots_for("fidelity"):
        assert lot["fund_name"] != "Fidelity Central Fund"
        assert lot["fund_name"] is None


def test_a_heading_that_names_no_fund_is_not_a_fund_name():
    assert ncsr.fund_title([["Restricted Securities"]]) is None
    assert ncsr.fund_title([["Notes to Financial Statements"]]) is None
    assert ncsr.fund_title([["Baron Focused Growth Fund"]]) == \
        "Baron Focused Growth Fund"


# -------------------------------------------------------- the inline layout

def test_blackrock_has_no_table_and_is_still_parsed():
    """The fifth layout: Reg S-X 12-12 satisfied inside a line item.

    BlackRock is one of the largest holders in this universe and every one of
    its filings returned zero lots until this was supported.
    """
    filer = FILERS["blackrock"]
    lots = ncsr.parse_inline("".join(filer["excerpts"]))
    by_name = {l["issuer_name_raw"]: l for l in lots}
    assert "Databricks, Inc., Series F" in by_name
    lot = by_name["Databricks, Inc., Series F"]
    assert lot["acquisition_date_first"] == date(2019, 10, 22)
    assert lot["cost_usd"] == 3030010.0
    assert lot["cost_basis_scope"] == "position"
    assert lot["company_provisional"] == "Databricks, Inc."


def test_the_inline_parser_survives_raw_filing_html():
    """Including the filing agent's zero-width row separators.

    Left in, U+200C welds the previous line's value onto the next security's
    name and "Databricks, Inc., Series F" arrives as
    "40,213,500‌Databricks, Inc., Series F".
    """
    lots = ncsr.parse_inline(FILERS["blackrock"]["raw_html"])
    assert lots
    for lot in lots:
        assert "‌" not in lot["issuer_name_raw"]
        assert not lot["issuer_name_raw"][0].isdigit()


def test_an_inline_name_keeps_its_periods():
    """The bug that made every inline name useless.

    Cutting the name at the previous full stop turns
    "Databricks, Inc., Series F" into "Series F", and every name in this
    universe contains a period.
    """
    text = ("CoreWeave, Inc. (d)(o) 2,520,000 2,494,800 "
            "Databricks, Inc., Series F, (Acquired 10/22/19, cost $3,030,010) "
            "(d)(g)(j) 211,650 40,213,500")
    lots = ncsr.parse_inline(text)
    assert [l["issuer_name_raw"] for l in lots] == ["Databricks, Inc., Series F"]


def test_a_repeated_page_heading_is_trimmed_off_the_name():
    assert ncsr._trim_section_header(
        "Security Shares Shares Value United States (continued) "
        "Fanatics Holdings, Inc. , Class A") == "Fanatics Holdings, Inc. , Class A"
    assert ncsr._trim_section_header("Databricks, Inc., Series F") == \
        "Databricks, Inc., Series F"


# ------------------------------------------------------------- housekeeping

def test_totals_rows_are_not_lots():
    for key in TABLE_FILERS:
        for lot in lots_for(key):
            assert not lot["issuer_name_raw"].lower().startswith("total")


def test_a_document_with_no_footnote_is_reported_as_such():
    assert ncsr.footnote_present("<html><body>nothing here</body></html>") is False
    assert ncsr.footnote_present("6. RESTRICTED SECURITIES At December 31") is True
    assert ncsr.footnote_present("(Acquired 10/22/19, cost $3,030,010)") is True


def test_slicing_never_cuts_a_table_in_half():
    """Overlapping windows are merged, so a table is whole or absent."""
    document = FILERS["neuberger"]["tables"][0]
    regions = ncsr.slice_regions(document)
    assert sum(len(ncsr._TABLE.findall(r)) for r in regions) >= 1
    assert len(ncsr.parse_document(document)) > 0


def test_the_loader_records_a_filing_even_when_it_yields_nothing():
    """"Found nothing" and "never looked" are different facts.

    Asserted against the SQL because it is a property of the write path, not
    of the parser: `ncsr_filings` gets a row before any lot does.
    """
    statement = ncsr.RECORD_FILING.lower()
    assert "footnote_found" in statement
    assert "lots_parsed" in statement
    assert "parse_note" in statement


def test_the_lot_table_stores_no_price_per_share():
    """N-CSR gives cost and value for a position, never a per-share price.

    Dividing a position cost by an N-PORT share count would assume the share
    count never changed -- and Week 7 confirmed seven splits.
    """
    statement = ncsr.RECORD_LOT.lower()
    for token in ("price_per_share", "valuation", "shares_outstanding"):
        assert token not in statement
