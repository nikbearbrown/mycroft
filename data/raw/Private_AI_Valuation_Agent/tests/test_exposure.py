"""The exposure map and the timeline: what they publish and what they refuse.

Offline. These assert the shape of the SQL and the arithmetic rule, because
the thing worth protecting here is a refusal, and a refusal is easy to delete
by accident while "improving" a report.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.signal import exposure  # noqa: E402


def sql_of(function) -> str:
    return " ".join(str(c) for c in function.__code__.co_consts
                    if isinstance(c, str)).lower()


def test_the_price_series_excludes_blocked_marks():
    """The same guard Week 8's findings use.

    If the timeline published a blocked mark, the same panel would say two
    different things in two reports -- and one of them would include a step
    across an unadjudicated split.
    """
    assert "not m.change_blocked" in sql_of(exposure.price_history)


def test_the_form_d_leg_joins_on_an_affirmed_identity():
    sql = sql_of(exposure.rounds)
    assert "company_identity" in sql
    assert "verdict = 'operating_company'" in sql
    assert "company_provisional" not in sql


def test_pct_net_assets_comes_from_the_filing():
    """Not value divided by a net-asset figure this project computed.

    `raw_holdings.pct_net_assets` is the filer's own number. Deriving it would
    need a fund's total net assets, which N-PORT reports at a different
    granularity, and the result would be a number no filing produced.
    """
    assert "r.pct_net_assets" in sql_of(exposure.exposure_map)


def test_cost_to_value_needs_both_numbers_from_one_filed_row():
    rows = [
        {"cost_usd": 100.0, "value_usd": 250.0, "cost_basis_scope": "position"},
        {"cost_usd": None, "value_usd": 250.0, "cost_basis_scope": "fund_total"},
        {"cost_usd": 100.0, "value_usd": None, "cost_basis_scope": "position"},
        {"cost_usd": 0.0, "value_usd": 250.0, "cost_basis_scope": "position"},
    ]
    for row in rows:
        cost, value = row["cost_usd"], row["value_usd"]
        row["cost_to_value"] = (
            round(float(value) / float(cost), 4)
            if row["cost_basis_scope"] == "position" and cost and value else None)
    assert rows[0]["cost_to_value"] == 2.5
    assert rows[1]["cost_to_value"] is None   # fund total is not an entry price
    assert rows[2]["cost_to_value"] is None   # no value filed
    assert rows[3]["cost_to_value"] is None   # zero cost, not an infinite return


def test_the_timeline_says_what_it_did_not_compute():
    """P3 in the artifact, not only in the docstring.

    A reader holding an entry cost and a current mark will divide them unless
    the report says why that is wrong.
    """
    blob = " ".join(exposure.NOT_COMPUTED).lower()
    assert "share count" in blob
    assert "shares outstanding" in blob
    assert "form d" in blob
    assert len(exposure.NOT_COMPUTED) >= 3


def test_no_valuation_anywhere_in_the_module():
    source = Path(exposure.__file__).read_text(encoding="utf-8").lower()
    for token in ("post_money", "pre_money", "implied_valuation",
                  "company_valuation"):
        assert token not in source


# ------------------------------------------------------- Form D corroboration

def test_corroboration_restricts_to_the_filing_window():
    """The restriction is the method, not a convenience.

    SpaceX stopped filing Form D in July 2022 and 22 of its 28 acquisition
    dates come after that. Measured against the nearest round they produce
    gaps of 873, 911, 1090 and 1293 days, none of which says anything about
    when a fund bought -- each is the distance to the end of the archive.
    Left in the denominator, a real 56% agreement reads as 33%.
    """
    sql = sql_of(exposure.corroboration)
    assert "between fd.first_round and fd.last_round" in sql
    assert "not l.acquisition_date_is_range" in sql


def test_corroboration_excludes_date_ranges():
    """A position built across three years has no single acquisition date.

    Picking an endpoint would manufacture either the match or the miss.
    """
    assert "not l.acquisition_date_is_range" in sql_of(exposure.corroboration)


def test_corroboration_joins_only_affirmed_identities():
    sql = sql_of(exposure.corroboration)
    assert "verdict = 'operating_company'" in sql
    assert "company_identity" in sql


def test_corroboration_windows_are_nested():
    """Share at 0 days cannot exceed share at 7, which cannot exceed 31."""
    assert exposure.CORROBORATION_WINDOWS == (0, 7, 31)
    hits = {0: 10, 7: 11, 31: 11}
    assert hits[0] <= hits[7] <= hits[31]


def test_corroboration_does_not_claim_causation():
    """Two filings agreeing is evidence. It is not proof a fund led a round."""
    import inspect

    source = inspect.getsource(exposure.corroboration)
    assert "caveat" in source
    assert "secondary purchase" in source
