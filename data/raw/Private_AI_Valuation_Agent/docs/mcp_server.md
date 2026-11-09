# MCP server — setup and contract

*Week 10, with [`signal_and_commentary.md`](signal_and_commentary.md) — the two
halves of making the panel consumable from outside this repository.*

A read-only FastMCP server over stdio, exposing the resolved marks panel so it
is queryable from Claude Desktop or Claude Code, and reusable by other Mycroft
agents without importing this project's code.

```
python -m src.mcp.server             # stdio — what a client launches
python -m src.mcp.server --selftest  # call every tool once, print response sizes
```

## The six tools

| Tool | Answers | Paged |
|---|---|---|
| `list_companies` | what exists, how much evidence, coverage status | no — 11 rows |
| `get_marks(company, share_class?, since?)` | one company's price-per-share series | yes |
| `compare_managers(company, window?, min_holders?)` | what managers priced it at on one period end | yes |
| `get_propagation(company?, event?, min_holders?)` | days for a new price level to reach half its holders | yes |
| `get_fund_exposure(fund?)` | what a manager holds, at what share of net assets | yes |
| `list_unresolved()` | every question a named human has not yet answered | yes |

`list_companies` is the entry point. Every other tool takes a canonical name
exactly as that tool returns it.

## Setup — Claude Desktop

The file is `claude_desktop_config.json`, and **where it lives depends on how
Claude Desktop was installed**:

| Install | Path |
|---|---|
| Windows, packaged / Microsoft Store | `%LOCALAPPDATA%\Packages\Claude_<id>\LocalCache\Roaming\Claude\claude_desktop_config.json` |
| Windows, standard installer | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |

A packaged install has **no** `%APPDATA%\Claude` directory at all, so looking
there and finding nothing is not evidence the file is missing. Verified on this
machine: the packaged path exists and `%APPDATA%\Claude` does not.

The file may already exist and already hold other top-level keys such as
`preferences` and `coworkUserFilesPath`. **`mcpServers` is a sibling of those,
not nested inside them.** Add it, keep what is there, and restart Claude
Desktop:

```json
{
  "mcpServers": {
    "private-ai-valuations": {
      "command": "E:\NEU\Jobs\Humanitarians_AI\Mycroft_prof\mycroft\data\raw\Private_AI_Valuation_Agent\.venv\Scripts\python.exe",
      "args": ["E:\NEU\Jobs\Humanitarians_AI\Mycroft_prof\mycroft\data\raw\Private_AI_Valuation_Agent\src\mcp\server.py"],
      "env": { "PYTHONIOENCODING": "utf-8" }
    }
  }
}
```

Three things that will otherwise cost an hour:

- **Launch the script by absolute path, not `python -m`.** Claude Desktop does
  **not** apply a `cwd` key before Python resolves `-m`, so
  `args: ["-m", "src.mcp.server"]` fails with
  `ModuleNotFoundError: No module named 'src'` even with `cwd` set — verified
  in the app. `server.py` puts the project root on `sys.path` itself and
  `src/db/connect.py` loads `ROOT/.env` by explicit path, so the script form
  works from any working directory. (If you prefer `-m`, set
  `"env": {"PYTHONPATH": "<project root>", "PYTHONIOENCODING": "utf-8"}` —
  that works too, and is tested.)
- **Use the venv interpreter by absolute path.** The desktop client inherits
  no shell, so `python` resolves to whatever is first on the system PATH,
  which is not this project's environment.
- **`PYTHONIOENCODING=utf-8` is not optional on Windows.** stdio is the MCP
  transport here, and a `cp1252` stdout turns the first em dash in a tool
  response into an encoding error that surfaces as a dead server.

## Setup — Claude Code

There is no `--cwd` flag on `claude mcp add`; environment variables go through
`-e`, and the command follows `--`.

**Pass `-s user`.** The default scope is `local`, which registers the server
*only for the directory you happened to run the command in* — adding it from
`C:\WINDOWS\System32` writes an entry under `projects["C:/WINDOWS/System32"]`
in `~/.claude.json` and the server is then invisible everywhere else,
including in this project. `user` scope makes it available from any directory,
which is what a read-only dataset server wants.

```bash
claude mcp add private-ai-valuations -s user -e PYTHONIOENCODING=utf-8 --   "E:/NEU/Jobs/Humanitarians_AI/Mycroft_prof/mycroft/data/raw/Private_AI_Valuation_Agent/.venv/Scripts/python.exe"   "E:/NEU/Jobs/Humanitarians_AI/Mycroft_prof/mycroft/data/raw/Private_AI_Valuation_Agent/src/mcp/server.py"
```

Check where it landed with `claude mcp list`, and remove a misplaced entry
with `claude mcp remove private-ai-valuations` run from the same directory
that created it.

## Verifying it works

```
$ python -m src.mcp.server --selftest
tool                   chars  rows  total  status
list_companies          3059    11     11  ok
get_marks              17976    50   2151  ok
compare_managers        9978    39     39  ok
get_propagation         6481    14     14  ok
get_fund_exposure       1185     2      2  ok
list_unresolved          335     0      0  ok

6 of 6 tools answered.
```

The `chars` column is the point of the selftest, not `status`. `get_marks` on
Databricks has **2,151 rows**; serialised whole, that is roughly 300,000
tokens — past most context windows and useless inside them, because a model
handed 2,151 rows will not read them. Bounded, the same call is 18 KB.

## Token bounding, and why it is the hard part

`plan.md`: *"Every response is token-bounded with a cursor — a tool returning
the whole marks table is useless to a model, so summary-first with drill-down
is the rule."*

Every response has the same three parts:

```json
{
  "summary": { "...": "describes the WHOLE result set" },
  "page":    { "offset": 0, "returned": 50, "total": 2151, "remaining": 2101 },
  "rows":    [ "...one bounded page..." ],
  "next_cursor": "eyJvIjo1MCwiZCI6..."
}
```

- **The summary describes the whole set, not the page.** A summary computed
  over page one would say "3 managers" about a company held by thirty.
- **Two bounds, not one.** A row limit (50, max 200) *and* a hard ceiling on
  the serialised response (48,000 characters ≈ 12,000 tokens). Row width is
  not uniform — a fund-exposure row is several times a marks row — so a row
  count alone is not a size bound. When the character ceiling bites, the
  response says `"truncated_for_size": true`.
- **Cursors are opaque, stateless and bound to their query.** They carry an
  offset and a digest of the arguments. No server state, so a client may page
  across a server restart; and a cursor from `get_marks("Databricks")` reused
  on `get_marks("Anthropic")` is rejected rather than silently returning
  Anthropic rows numbered from Databricks' offset.

## What this server will not do

**It is read-only.** No tool writes a mark, clears a gate, or records a
decision. Week 6 established that a resolution decision needs a named human
(P4), and a tool a model can call is the opposite of that. A model here can
read every judgment already made, and can see exactly what is still open via
`list_unresolved` — it cannot make one.

**It publishes no number this project does not already publish.** Every tool
reads the same tables with the same blocked-mark exclusion as
`docs/findings.md`, so an MCP answer and the written report cannot disagree
(P6). `get_propagation` and `get_fund_exposure` call
`src/signal/findings.py` and `src/signal/exposure.py` directly rather than
re-deriving anything.

**It does not serve a valuation.** N-PORT gives a fund's share count, never
the company's shares outstanding. The server's own instructions say so, so a
model reading them is told before it asks.

## Answers carry their caveats

A tool result is read by a model that has not read this repository, so the
qualification travels with the number rather than sitting in a document it
will never open. `compare_managers("Anthropic PBC")` returns:

```json
{
  "period_end": "2026-04-30",
  "managers": 8,
  "price_min": 259.1364,
  "price_max": 388.19,
  "spread": 0.498,
  "distinct_price_levels": 6,
  "note": "A spread is not automatically disagreement. Where distinct_price_levels is 2 or more, some managers may have reflected a new round and others not... Period ends are staggered across fund families, so same-date here means same filed period end, not same observation moment."
}
```

A 49.8% spread with six distinct price levels is not eight managers disagreeing
about value. Without the note, that is exactly what it reads as.

## What was tested, and what was not

**Confirmed against a real client.** `claude mcp list` reports this server
**✔ Connected** at user scope — an independent MCP runtime launched it as a
subprocess, completed the handshake and enumerated its tools. That is the
Week 10 clause *"queryable from Claude Desktop or Claude Code"* satisfied by
observation rather than by inference.

**Tested** (`tests/test_mcp.py`, 21 tests): the paging contract offline; a
live roundtrip where a real MCP client spawns this server and speaks the
protocol over stdio; and — added after three wrong setup instructions in a row
— the three *client-side* facts that no in-process test can see:

- the server must start with **no `cwd` and no `PYTHONPATH`**, run from a
  temporary directory, because Claude Desktop sets neither before Python
  resolves its entry point;
- the bare `-m src.mcp.server` form must still **fail** from elsewhere,
  pinned so the documented invocation and the working one cannot drift;
- the documented config block must launch the script by path, and the
  documented `claude mcp add` command must carry an explicit `--scope`.

**Still not confirmed:** the Claude Desktop application specifically. Claude
Code and Claude Desktop read different files — `~/.claude.json` and
`claude_desktop_config.json` — so one connecting does not prove the other is
configured. The server binary and the launch form are now verified; what
remains is per-application configuration.

**The lesson these three bugs share.** Every one of them — the `cwd` key, the
`--cwd` flag, the default `--scope` — is a property of *how a client launches
the server*, and none is observable from inside it. `--selftest` passed
throughout. An in-process stdio test that supplies `cwd` itself passed
throughout. A test only finds this class of bug if it withholds what the real
caller withholds.

## Dependency deviation

`plan.md` pins `fastmcp==2.2.0`. That release predates the 2.x tool-decorator
API this server uses and does not resolve against the `mcp` package in this
environment. **`fastmcp==2.11.3`** is used and pinned in `requirements.txt`.
