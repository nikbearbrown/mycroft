"""The MCP server: token bounding, cursors, and the stdio protocol itself.

Two layers, deliberately separate.

**Offline** — the paging contract. These are the tests that matter most,
because the failure this server actually has is not a protocol error. It is a
tool that works perfectly and answers with 300,000 tokens. A protocol test
would pass on exactly that server.

**Live** — a real client speaking the real protocol over stdio, skipped when
the database is unreachable. This is the same transport Claude Desktop uses,
so a server that passes it is one a desktop client can call. What it does not
prove is the desktop configuration itself; that is a human step and
`docs/mcp_server.md` is what carries it.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mcp import paging  # noqa: E402


# ------------------------------------------------------------------ bounding

def rows(n: int, width: int = 1) -> list[dict]:
    return [{"i": i, "pad": "x" * width} for i in range(n)]


def test_a_page_is_bounded_even_when_the_result_is_not():
    """2,151 marks must not become a 2,151-row answer."""
    out = paging.page(rows(2151), scope={"t": "get_marks"})
    assert out["page"]["returned"] == paging.DEFAULT_LIMIT
    assert out["page"]["total"] == 2151
    assert out["page"]["remaining"] == 2151 - paging.DEFAULT_LIMIT
    assert "next_cursor" in out


def test_the_summary_describes_the_whole_set_not_the_page():
    """A summary computed over page one would say "3 managers" about a
    company held by thirty. The summary is passed in whole and returned
    untouched."""
    summary = {"marks": 2151, "managers": 30}
    out = paging.page(rows(2151), scope={"t": "x"}, summary=summary)
    assert out["summary"] == summary
    assert out["page"]["returned"] < out["summary"]["marks"]


def test_a_small_result_carries_no_cursor():
    out = paging.page(rows(5), scope={"t": "x"})
    assert out["page"]["remaining"] == 0
    assert "next_cursor" not in out


def test_an_empty_result_is_a_valid_answer():
    out = paging.page([], scope={"t": "list_unresolved"})
    assert out["rows"] == []
    assert out["page"]["total"] == 0
    assert "next_cursor" not in out


def test_limit_is_clamped_in_both_directions():
    assert paging.clamp(None) == paging.DEFAULT_LIMIT
    assert paging.clamp(0) == 1
    assert paging.clamp(-5) == 1
    assert paging.clamp(10_000) == paging.MAX_LIMIT
    assert paging.clamp(25) == 25


def test_the_hard_character_ceiling_wins_over_the_row_limit():
    """Row width is not uniform, so a row count is not a size bound.

    A fund-exposure row with a long registrant name is several times a marks
    row; a tool returning 50 of either would be well-behaved for one and
    oversized for the other.
    """
    fat = rows(50, width=4000)          # ~200,000 chars at 50 rows
    out = paging.page(fat, scope={"t": "x"})
    assert len(json.dumps(out, default=str)) <= paging.MAX_RESPONSE_CHARS
    assert out["page"]["returned"] < 50
    assert out["page"]["truncated_for_size"] is True


def test_a_single_oversized_row_is_still_returned():
    """Better one row over budget than an empty answer with no explanation."""
    out = paging.page(rows(1, width=paging.MAX_RESPONSE_CHARS * 2),
                      scope={"t": "x"})
    assert out["page"]["returned"] == 1


# ------------------------------------------------------------------- cursors

def test_a_cursor_walks_the_whole_result_exactly_once():
    everything, scope, seen = rows(137), {"t": "get_marks"}, []
    cursor = None
    for _ in range(20):
        out = paging.page(everything, scope=scope, cursor=cursor, limit=25)
        seen.extend(r["i"] for r in out["rows"])
        cursor = out.get("next_cursor")
        if not cursor:
            break
    assert seen == list(range(137))


def test_a_cursor_from_another_query_is_rejected():
    """The bug this prevents is silent.

    A model reusing a Databricks cursor on Anthropic would otherwise get
    Anthropic rows numbered from Databricks' offset, with nothing in the
    response saying so.
    """
    out = paging.page(rows(200), scope={"t": "get_marks", "a": "Databricks"})
    stolen = out["next_cursor"]
    with pytest.raises(paging.CursorError, match="different arguments"):
        paging.page(rows(200), scope={"t": "get_marks", "a": "Anthropic"},
                    cursor=stolen)


def test_a_malformed_cursor_is_rejected_not_ignored():
    with pytest.raises(paging.CursorError, match="malformed"):
        paging.page(rows(10), scope={"t": "x"}, cursor="not-base64-at-all!!")


def test_a_cursor_survives_a_server_restart():
    """Cursors carry no server state, so a client may page across restarts."""
    scope = {"t": "get_marks", "a": "Databricks"}
    first = paging.page(rows(300), scope=scope, limit=50)
    offset = paging.decode_cursor(first["next_cursor"], scope)
    assert offset == 50


# -------------------------------------------------------------- the contract

def test_every_tool_the_plan_names_exists():
    from src.mcp import server

    assert set(server.TOOLS) == {
        "list_companies", "get_marks", "compare_managers",
        "get_propagation", "get_fund_exposure", "list_unresolved"}


def test_the_server_exposes_no_write_tool():
    """Read-only is a design decision, not an omission.

    A resolution decision needs a named human (P4). A tool a model can call to
    record one is the opposite of that.
    """
    from src.mcp import server

    source = Path(server.__file__).read_text(encoding="utf-8").lower()
    for verb in ("def affirm", "def adjudicate", "def record", "def set_",
                 "def update_", "def delete_", "def clear_"):
        assert verb not in source, f"{verb!r} suggests a write tool"


def test_queries_exclude_blocked_marks():
    """The MCP answer and docs/findings.md must not disagree (P6)."""
    from src.mcp import queries

    source = Path(queries.__file__).read_text(encoding="utf-8")
    priced = [block for block in source.split("def ")
              if "price_per_share" in block and "SELECT" in block]
    assert priced, "no price query found to check"
    for block in priced:
        assert "change_blocked" in block, \
            "a price query that does not exclude blocked marks"


# ------------------------------------------------------------ live, over stdio

def database_reachable() -> bool:
    try:
        from src.db.connect import connect

        connect().close()
        return True
    except Exception:                              # noqa: BLE001
        return False


live = pytest.mark.skipif(not database_reachable(),
                          reason="needs the Postgres instance")


async def _roundtrip():
    """Start the server as a subprocess and speak MCP to it over stdio."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=sys.executable, args=["-m", "src.mcp.server"],
        cwd=str(ROOT), env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listed = await session.list_tools()
            first = await session.call_tool("list_companies", {})
            marks = await session.call_tool(
                "get_marks", {"company": "Databricks, Inc.", "limit": 10})
            return listed, first, marks


@live
def test_a_real_client_can_list_and_call_over_stdio():
    listed, first, marks = asyncio.run(_roundtrip())

    from src.mcp import server

    assert {t.name for t in listed.tools} == set(server.TOOLS)

    payload = json.loads(first.content[0].text)
    assert payload["page"]["total"] >= 1
    assert "summary" in payload

    page = json.loads(marks.content[0].text)
    assert page["page"]["returned"] <= 10
    assert page["page"]["total"] > 10
    assert "next_cursor" in page


@live
def test_every_tool_carries_a_description_for_the_model():
    """A tool a model cannot tell apart from another is not callable."""
    listed, _, _ = asyncio.run(_roundtrip())
    for tool in listed.tools:
        assert tool.description and len(tool.description) > 60, tool.name


@live
def test_an_unknown_company_answers_rather_than_failing():
    """A model will guess a name. The answer has to say what to do next."""
    from src.mcp.server import get_marks

    payload = json.loads(get_marks.fn("Not A Real Company"))
    assert payload["page"]["total"] == 0
    assert "list_companies" in payload["summary"]["note"]


# ------------------------------------- launching the way a desktop client does

@live
def test_the_server_starts_with_no_cwd_and_no_pythonpath():
    """The gap the first version of this file had.

    `test_a_real_client_can_list_and_call_over_stdio` passes `cwd=ROOT` to
    `StdioServerParameters`, so it proves the server works *when something
    sets the working directory*. Claude Desktop does not: a config with
    `"cwd"` set and `args: ["-m", "src.mcp.server"]` failed in the app with
    `ModuleNotFoundError: No module named 'src'`, because `python -m` resolves
    the module against the real working directory before any `cwd` key is
    applied.

    So the supported invocation is the **script by absolute path**, which
    works from anywhere: `server.py` puts the project root on `sys.path`
    itself, and `src/db/connect.py` loads `ROOT / ".env"` explicitly rather
    than searching upward from the cwd.

    Run from a directory with no `.env` anywhere above it, with no PYTHONPATH.
    """
    import subprocess
    import tempfile

    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["PYTHONIOENCODING"] = "utf-8"

    with tempfile.TemporaryDirectory() as elsewhere:
        result = subprocess.run(
            [sys.executable, str(ROOT / "src" / "mcp" / "server.py"), "--selftest"],
            cwd=elsewhere, env=env, capture_output=True, text=True, timeout=300)

    assert "No module named" not in result.stdout + result.stderr
    assert "6 of 6 tools answered" in result.stdout, result.stdout[-2000:]


@live
def test_the_module_form_needs_help_and_the_docs_say_so():
    """`-m src.mcp.server` from elsewhere fails, and that is expected.

    Pinned as a test so the documented invocation and the working one cannot
    drift: if this ever starts passing, the docs can be simplified.
    """
    import subprocess
    import tempfile

    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    with tempfile.TemporaryDirectory() as elsewhere:
        bare = subprocess.run(
            [sys.executable, "-m", "src.mcp.server", "--selftest"],
            cwd=elsewhere, env=env, capture_output=True, text=True, timeout=120)
        assert "No module named 'src'" in bare.stdout + bare.stderr

        # ...and PYTHONPATH is the documented alternative that does work.
        with_path = subprocess.run(
            [sys.executable, "-m", "src.mcp.server", "--selftest"],
            cwd=elsewhere, env={**env, "PYTHONPATH": str(ROOT),
                                "PYTHONIOENCODING": "utf-8"},
            capture_output=True, text=True, timeout=300)
        assert "6 of 6 tools answered" in with_path.stdout


def test_the_documented_invocation_is_the_one_that_works():
    """The docs must not tell anyone to rely on a `cwd` key again."""
    for doc in (ROOT / "docs" / "mcp_server.md", ROOT / "README.md"):
        text = doc.read_text(encoding="utf-8")
        if "mcpServers" not in text:
            continue
        # Only the fenced JSON blocks that declare mcpServers. A character
        # window bled into the surrounding prose, which quotes the broken
        # `-m` form in order to warn against it -- so the test failed on the
        # documentation of the very fix it was checking for.
        import re

        blocks = [b for b in re.findall(r"```json\n(.*?)```", text, re.S)
                  if "mcpServers" in b]
        assert blocks, f"{doc.name}: no mcpServers JSON block found"
        for block in blocks:
            assert "server.py" in block, \
                f"{doc.name}: the config block should launch the script by path"
            assert '"-m"' not in block, \
                f"{doc.name}: -m needs a cwd that Claude Desktop does not apply"


def test_the_claude_code_command_sets_an_explicit_scope():
    """`claude mcp add` defaults to --scope local, which means "this directory".

    Run from anywhere but the project, that registers the server under a
    project key nobody will ever open again -- which is what happened:
    `projects["C:/WINDOWS/System32"]`. The documented command passes
    `-s user` so the server is reachable from any directory.
    """
    text = (ROOT / "docs" / "mcp_server.md").read_text(encoding="utf-8")
    assert "claude mcp add" in text
    command = text[text.index("claude mcp add"):][:400]
    assert "-s user" in command or "--scope user" in command,         "the documented command must set an explicit scope"
