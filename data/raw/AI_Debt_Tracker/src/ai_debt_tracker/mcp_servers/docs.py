"""`docs` MCP server (stdio): a filing as addressable sentences, headings and table cells.

A thin binding of `documents.store` to MCP tool names. Started per episode like `edgar_pit`, from the
same environment (`EDGAR_PIT_TARGET`, or `EDGAR_PIT_AS_OF` + `EDGAR_PIT_EXCLUDE`), so it opens only
documents the point-in-time rule allows — every open goes through `PointInTimeEdgar.raw`.

Document keys are `"<cik>/<accession>/<file name>"` (the file name from `edgar_pit.exhibits`).

Run:  python -m ai_debt_tracker.mcp_servers.docs
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..documents import store
from .edgar_pit import _make
from .edgar_pit_core import Refused

STORE = store.DocumentStore(_make())
mcp = FastMCP(
    "docs",
    instructions=("Read SEC filings by id instead of retyping them. sections(key) first, then search(key, query) "
                  "to find where a bond or loan is described, then span(key, id) for the exact text of a sentence "
                  "(s12), table (t3), row (t3.r2) or cell (t3.r2.c1). Cite ids; never copy numbers from memory."),
)


def _open(key: str):
    try:
        return STORE.open(key), None
    except Refused as ex:
        return None, {"refused": True, "reason": str(ex)}
    except ValueError as ex:
        return None, {"error": str(ex)}


@mcp.tool()
def sections(key: str) -> dict:
    """The document's headings with how many sentences and tables each holds."""
    doc, err = _open(key)
    return err or store.sections(doc)


@mcp.tool()
def sentences(key: str, section: str | None = None, offset: int = 0) -> dict:
    """Sentences with ids, optionally of one section (an id from sections()); paged by `next_offset`."""
    doc, err = _open(key)
    return err or store.sentences(doc, section, offset)


@mcp.tool()
def tables(key: str, offset: int = 0) -> dict:
    """Tables with ids and their first rows; span(key, "t3") returns one table whole."""
    doc, err = _open(key)
    return err or store.tables(doc, offset)


@mcp.tool()
def search(key: str, query: str) -> dict:
    """Sentences and table rows ranked by how many query words they contain."""
    doc, err = _open(key)
    return err or store.search(doc, query)


@mcp.tool()
def span(key: str, id: str) -> dict:  # noqa: A002 — the tool's argument is named for what the model passes
    """The exact text behind an id: a sentence, heading, table, row or cell."""
    doc, err = _open(key)
    if err:
        return err
    try:
        return store.span(doc, id)
    except KeyError:
        return {"error": f"no such id in this document: {id}"}


if __name__ == "__main__":
    mcp.run()
