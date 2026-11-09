"""The MCP server: the resolved dataset, queryable from Claude Desktop or Code.

`plan.md` week 10: "A small FastMCP server over stdio, exposing the resolved
dataset so it is queryable from Claude Desktop or Claude Code and reusable by
other Mycroft agents without importing this project's code."

    python -m src.mcp.server            # stdio, what a client launches
    python -m src.mcp.server --selftest # call every tool once and report

Six tools, each a thin binding over `src.mcp.queries`:

    list_companies      the entry point; what exists and how much evidence
    get_marks           one company's price series
    compare_managers    what different managers said on one period end
    get_propagation     how long a new price level took to spread
    get_fund_exposure   what a manager holds, at what share of net assets
    list_unresolved     what a human has not yet answered

--------------------------------------------------------------------------
What this server will not do
--------------------------------------------------------------------------
It is **read-only**. There is no tool that writes a mark, clears a gate, or
records a decision. That is not an oversight: Week 6 established that a
resolution decision needs a named human, and a tool a model can call is the
opposite of that. A model using this server can read every judgment already
made and can see exactly what is still open; it cannot make one.

It also publishes no number this project does not already publish. Every tool
reads the same tables, with the same blocked-mark exclusion, as
`docs/findings.md` -- so an MCP answer and the written report cannot disagree
(P6).

--------------------------------------------------------------------------
Dependency note
--------------------------------------------------------------------------
`plan.md` pins `fastmcp==2.2.0`. That release predates the 2.x tool-decorator
API this file uses and is not installable alongside the pinned `mcp` package
this environment resolved; 2.11.3 is used instead and pinned in
requirements.txt. Logged as a deviation in docs/worklog.md.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from fastmcp import FastMCP  # noqa: E402

from src.db.connect import connect  # noqa: E402
from src.mcp import queries as Q  # noqa: E402
from src.mcp.paging import CursorError, page  # noqa: E402

mcp = FastMCP(
    name="private-ai-valuations",
    instructions=(
        "Per-share marks for private AI companies, derived from SEC Form "
        "N-PORT filings by dividing a fund's reported position value by its "
        "share count.\n\n"
        "Start with list_companies. Every response is summary-first: read the "
        "summary before the rows, because it describes the whole result set "
        "and the rows are one bounded page of it.\n\n"
        "This dataset does NOT contain company valuations. N-PORT gives a "
        "fund's share count, never the company's shares outstanding, so no "
        "company-level value is derivable from anything here. It is also not "
        "timely: filings lag their period end by roughly 55-60 days and the "
        "bulk sets lag those again."
    ),
)


def _respond(name: str, rows, summary, *, args: dict, cursor, limit) -> str:
    try:
        envelope = page(rows, scope={"tool": name, "args": args},
                        cursor=cursor, limit=limit, summary=summary)
    except CursorError as exc:
        envelope = {"error": str(exc), "tool": name}
    return json.dumps(envelope, indent=2, default=str)


def _call(name: str, fn, args: dict, cursor=None, limit=None) -> str:
    """One tool invocation: open, query, bound, close.

    A connection per call rather than one held open for the server's life.
    Claude Desktop keeps a server process alive for the whole session, and a
    Postgres connection idle for hours behind a laptop's sleep is a connection
    that fails on the next query rather than at startup, where the failure
    would be legible.
    """
    conn = connect()
    try:
        rows, summary = fn(conn, **args)
    except Exception as exc:                       # noqa: BLE001
        return json.dumps({"tool": name, "error": f"{type(exc).__name__}: {exc}"},
                          indent=2)
    finally:
        conn.close()
    return _respond(name, rows, summary, args=args, cursor=cursor, limit=limit)


@mcp.tool
def list_companies() -> str:
    """List every company in the universe with the size of its evidence.

    Call this first. Returns canonical names (which every other tool expects
    verbatim), coverage status, mark counts, manager counts and the period
    range. Small enough to return whole.
    """
    return _call("list_companies", Q.list_companies, {})


@mcp.tool
def get_marks(company: str, share_class: str | None = None,
              since: str | None = None, cursor: str | None = None,
              limit: int | None = None) -> str:
    """Price-per-share series for one company, newest period first.

    Args:
        company: canonical name exactly as list_companies returns it.
        share_class: optional normalized class, e.g. 'PFD:SERIES_F'.
        since: optional ISO date; only period ends on or after it.
        cursor: next_cursor from a previous call to this same tool.
        limit: rows per page, 1-200, default 50.

    The summary carries the period range, the latest-period price spread and
    the count of blocked marks excluded. Read it before paging.
    """
    return _call("get_marks", Q.get_marks,
                 {"company": company, "share_class": share_class, "since": since},
                 cursor=cursor, limit=limit)


@mcp.tool
def compare_managers(company: str, window: str | None = None,
                     min_holders: int = 2, cursor: str | None = None,
                     limit: int | None = None) -> str:
    """Compare what different managers priced one company at on one date.

    Args:
        company: canonical name.
        window: a period end as ISO date. Omitted, the latest period end on
            which at least min_holders managers both priced the company.
        min_holders: managers required for a comparison, default 2.

    The summary reports the spread and how many distinct price levels the
    marks fall into. More than one level often means a new round that some
    managers have reflected and others have not, rather than disagreement.
    """
    return _call("compare_managers", Q.compare_managers,
                 {"company": company, "window": window,
                  "min_holders": min_holders}, cursor=cursor, limit=limit)


@mcp.tool
def get_propagation(company: str | None = None, event: str | None = None,
                    min_holders: int = 3, cursor: str | None = None,
                    limit: int | None = None) -> str:
    """How long a new price level took to reach the managers who adopted it.

    Args:
        company: optional canonical name; omitted, every company.
        event: optional price level or first-adoption date to filter to.
        min_holders: managers that must adopt a level for it to count, 3.

    Measures days from the first manager reporting a price level to half of
    them doing so. Bounded below by the fiscal-quarter stagger, which the
    summary's caveat states: this is observability, not diligence.
    """
    return _call("get_propagation", Q.get_propagation,
                 {"company": company, "event": event,
                  "min_holders": min_holders}, cursor=cursor, limit=limit)


@mcp.tool
def get_fund_exposure(fund: str | None = None, cursor: str | None = None,
                      limit: int | None = None) -> str:
    """What a manager holds and what share of its funds' net assets it is.

    Args:
        fund: manager family, matched case-insensitively as a substring, so
            'baron' finds 'Baron Capital'. Omitted, every manager.

    The percentage is the filer's own figure from N-PORT. Each row is that
    manager's latest reported period end, which differs between managers.
    """
    return _call("get_fund_exposure", Q.get_fund_exposure, {"fund": fund},
                 cursor=cursor, limit=limit)


@mcp.tool
def list_unresolved(cursor: str | None = None, limit: int | None = None) -> str:
    """List every question a named human has not yet answered.

    Three kinds: ambiguities a reviewer looked at and could not settle,
    suspected splits awaiting adjudication, and Form D issuer identities not
    yet affirmed. An empty list is a real answer and the summary says so.
    """
    return _call("list_unresolved", Q.list_unresolved, {},
                 cursor=cursor, limit=limit)


TOOLS = ("list_companies", "get_marks", "compare_managers", "get_propagation",
         "get_fund_exposure", "list_unresolved")


def selftest() -> int:
    """Call every tool once against the live database and report sizes.

    Exists because the failure this server actually has is not a protocol
    error -- it is a tool that works and answers with 300,000 tokens. The
    character count per response is the thing worth printing.
    """
    checks = [
        ("list_companies", lambda: list_companies.fn()),
        ("get_marks", lambda: get_marks.fn("Databricks, Inc.")),
        ("compare_managers", lambda: compare_managers.fn("Anthropic PBC")),
        ("get_propagation", lambda: get_propagation.fn("Databricks, Inc.")),
        ("get_fund_exposure", lambda: get_fund_exposure.fn("Baron")),
        ("list_unresolved", lambda: list_unresolved.fn()),
    ]
    failures = 0
    print(f"{'tool':20} {'chars':>7} {'rows':>5} {'total':>6}  status")
    for name, call in checks:
        try:
            body = call()
            payload = json.loads(body)
        except Exception as exc:                   # noqa: BLE001
            print(f"{name:20} {'-':>7} {'-':>5} {'-':>6}  FAILED {exc}")
            failures += 1
            continue
        if "error" in payload:
            print(f"{name:20} {len(body):7} {'-':>5} {'-':>6}  ERROR "
                  f"{payload['error']}")
            failures += 1
            continue
        page_info = payload.get("page", {})
        print(f"{name:20} {len(body):7} {page_info.get('returned', 0):5} "
              f"{page_info.get('total', 0):6}  ok")
    print(f"\n{len(checks) - failures} of {len(checks)} tools answered.")
    return 1 if failures else 0


def main() -> None:
    if "--selftest" in sys.argv:
        raise SystemExit(selftest())
    mcp.run()


if __name__ == "__main__":
    main()
