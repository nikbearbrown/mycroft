"""
Fabricated mock transaction data.

Entirely invented for this scaffold. No real Lloyds customer, account, or
transaction data is used anywhere in this repository. Keyed by ISO date;
each date maps to a list of transactions that occurred that day (a date
can have more than one transaction, same as a real account).
"""

from .models import TransactionRecord

MOCK_TRANSACTIONS = {
    "2026-06-15": [
        TransactionRecord(amount=42.50, date="2026-06-15", merchant="Greggs", description="Card payment"),
    ],
    "2026-06-10": [
        TransactionRecord(amount=89.99, date="2026-06-10", merchant="ASOS", description="Online purchase"),
        TransactionRecord(amount=12.30, date="2026-06-10", merchant="TfL", description="Contactless travel"),
    ],
    "2026-06-01": [
        TransactionRecord(amount=650.00, date="2026-06-01", merchant="Landlord Ltd", description="Standing order — rent"),
    ],
}
