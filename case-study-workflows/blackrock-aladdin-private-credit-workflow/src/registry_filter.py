"""
Plugin Registry Filter (§3.2 of the architecture reference).

Input: parsed intent, full registry of available data-source tools.
Output: a scoped subset of tools relevant to this specific query.

§3.2's [DEV] marker frames "hard-coded rules vs. embedding-based retrieval"
as a decision that scales with registry size — a small deployment hard-codes
it, a larger one needs retrieval over tool descriptions. This reference
implementation has exactly two tools, per §2's component inventory
(private credit adapter, portfolio holdings adapter). Embedding retrieval
over a two-item registry is over-engineering, not a judgment call. Rule-based
scoping is the correct choice here — reconsider only if you extend this repo
with more data sources than these two.
"""

METRICS_NEEDING_FUND_DATA = {
    "money_multiple", "leverage_ratio", "valuation_trend",
    "equity_cushion", "debt_service_coverage",
}
METRICS_NEEDING_PORTFOLIO_DATA = {"position_size"}


class ToolRegistryFilter:
    def filter(self, intent, full_registry: dict) -> dict:
        requested = set(intent.requested_metrics)
        scoped = {}

        if not requested or METRICS_NEEDING_FUND_DATA & requested:
            scoped["private_credit"] = full_registry["private_credit"]
        if METRICS_NEEDING_PORTFOLIO_DATA & requested:
            scoped["portfolio_holdings"] = full_registry["portfolio_holdings"]

        # Unscoped or unrecognized query: retrieve everything rather than
        # nothing, so an ambiguous question still gets an answer.
        return scoped or full_registry
