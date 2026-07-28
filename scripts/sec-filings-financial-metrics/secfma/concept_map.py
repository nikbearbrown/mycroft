"""Canonical financial metric -> ordered candidate XBRL tags.

This module is the heart of the project. Companies tag the *same* economic
concept with *different* us-gaap elements (e.g. "Net Sales" vs "Revenue from
Contracts with Customers"), and some introduce their own custom extensions.
We resolve each canonical metric by trying candidate tags in priority order
and *recording which one matched*, so every value stays auditable.

period_type:
  * "duration" -> income-statement / cash-flow items (have start & end dates)
  * "instant"  -> balance-sheet items (a single point-in-time `end` date)
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricSpec:
    name: str
    period_type: str             # "duration" | "instant"
    unit: str                    # expected unit key in the facts, e.g. "USD"
    candidates: tuple[str, ...]  # us-gaap tags, most-preferred first


# Priority order matters: prefer newer ASC 606 revenue tags over legacy ones.
CANONICAL_METRICS: tuple[MetricSpec, ...] = (
    MetricSpec("revenue", "duration", "USD", (
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
    )),
    MetricSpec("cost_of_revenue", "duration", "USD", (
        "CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold",
    )),
    MetricSpec("gross_profit", "duration", "USD", ("GrossProfit",)),
    MetricSpec("operating_income", "duration", "USD", ("OperatingIncomeLoss",)),
    MetricSpec("net_income", "duration", "USD", ("NetIncomeLoss", "ProfitLoss")),
    MetricSpec("research_and_development", "duration", "USD", (
        "ResearchAndDevelopmentExpense",
    )),
    MetricSpec("operating_cash_flow", "duration", "USD", (
        "NetCashProvidedByUsedInOperatingActivities",
        "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
    )),
    MetricSpec("total_assets", "instant", "USD", ("Assets",)),
    MetricSpec("total_liabilities", "instant", "USD", ("Liabilities",)),
    MetricSpec("stockholders_equity", "instant", "USD", (
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    )),
    MetricSpec("current_assets", "instant", "USD", ("AssetsCurrent",)),
    MetricSpec("current_liabilities", "instant", "USD", ("LiabilitiesCurrent",)),
    MetricSpec("cash_and_equivalents", "instant", "USD", (
        "CashAndCashEquivalentsAtCarryingValue",
    )),
)
