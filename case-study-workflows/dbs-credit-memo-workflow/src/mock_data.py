"""
WHAT THIS FILE DOES: provides fabricated client/credit records for the reference
implementation to synthesize a draft memo from. Nothing in this file is real DBS
data, a real DBS system, or connected to any real credential or API.

CONFIRMED / CONSTRUCTED: entirely CONSTRUCTED. DBS's public disclosure describes
agents drawing on "raw data" but discloses no data-source list, no schema, and no
specific records. This module exists only so the reference implementation has
something concrete to synthesize from and to deliberately withhold, to exercise
both the happy path and the data-gap path described in Section 4 of the case study.

Series convention: mock data modules never contain real company data of any kind.
"""

from typing import Optional

# CONSTRUCTED. A small, fabricated set of client records. Field names are chosen
# to be the minimum plausible shape a credit-memo synthesis step would need —
# DBS discloses no such schema, so this is illustrative only, not a claim about
# DBS's actual data model.
_MOCK_CLIENT_RECORDS: dict[str, dict] = {
    "CLIENT-001": {
        "client_id": "CLIENT-001",
        "client_name": "Aurora Freight Holdings",
        "existing_facility_type": "trade_finance",
        "existing_facility_limit": 12_000_000,
        "requested_facility_limit": 18_000_000,
        "credit_rating": "BBB+",
        "relationship_tenure_years": 7,
    },
    "CLIENT-002": {
        "client_id": "CLIENT-002",
        "client_name": "Meridian Components Pte Ltd",
        "existing_facility_type": "working_capital",
        "existing_facility_limit": 5_000_000,
        "requested_facility_limit": 7_500_000,
        "credit_rating": "A-",
        "relationship_tenure_years": 3,
    },
    # CLIENT-003 is deliberately incomplete — missing credit_rating — to give the
    # test suite a real, addressable case for the data-gap-flagged path, rather
    # than only ever testing the happy path.
    "CLIENT-003": {
        "client_id": "CLIENT-003",
        "client_name": "Northbridge Industrial Supply",
        "existing_facility_type": "trade_finance",
        "existing_facility_limit": 3_000_000,
        "requested_facility_limit": 4_000_000,
        "credit_rating": None,
        "relationship_tenure_years": 1,
    },
}


def get_client_record(client_id: str) -> Optional[dict]:
    """
    Looks up a fabricated client/credit record by client_id.

    Returns the record dict if found, or None if client_id is not present in the
    mock set. Per Design Decision 6 (Addendum v3), this is the orchestrator's
    responsibility to call — draft_synthesis.py never calls this function itself,
    to keep synthesis pure and directly testable via injected records.

    A None return is a legitimate, expected outcome (an unrecognized client_id),
    not an error condition — callers should treat it as such rather than raising.
    """
    return _MOCK_CLIENT_RECORDS.get(client_id)
