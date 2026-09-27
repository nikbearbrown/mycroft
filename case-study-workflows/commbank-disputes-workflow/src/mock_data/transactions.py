"""
Mock internal transaction records — CommBank Disputes Workflow (Illustrative).

WHAT THIS FILE DOES: stands in for CBA's core banking system. Verification
queries this module the same way it would query a real transaction API —
by merchant and date — to check whether a claimed transaction actually
exists.

These are entirely fabricated records used to demonstrate the Verification
component's matching logic. They do not represent, resemble, or derive from
any real CBA customer data, transaction, or system. [DEV] Replace this module
with a real data-access layer (API client, DB query) when adapting this
scaffold — see the [DEV] marker in verification.py for the integration point.
"""

from datetime import date

MOCK_TRANSACTIONS = [
    {"merchant": "Amazon", "amount": 340.00, "date": date(2026, 6, 12), "account_id": "acct_001"},
    {"merchant": "Woolworths", "amount": 84.50, "date": date(2026, 6, 14), "account_id": "acct_001"},
    {"merchant": "Netflix", "amount": 22.99, "date": date(2026, 6, 1), "account_id": "acct_002"},
    {"merchant": "Uber", "amount": 615.00, "date": date(2026, 6, 20), "account_id": "acct_003"},
    {"merchant": "Coles", "amount": 600.00, "date": date(2026, 7, 1), "account_id": "acct_004"},
    {"merchant": "Spotify", "amount": 12.99, "date": date(2026, 6, 5), "account_id": "acct_005"},
]


def find_transaction(merchant: str, claimed_date: date):
    """
    CONSTRUCTED matching logic: exact merchant name (case-insensitive) and
    exact date. No source describes CBA's actual matching tolerance (e.g.
    whether a 1-day date drift or fuzzy merchant name is accepted) — this is
    the strictest reasonable interpretation, stated here explicitly rather
    than silently assumed. [DEV] Loosen or tighten this matching tolerance
    per your own risk criteria.
    """
    for txn in MOCK_TRANSACTIONS:
        if txn["merchant"].lower() == merchant.lower() and txn["date"] == claimed_date:
            return txn
    return None
