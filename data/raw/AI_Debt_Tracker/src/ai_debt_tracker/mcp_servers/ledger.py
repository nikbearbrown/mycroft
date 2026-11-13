"""`ledger` MCP server (stdio): the tracker's ledger, read-only plus a dry-run `propose`.

A thin binding of `ledger_core.LedgerStore` to MCP tool names (DESIGN.md §6). The agent proposes; code
validates; nothing here writes a ledger.

Run:  python -m ai_debt_tracker.mcp_servers.ledger
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .. import config
from .ledger_core import LedgerStore

STORE = LedgerStore(config.data_dir() / "week5" / "episodes")
mcp = FastMCP(
    "ledger",
    instructions=("The tracker's bond and loan ledger per company. get(cik, as_of) for the closing ledger of the "
                  "latest quarter ended on or before as_of; propose(cik, as_of, event) to check a change before it is "
                  "made (dry run: nothing is written); open_questions(cik) for what the self-checks could not settle."),
)


@mcp.tool()
def get(cik: int, as_of: str, offset: int = 0) -> dict:
    """The closing ledger of the latest quarter ended on or before `as_of` (YYYY-MM-DD), a summary first."""
    return STORE.get(cik, as_of, offset)


@mcp.tool()
def propose(cik: int, as_of: str, event: dict) -> dict:
    """Validate one debt event against the ledger: the diff it would make and the self-checks. Not applied."""
    return STORE.propose(cik, as_of, event)


@mcp.tool()
def open_questions(cik: int) -> dict:
    """Repayments of unknown bonds and new bonds without a maturity, left for the investigators."""
    return STORE.open_questions(cik)


if __name__ == "__main__":
    mcp.run()
